# Copyright 2022 DeepMind Technologies Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Tests for extraction."""

import base64
import dataclasses
import gzip
from typing import BinaryIO, Iterable

from absl.testing import absltest
import extraction
from fs import memoryfs


@dataclasses.dataclass(frozen=True)
class _WMTDocInput:
  date: str
  sentence_split: str
  unsplit: str


@dataclasses.dataclass(frozen=True)
class _ArchiveFileInput:
  docs: list[_WMTDocInput]
  file_name: str


class ExtractionTest(absltest.TestCase):

  def setUp(self):
    super(ExtractionTest, self).setUp()

    self.mfs = memoryfs.MemoryFS()
    self.addCleanup(self.mfs.close)

  def test_get_wmt_docs_from_archive_file_paths(self):
    deduplicated_wmt_sorting_keys = [
        ('20190101000000000000\x00\x01'
         '1d377af8d421d226f274f12d31d4'
         'cc15e7c6f85e2e1eb2530e19b123d019d776\x00\x01'),
        ('20190102000000000000\x00\x01'
         'e1587db7b0a1fd73546c5b475626'
         '2c39f3309f8b8cc2b63a5034a80928eb533a\x00\x01'),
        ('20200103000000000000\x00\x01'
         'f86e132442e069c17be5b53fa9f2'
         '890b54007a4f12332e717e29f35d3b96accc\x00\x01'),
    ]
    deduplicated_wmt_sorting_keys_file_name = 'wmt_ids.gz'
    with self.mfs.openbin(deduplicated_wmt_sorting_keys_file_name, 'wb') as f:
      _write_doc_lines_to_archive(
          [k.encode() for k in deduplicated_wmt_sorting_keys], f)

    archive_file_inputs = [
        _ArchiveFileInput(
            docs=[
                _WMTDocInput('20190101', 'sentence_split_1', 'unsplit_1'),
                _WMTDocInput('20190102', 'sentence_split_2', 'unsplit_2'),
            ],
            file_name='news-docs.2019.en.filtered.gz',
        ),
        _ArchiveFileInput(
            docs=[
                _WMTDocInput('20200103', 'sentence_split_3', 'unsplit_3'),
                _WMTDocInput('20200103', 'duplicate', 'duplicate'),
            ],
            file_name='news-docs.2020.en.filtered.gz',
        ),
    ]
    _write_test_inputs(archive_file_inputs, self.mfs)

    wmt_docs = []
    for archive_file_input in archive_file_inputs:
      with self.mfs.openbin(deduplicated_wmt_sorting_keys_file_name,
                            'rb') as keys_file:
        with self.mfs.openbin(archive_file_input.file_name,
                              'rb') as archive_file:
          wmt_docs_for_archive = extraction.get_deduplicated_wmt_docs(
              wmt_archive_files=[archive_file],
              deduplicated_sorting_keys_file=keys_file,
          )
          wmt_docs.extend(wmt_docs_for_archive)

    wmt_docs.sort(key=lambda x: x.sorting_key)
    self.assertEqual([
        extraction.WMTDoc(
            sorting_key=deduplicated_wmt_sorting_keys[0],
            publication_ts=1546300800,
            text=b'sentence_split_1',
        ),
        extraction.WMTDoc(
            sorting_key=deduplicated_wmt_sorting_keys[1],
            publication_ts=1546387200,
            text=b'sentence_split_2',
        ),
        extraction.WMTDoc(
            sorting_key=deduplicated_wmt_sorting_keys[2],
            publication_ts=1578009600,
            text=b'sentence_split_3',
        )
    ], wmt_docs)

  def test_get_wmt_passages_from_docs(self):
    self.assertEqual([
        extraction.WMTPassage(id='doc_0_0', text=b'1. 2. 3. 4. 5. 6.'),
        extraction.WMTPassage(id='doc_0_1', text=b'7.'),
        extraction.WMTPassage(id='doc_1_0', text=b'1. 2. 3. 4. 5.'),
        extraction.WMTPassage(id='doc_2_0', text=b'1. 2. 3. 4. 5.'),
        extraction.WMTPassage(id='doc_3_0', text=b'1. 2. 3. 4. 5.'),
        extraction.WMTPassage(id='doc_4_0', text=b'1. 2. 3. 4. 5? 6. 7.'),
    ],
                     list(
                         extraction.get_wmt_passages_from_docs(
                             [
                                 extraction.WMTDoc(
                                     sorting_key='doc_0',
                                     publication_ts=0,
                                     text=b'1. 2. 3. 4. 5. 6. 7.'),
                                 extraction.WMTDoc(
                                     sorting_key='doc_1',
                                     publication_ts=0,
                                     text=b'1. 2. 3. 4. 5.'),
                                 extraction.WMTDoc(
                                     sorting_key='doc_2',
                                     publication_ts=0,
                                     text=b'1. 2. 3. 4.\n5.'),
                                 extraction.WMTDoc(
                                     sorting_key='doc_3',
                                     publication_ts=0,
                                     text=b'1. 2. 3. 4.\n 5.'),
                                 extraction.WMTDoc(
                                     sorting_key='doc_4',
                                     publication_ts=0,
                                     text=b'1. 2. 3. 4. 5? 6. 7.'),
                             ],
                             prepend_date=False)))

    self.assertEqual([
        extraction.WMTPassage(
            id='doc_0_0',
            text=b'Thursday, January 1, 1970. 1. 2. 3. 4. 5. 6.',
        ),
        extraction.WMTPassage(
            id='doc_0_1',
            text=b'Thursday, January 1, 1970. 7.',
        ),
    ],
                     list(
                         extraction.get_wmt_passages_from_docs([
                             extraction.WMTDoc(
                                 sorting_key='doc_0',
                                 publication_ts=0,
                                 text=b'1. 2. 3. 4. 5. 6. 7.')
                         ])))


def _write_test_inputs(archive_file_inputs: Iterable[_ArchiveFileInput],
                       memory_fs: memoryfs.MemoryFS):
  for archive in archive_file_inputs:
    doc_lines = [_get_doc_line(doc) for doc in archive.docs]
    with memory_fs.openbin(archive.file_name, 'wb') as f:
      _write_doc_lines_to_archive(doc_lines, f)


def _get_doc_line(wmt_doc: _WMTDocInput) -> bytes:
  return b'\t'.join([
      wmt_doc.date.encode(),
      base64.b64encode(wmt_doc.sentence_split.encode()),
      base64.b64encode(wmt_doc.unsplit.encode()),
  ])


def _write_doc_lines_to_archive(doc_lines: Iterable[bytes],
                                file_object: BinaryIO):
  with gzip.open(file_object, 'wb') as gfb:
    gfb.write(b'\n'.join(doc_lines))


if __name__ == '__main__':
  absltest.main()
