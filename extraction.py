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

"""WMT docs extraction.

The exported functions are:

`get_deduplicated_wmt_docs`
  1) takes the `gz` document-split versions of the WMT News Crawl from
     'https://data.statmt.org/news-crawl/README',
  2) extracts the documents,
  3) filters out duplicates,
  4) and then yields the lines parsed into `WMTDoc` objects.

`get_wmt_passages_from_docs`
  1) takes the `WMTDoc`s from the previous output
  2) splits the articles into sentences
  3) and yields them as `WMTPassage` chunks.
"""

import base64
import dataclasses
import datetime
import gzip
import hashlib
from typing import BinaryIO, Iterable, Iterator, Union

import pytz

_EXTRACTION_FIELD_SEPARATOR = b'\t'
_EXTRACTION_DATE_FORMAT = '%Y%m%d'

_SORTING_KEY_DATE_FORMAT = '%Y%m%d%H%M%S%f'
_SORTING_KEY_FIELD_SEPARATOR = '\x00\x01'

_PASSAGE_ID = '{sorting_key}_{passage_idx}'
_PASSAGE_SENTENCE_SEPARATOR = b'. '
_PASSAGE_NUM_SENTENCES = 6
_PASSAGE_DATE_PREFIX_FORMAT = '%A, %B %-d, %Y'


@dataclasses.dataclass(frozen=True)
class WMTDoc:
  """The input extracted from the WMT archive files.

  Attributes:
    sorting_key: The assigned sorting key to the document.
    publication_ts: Publication date of the document as UTC timestamp seconds.
    text: The processed document text / article.
  """
  sorting_key: str
  publication_ts: int
  text: bytes


@dataclasses.dataclass(frozen=True)
class WMTPassage:
  """A passage from a sequence of `WMTDoc` article sentence chunks.

  Attributes:
    id: Assigned ID consisting of the original `WMTDoc` `sorting_key` and an
      index for the passage position in the original article.
    text: A chunk from a sequence of sentences extracted from the `WMTDoc`
      article.
  """
  id: str
  text: bytes


def get_deduplicated_wmt_docs(
    wmt_archive_files: Iterable[Union[str, BinaryIO]],
    deduplicated_sorting_keys_file: Union[str, BinaryIO]) -> Iterator[WMTDoc]:
  """Reads and yields deduplicated `WMTDoc`s from the WMT News Crawl.

  Args:
    wmt_archive_files: List of file paths or file path objects of the WMT News
      Crawl dataset `.gz` files.
    deduplicated_sorting_keys_file: File path to the gzipped newline delimited
      txt file of deduplicated WMT sorting key IDs.

  Yields:
    Extracted and filtered `WMTDoc` objects.
  """
  with gzip.open(deduplicated_sorting_keys_file) as f:
    sorting_keys = set(line.strip().decode() for line in f)

  for file_path_or_object in wmt_archive_files:
    with gzip.open(file_path_or_object) as f:
      for line in f:
        doc = _extract_doc(line)
        if doc.sorting_key in sorting_keys:
          yield doc


def get_wmt_passages_from_docs(
    wmt_docs: Iterable[WMTDoc],
    prepend_date: bool = True) -> Iterator[WMTPassage]:
  """Yields `WMTPassage`s based on sentence split and chunked `WMTDoc` articles.

  Args:
    wmt_docs: The articles to be sentence split and chunked into passages.
    prepend_date: If True, will prepend the article publication date to each
      extracted passage.

  Yields:
    WMT passages as ID and text which can be used for the retrieval search
    space.
  """
  for doc in wmt_docs:
    article = doc.text + b' '
    article = article.replace(b'.\n', _PASSAGE_SENTENCE_SEPARATOR)

    sentences = [s.strip() for s in article.split(_PASSAGE_SENTENCE_SEPARATOR)]
    sentences = [s for s in sentences if s]

    for p_i, s_i in enumerate(range(0, len(sentences), _PASSAGE_NUM_SENTENCES)):
      chunk = sentences[s_i:s_i + _PASSAGE_NUM_SENTENCES]
      passage = _PASSAGE_SENTENCE_SEPARATOR.join(chunk) + b'.'

      if prepend_date:
        prefix = datetime.datetime.fromtimestamp(
            doc.publication_ts).strftime(_PASSAGE_DATE_PREFIX_FORMAT).encode()
        passage = _PASSAGE_SENTENCE_SEPARATOR.join([prefix, passage])

      passage_id = _PASSAGE_ID.format(
          sorting_key=doc.sorting_key, passage_idx=p_i)
      yield WMTPassage(id=passage_id, text=passage)


def _extract_doc(doc_line: bytes) -> WMTDoc:
  """Processes a doc line (= one line per doc) from the WMT dataset file."""
  try:
    publication_date, sentence_split_doc_line, unsplit_doc_line = (
        doc_line.strip().split(_EXTRACTION_FIELD_SEPARATOR))
  except ValueError as e:
    raise ValueError('Failed to parse doc line') from e

  # pylint: disable=g-tzinfo-replace
  publication_dt = datetime.datetime.strptime(
      publication_date.decode(),
      _EXTRACTION_DATE_FORMAT).replace(tzinfo=pytz.UTC)
  line_hash = hashlib.sha256(unsplit_doc_line).hexdigest()
  sorting_key = _SORTING_KEY_FIELD_SEPARATOR.join([
      publication_dt.strftime(_SORTING_KEY_DATE_FORMAT),
      line_hash,
      '',
  ])

  return WMTDoc(
      sorting_key=sorting_key,
      publication_ts=int(publication_dt.timestamp()),
      text=base64.b64decode(sentence_split_doc_line),
  )
