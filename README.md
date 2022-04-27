# StreamingQA

This repository contains the question-answering StreamingQA datasets, a list of
deduplicated WMT document IDs, and a script to process and filter the WMT
documents to be used in conjunction with the paper: [StreamingQA: A Benchmark
for Adaptation to New Knowledge over Time in Question Answering Models (Liška,
Kočiský, Gribovskaya, Terzi et al., 2021)](https://arxiv.org/abs/?.?).

If you use this dataset in your research please cite

```
@article{streamingqa2022,
  title={StreamingQA: A Benchmark
    for Adaptation
    to New Knowledge over Time
    in Question Answering Models},
  author={Adam Li{\v{s}}ka and
    Tom{\'a}{\v{s}} Ko{\v{c}}isk{\'y} and
    Elena Gribovskaya and
    Tayfun Terzi and
    Eren Sezener and
    Devang Agrawal and
    Cyprien de Masson d'Autume and
    Tim Scholtes and
    Manzil Zaheer and
    Susannah Young and
    Ellen Gilsenan-McMahon
    Sophia Austin and
    Phil Blunsom and
    Angeliki Lazaridou},
  journal={arXiv preprint arXiv:?.?},
  year={2022}
}
```

## Data

The paper specific data can be downloaded using the links provided below. These
are files stored in Google Cloud Storage in gzipped form.

### WMT

We downloaded document-split versions of the English
[WMT News Crawl dataset](http://data.statmt.org/news-crawl/README). As the
dataset does not provide document IDs, we used SHA256 hashes of the Base64
encoded unsplit texts of articles as part of "sorting key IDs" (see below).

#### Deduplicated subset

For the paper, we use a deduplicated subset of the WMT data. To reproduce the
subset, please find a list of WMT sorting key IDs, which in conjunction with the
extraction script can be used to filter out duplicate documents. The list is
stored as newline delimited sorting keys.

### StreamingQA

The StreamingQA questions and answers (including metadata) are stored in JSONL
files. We provide subsets for train, valid, and eval separately.

Each QA entry has attributes:

Field                        | Type        | Description
:--------------------------- | ----------: | :----------
`qa_id`                      | `str`       | Question identifier: `"eval-X"`, `"valid-X"`, and `"train-X"`, where `X` is an integer index starting from zero.
`question`                   | `str`       | The question text.
`answers`                    | `List[str]` | A list of answers, where there `len=1` for questions in the `'train'` and `'valid'` subset, and `len=3` for questions in the `'eval'` subset.
`answers_additional`         | `List[str]` | Additional answers only available for the `'eval'` subset (empty string for subset `'train'` and `'valid'`). This is the 4th additional reference collected to compute the human benchmark. This is not used for evaluation but may serve useful for other purposes.
`question_ts`                | `int`       | Timestamp (UTC seconds) of the date when the question was asked.
`evidence_ts`                | `int`       | Timestamp (UTC seconds) of the date when the corresponding WMT news article was published.
`evidence_id`                | `str`       | The WMT sorting key ID of the document text that was used as evidence for the question.
`recent_or_past`             | `str`       | To which subset the question belongs ( `"recent"` vs `"past"`).
`written_or_generated`       | `str`       | Whether the question is based on human annotations (`"written"`) or was `"generated"`.
`toxicity_identity_attack`   | `float`     | Toxicity score of Perspective API classifier "IDENTITY_ATTACK".
`toxicity_insult`            | `float`     | Toxicity score of Perspective API classifier "INSULT".
`toxicity_profanity`         | `float`     | Toxicity score of Perspective API classifier "PROFANITY".
`toxicity_severe_toxicity`   | `float`     | Toxicity score of Perspective API classifier "SEVERE_TOXICITY".
`toxicity_sexually_explicit` | `float`     | Toxicity score of Perspective API classifier "SEXUALLY_EXPLICIT".
`toxicity_threat`            | `float`     | Toxicity score of Perspective API classifier "THREAT".

For detailed definitions of the toxicity classifiers please refer to
[Perspective API](https://developers.perspectiveapi.com/s/about-the-api-attributes-and-languages)
website.

### Download

Name                             | File                         | Size (bytes)  | Entries (lines) | MD5                                | Download
:------------------------------- | :--------------------------- | ------------: | --------------: | :--------------------------------- | :-------
Deduplicated WMT sorting key IDs | `wmt_sorting_key_ids.txt.gz` | `439,101,648` | `11,393,471`    | `3356d7e38e43b7bf4338e2003ab92f36` | [Link](https://storage.googleapis.com/dm-streamingqa/wmt_sorting_key_ids.txt.gz)
StreamingQA train subset         | `streaminqa_train.jsonl.gz`  | `17,466,691`  | `99,402`        | `32b3bc32b39f81bc2f0e9ab6fb4201b3` | [Link](https://storage.googleapis.com/dm-streamingqa/streaminqa_train.jsonl.gz)
StreamingQA valid subset         | `streaminqa_valid.jsonl.gz`  | `1,749,221`   | `9,939`         | `3570fbba6e2630e0c2bff03b150f9230` | [Link](https://storage.googleapis.com/dm-streamingqa/streaminqa_valid.jsonl.gz)
StreamingQA eval subset          | `streaminqa_eval.jsonl.gz`   | `7,455,358`   | `36,378`        | `a54db9a7e6fb1adfea7d4022f5fc49bd` | [Link](https://storage.googleapis.com/dm-streamingqa/streaminqa_eval.jsonl.gz)

### Metadata

The following table is necessary for this dataset to be indexed by search
engines such as <a href="https://g.co/datasetsearch">Google Dataset Search</a>.
<div itemscope itemtype="http://schema.org/Dataset">
<table>
  <tr>
    <th>property</th>
    <th>value</th>
  </tr>
  <tr>
    <td>name</td>
    <td><code itemprop="name">StreamingQA</code></td>
  </tr>
  <tr>
    <td>url</td>
    <td><code itemprop="url">https://github.com/deepmind/streamingqa</code></td>
  </tr>
  <tr>
    <td>sameAs</td>
    <td><code itemprop="sameAs">https://github.com/deepmind/streamingqa</code></td>
  </tr>
  <tr>
    <td>description</td>
    <td><code itemprop="description">
      Data accompanying
      [StreamingQA: A Benchmark
for Adaptation to New Knowledge over Time in Question Answering Models (Liška,
Kočiský, Gribovskaya, Terzi et al., 2021)](https://arxiv.org/abs/?.?).
      </code></td>
  </tr>
  <tr>
    <td>provider</td>
    <td>
      <div itemscope itemtype="http://schema.org/Organization" itemprop="provider">
        <table>
          <tr>
            <th>property</th>
            <th>value</th>
          </tr>
          <tr>
            <td>name</td>
            <td><code itemprop="name">DeepMind</code></td>
          </tr>
          <tr>
            <td>sameAs</td>
            <td><code itemprop="sameAs">https://en.wikipedia.org/wiki/DeepMind</code></td>
          </tr>
        </table>
      </div>
    </td>
  </tr>
  <tr>
    <td>citation</td>
    <td><code itemprop="citation">https://identifiers.org/arxiv:?.?</code></td>
  </tr>
</table>
</div>

### Disclaimer

This dataset is based on news articles from various sources and contains a small
number of questions or answers, both human written and automatically generated,
that are toxic and may be triggering or worrisome for researchers, or cause
models to generate such content. We aimed to create a balanced process that
identifies most of the toxic content while decreasing the risk of removing false
positives. We estimate that 0.5% items in the dataset are toxic after our
toxicity filtering. Secondly, questions and answers reflect information from the
news articles, and in particular, may not always be factually correct.
Furthermore, this dataset is intended to evaluate adaptation of models to new
information in news over time, and therefore, it may not be applicable to
settings where the assumptions we made don't apply. We provide further toxicity
discussion and details of our filtering in the paper.

## Code

### Installation

For installation please run `./run.sh` to setup a Python environment and install
the necessary Python packages (listed in `requirements.txt`). The script
completes with the output of the test.

### Example usage in Python

After installation, and in the activated Python virtual environment (here
`streamingqa_env`) you may start an interactive Python session and use the
following code (if you have downloaded files to the same directory as the code
from the links provided above):

#### WMT Docs

We provide a Python script `extraction.py` that extracts the downloaded WMT
data, pre-processes the text, assigns the sorting key IDs, and finally filters
out the duplicate documents. The main entry point `get_deduplicated_wmt_docs`
yields `WMTDoc` objects with attributes being the assigned sorting key ID
(`sorting_key`), the document publication date as UTC timestamp in seconds
(`publication_ts`), and the pre-processed document text (`text`).

```py
import extraction

_archive_file_names = [
  'news-docs.2007.en.filtered.gz',
  'news-docs.2008.en.filtered.gz',
  'news-docs.2009.en.filtered.gz',
  'news-docs.2010.en.filtered.gz',
  'news-docs.2011.en.filtered.gz',
  'news-docs.2012.en.filtered.gz',
  'news-docs.2013.en.filtered.gz',
  'news-docs.2014.en.filtered.gz',
  'news-docs.2015.en.filtered.gz',
  'news-docs.2016.en.filtered.gz',
  'news-docs.2017.en.filtered.gz',
  'news-docs.2018.en.filtered.gz',
  'news-docs.2019.en.filtered.gz',
  'news-docs.2020.en.filtered.gz',
  'news-docs.2021.en.filtered.gz',
]

wmt_docs = extraction.get_deduplicated_wmt_docs(
  wmt_archive_file_paths_or_objects=_archive_file_names,
  deduplicated_sorting_keys_file_path_or_object='wmt_sorting_key_ids.txt.gz',
)
```

#### WMT Passages

Furthermore, we also provide a function to reproduce our splits of articles into
sentence chunks. These passages can be used as the search space for the
retrieval architecture as is discussed in more detail in the paper mentioned
above.

```py
wmt_passages = extraction.get_wmt_passages_from_docs(
  wmt_docs=wmt_docs,
  preprend_date=True,
)
```

#### StreamingQA

```py
import gzip
import json

_file_name_by_streamingqa_subset = {
  'train': 'streaminqa_train.jsonl.gz',
  'valid': 'streaminqa_valid.jsonl.gz',
  'eval': 'streaminqa_eval.jsonl.gz',
}

streamingqa = {}
for subset_name, file_name in _file_name_by_streamingqa_subset.items():
  with open('streamingqa_train.jsonl.gz'), 'rb') as input_file:
    with gzip.open(input_file) as ungzipped_file:
      streamingqa[subset_name] = [
          json.loads(line.decode()) for line in ungzipped_file
      ]
```

## License and disclaimer

Copyright 2022 DeepMind Technologies Limited

All software is licensed under the Apache License, Version 2.0 (Apache 2.0);
you may not use this file except in compliance with the Apache 2.0 license.
You may obtain a copy of the Apache 2.0 license at:
https://www.apache.org/licenses/LICENSE-2.0

All other materials are licensed under the Creative Commons Attribution 4.0
International License (CC-BY). You may obtain a copy of the CC-BY license at:
https://creativecommons.org/licenses/by/4.0/legalcode

Unless required by applicable law or agreed to in writing, all software and
materials distributed here under the Apache 2.0 or CC-BY licenses are
distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the licenses for the specific language governing
permissions and limitations under those licenses.

This is not an official Google product.
