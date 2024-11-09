# Text History Extraction Tool (THEtool). A tool for Linguistic Modeling of Written Text Production

An open-source application implemented in Python for parsing raw keystroke logging data from a writing session, processing it to retrieve all relevant text versions produced during this session, and eventually generating text and sentence histories based on the collected information.

The input file processed by the tool is an idfx file in XML format.

The tool uses two main modes to capture text versions from idfx files:
* the Pause Capturing Mode (PCM), which relies on a preset pause duration in the text production to yield versions,
* and the Edit Capturing Mode (ECM), which uses a change production mode to determine versions. A  change  in  production  mode  is  defined  as switching between one of the modes (a) writing at the edge of the text, (b) deleting something, (c) inserting something.

## Tool Outputs

The main outputs of the tool are:
* text history in ECM in JSON format
* all text versions in ECM exported to TXT format
* visualisation of text history in ECM in SVG format
* text history in PCM in JSON format
* sentence history in JSON format
* sentence history visualisation in SVG format

In case filtering has been activated in the configuration:
* filtered text history in JSON format
* filtered text versions exported to TXT format
* filtered sentence history in JSON format
* visualisation of filtered text history in ECM in SVG format
* filtered sentence history visualisation in SVG format

## Processing Pipeline

The central building block of the tool is TPSF. It is a data type for storing the text version together with further details retrieved from the processed keystroke logging data.

Generating a TPSF comprises the following steps:
* First the input file is parsed and the keystroke logging data is processed to capture all details on the particular text version.
* This data is next stored in a TPSF data structure and subsequently used to retrieve information on the sentences constituting this version.
* Finally, the version is evaluated for its morphosyntactic relevance.

In each step, the TPSF is enriched with the newly collected details.

An accomplished collection of TPSFs results in a text history which constitutes the basis for another output: the sentence history. Based on the relevancy label of each TPSF, both the text and the sentence history can be filtered.

The following figure provides an overview of the processing steps.

![Processing Pipeline](docs/charts/Concept_Overview.png)

An example of a TPD exported to JSON format:

```
{
	"revision_id": 4,
	"previous_text_version": "An edit operation is an act of either removing or inserting a sequence. ",
	"preceding_pause": 0.54,
	"result_text": "An edit operation is an act of either removing or inserting a sequence without interruption. ",
	"edit": {
		"edit_start_position": 70,
		"transforming_sequence": {
			"label": "insertion",
			"text": " without interruption",
			"tags": [
				{"text": " ", "pos": "SPACE", "pos_details": "_SP", "dep": "", "lemma": " ", "oov": false, "is_punct": false, "is_space": true},
				"text": "without", "pos": "ADP", "pos_details": "IN", "dep": "ROOT", "lemma": "without", "oov": false, "is_punct": false, "is_space": false},
				"text": "interruption", "pos": "NOUN", "pos_details": "NN", "dep": "pobj", "lemma": "interruption", "oov": false, "is_punct": false, "is_space": false},
				]
	},
	"sentences": {
		"previous_sentence_list": [
			{
				"text": "An edit operation is an act of either removing or inserting a sequence. ",
				"start_index": 0,
				"end_index": 70,
				"revision_id": 3,
				"pos_in_text": 0
			}
		],
		"current_sentence_list": [
			{
				"text": "An edit operation is an act of either removing or inserting a sequence without interruption. ",
				"start_index": 0,
				"end_index": 91,
				"revision_id": 3,
				"pos_in_text": 0,
				"label": "modified"
			},
		"new_sentences": [],
		"edited_sentences": [
			{
				"previous_sentence": {
					"text": "An edit operation is an act of either removing or inserting a sequence. ",
					"start_index": 0,
					"end_index": 70,
					"revision_id": 3,
					"pos_in_text": 0
				},
				"current_sentence": {
					"text": "An edit operation is an act of either removing or inserting a sequence without interruption. ",
					"start_index": 0,
					"end_index": 91,
					"revision_id": 3,
					"pos_in_text": 0,
					"label": "modified"
				}
			}
		],
		"deleted_sentences": [],
		"unchanged_sentences": []
	},
	"morphosyntactic_relevance_evaluation": [
		"number_affected_tokens": 3,
		"affected_tokens": [
			{"prev_tok": ("sequence.", 62, 70), "cur_tok": ("sequence", 62, 69)},
			{"prev_tok": ("", null, null), "cur_tok": ("without", 71, 77)},
			{"prev_tok": ("", null, null), "cur_tok": ("interruption.", 79, 91)},
		]
		"is_any_tok_oov": false,
		"edit_distance": 21
	],
	"morphosyntactic_relevance": true
}

```

