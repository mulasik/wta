# A tool for Linguistic Modeling of Written Text Production

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

![Processing Pipeline](https://github.com/mulasik/wta/blob/main/docs/charts/Concept_Overview.png)

An example of a TPSF exported to JSON format:

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
				{"text": " ", "pos": "SPACE", "pos_details": "_SP", "dep": "", "lemma": " ", "oov": false, "is_punct": false, "is_space": true},
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
	"relevance_evaluation": [
	    "edit_distance": 21,
		"number_tokens_in_transformin_seq": 4,
		"tpsf_contains_typos": false,
		
	], 
	"relevance": true
}

```

For supplementing the analysis with relevant linguistic annotations, we apply [spaCy](https://spacy.io), an open-source Python software library for advanced natural language processing.  spaCy offers a set of trained pipeline packages for multiple languages.  We used two of them: ```en_core_web_md``` for processing English texts and ```de_core_web_md``` for German data. 

## Tool Configuration

Several parameters related to TPSF generation and relevance definition are configurable.

TPSF generation parameters:
* xml_paths: a list of paths to idfx files to be parsed
* output_path: path to the directory where the all output files should be stored
* pause_duration: the duration of the pause that should trigger TPSF generation in PCM mode, default = 2
* language: 'German', 'English' or 'Greek'

TPSF relevance definition parameters:
* min_edit_distance: the minimum edit distance between two TPSFs required for classifying a TPSF as relevant, default = 3
* ts_min_tokens_number: the minimum number of tokens contained in a transforming sequence required for classifying a TPSF as relevant, default = 2
* spellchecking: if set to True, only the TPSFs which don't contain any spelling errors are classified as relevant, default = False
* punctuation: if set to True, a TPSF is always classified as relevant if the edit affects the punctuation in any way (removing or adding a punctuation mark), default = True

The configuration file ```config.py``` is stored in the tool root directory. You can define multiple configurations in the configuration file.

The configuration structure:

```
<YOUR CONFIGURATION NAME> = {
    'xml': list,
    'output': str,
    'pause_duration': int,
    "min_edit_distance": int,
    "ts_min_tokens_number": int,
    "spellchecking": bool,
    "punctuation": bool,
    "language": str,
}
```

## Running the Tool

* To install all dependencies, run: 

```
pip install -r requirements.txt
```

* To run the tool, execute:

```
python -m wta config.<YOUR CONFIGURATION NAME>
```

To run the tool for the provided **example data** (seven idfx files with short descriptive comments created by seven subjects after watching a two-minute video), execute the following command:

```
python -m wta config.VIDEO
```

By default, the tool will create a directory ```output_data``` in the tool directory where it will store the output files. The output path can be changed by modifying the ```output```in the ```VIDEO``` configuration in ```config.py```.


## Relevance

There are 4 relevance definition parameters:
* min_edit_distance: the minimum edit distance between two TPSFs required for classifying a TPSF as relevant, default = 3
* ts_min_tokens_number: the minimum number of tokens contained in a transforming sequence required for classifying a TPSF as relevant, default = 2
* spellchecking: if set to True, only the TPSFs which don't contain any spelling errors are classified as relevant, default = False
* punctuation: if set to True, a TPSF is always classified as relevant if the edit affects the punctuation in any way (removing or adding a punctuation mark), default = True

The parameters allow you to define what determines whether a text version is relevant or not. The relevance is defined on two levels:
* the relevance of the whole TPSF
* relevance of each sentence modified or added as a result of the edit

Based on the relevance, the tool outputs are filtered. There are 2 outputs which are subject to filtering:
* text history (filtered based on the TPSF relevance)
* sentence history (filtered based on the sentence relevance)

Examples:

Given the following configuration file:
```
VIDEO = {
    "xml": [
        os.path.join(VIDEO_DATA_DIR, f)
        for f in os.listdir(VIDEO_DATA_DIR)
        if os.path.isfile(os.path.join(VIDEO_DATA_DIR, f)) and f.endswith("idfx")
    ],
    "output": os.path.join("output_data", "video"),
    "pause_duration": 2,
    "min_edit_distance": 3,
    "ts_min_tokens_number": 2,
    "spellchecking": True,
    "punctuation": False,
    "language": "English",
}
```

the following TPSF versions will be classified as irrelevant:

* "The sky is blue." --> "The sky is blue"

The edit consists in removing the punctuation mark. As ```punctuation``` is set to False, this text version is classified as irrelevant.

* "The sky is blue" --> "The sky abov us is blue"

The edit consists in inserting the phrase "abov us". As ```spellchecking``` is set to True and the phrase contains a typo, this text version is classified as irrelevant.

* "The sky abov us is blue" --> "The sky above us is blue"

The edit consists in inserting "e". As ```min_edit_distance``` is set to 3 and the edit contains only 1 character and as ```ts_min_tokens_number``` is set to 2 and the edit contains only one token, this text version is classified as irrelevant)