For supplementing the analysis with relevant linguistic annotations, we apply [spaCy](https://spacy.io), an open-source Python software library for advanced natural language processing.  spaCy offers a set of trained pipeline packages for multiple languages.  We used two of them: ```en_core_web_md``` for processing English texts and ```de_core_web_md``` for German data.

## Tool Configuration

Several parameters related to TPSF generation are configurable. These are:
* xml_paths: a list of paths to idfx files to be parsed
* output_path: path to the directory where the all output files should be stored
* pause_duration: the duration of the pause that should trigger TPSF generation in PCM mode, default = 2
* edit_distance: the maximum edit distance between two TPSFs which makes a TPSFs morphosyntactically irrelevant, default = 3
* filtering: if set to True, a filtered TPSF list will be generated next to an unfiltered one, default = True
* language: 'German' or 'English'

The configuration file ```config.py``` is stored in the tool root directory. You can define multiple configurations in the configuration file.

The configuration structure:

```
<YOUR CONFIGURATION NAME> = {
    'xml_paths': [],
    'output_path': '',
    'pause_duration': int,
    'edit_distance': int,
    'filtering': int,
    'language': ''
}
```

## Running the Tool

* To install all dependencies install [poetry](https://python-poetry.org/), run:

```
poetry install
```

* To run the tool, execute:

```
poetry run wta config.<YOUR CONFIGURATION NAME>
```

To run the tool for the provided **example data** (seven idfx files with short descriptive comments created by seven subjects after watching a two-minute video), execute the following command:

```
poetry run wta config.VIDEO
```

By default, the tool will create a directory ```wta``` in the user's home directory where it will store the output files. The output path can be changed by modifying the ```output_path```in the ```VIDEO``` configuration in ```config.py```.

## Relevant Definitions

**SENTENCE MORPHOSYNTACTIC RELEVANCE** A sentence is morphosyntactically relevant if:
* it does not contain any spelling errors
* it does not contain any tokens of the length 1
* the edit distance between the sentence and its previous version is larger than 3 (only relevant if the difference between the sentence versions contains one token; the edit distance is NOT taken into account, if the difference between versions contains multiple tokens.)


## Citation

If you use THEtool, please cite our paper [Extraction of transforming sequences and sentence histories from writing process data: a first step towards linguistic modeling of writing](https://doi.org/10.1007/s11145-021-10234-6) as follows:

```
@article{mahlow_extraction_2024,
	title = {Extraction of transforming sequences and sentence histories from writing process data: a first step towards linguistic modeling of writing},
	volume = {37},
	issn = {1573-0905},
	url = {https://doi.org/10.1007/s11145-021-10234-6},
	doi = {10.1007/s11145-021-10234-6},
	abstract = {Producing written texts is a non-linear process: in contrast to speech, writers are free to change already written text at any place at any point in time. Linguistic considerations are likely to play an important role, but so far, no linguistic models of the writing process exist. We present an approach for the analysis of writing processes with a focus on linguistic structures based on the novel concepts of transforming sequences, text history, and sentence history. The processing of raw keystroke logging data and the application of natural language processing tools allows for the extraction and filtering of product and process data to be stored in a hierarchical data structure. This structure is used to re-create and visualize the genesis and history for a text and its individual sentences. Focusing on sentences as primary building blocks of written language and full texts, we aim to complement established writing process analyses and, ultimately, to interpret writing timecourse data with respect to linguistic structures. To enable researchers to explore this view, we provide a fully functional implementation of our approach as an open-source software tool and visualizations of the results. We report on a small scale exploratory study in German where we used our tool. The results indicate both the feasibility of the approach and that writers actually revise on a linguistic level. The latter confirms the need for modeling written text production from the perspective of linguistic structures beyond the word level.},
	number = {2},
	journal = {Reading and Writing},
	author = {Mahlow, Cerstin and Ulasik, Malgorzata Anna and Tuggener, Don},
	month = feb,
	year = {2024},
	pages = {443--482},
}
```
