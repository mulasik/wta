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

The following figure provides an overview of the processing steps. The steps are described in more detail below.

![Processing Pipeline](https://github.com/mulasik/wta/blob/main/docs/charts/Concept_Overview.png)

For supplementing the analysis with relevant linguistic annotations, we apply spaCy, an open-source Python software library for advanced natural language processing.  spaCy offers a set of trained pipeline packages for multiple languages.  We used two of them: ```en_core_web_md``` for processing English texts and ```de_core_web_md``` for German data. 

#### Keystroke logging data processing

The tool iterates over the idfx file collecting keystroke data such as cursor position, key name, keystroke value, start and end time until an event occurs that triggers the TPSF creation. In PCM it is a pause of a certain length in the text production process.  The configuration allows to set a static threshold in milliseconds.  If the limit is exceeded, the current text version is captured and stored as a TPSF instance. In ECM, the trigger is either a detected edit operation or a change of cursor position without edits. An edit operation is either deleting or inserting a sequence at the beginning, in the middle, or at the end of the text without interruption. As long as the writer keeps deleting or inserting subsequent characters one after another without changing direction or moving the cursor to a different position (e.g., with cursor keys or a mouse click), the whole sequence is treated as a single edit operation. As soon as the edit operation is interrupted (i.e., a change in production mode is detected), the current text version is captured. 

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

The characters deleted or inserted during a single edit operation are aggregated and stored in a data structure representing the transforming sequence. The character sequence is split into tokens and each token is described with additional metadata---e.g., part-of-speech and dependency tags---, and out-of-vocabulary labels. The token information is also stored in the transforming sequence data structure.

#### Sentence processing
#### Text history generation
#### Sentence histories generation
#### Filtering according to morphosyntactic relevancy



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

* To install all dependencies, run: 

```
pip install -r requirements.txt
```

* To run the tool, execute:

```
python -m wta config.<YOUR CONFIGURATION NAME>
```

To run the tool for the provided example data (short descriptive comments created by seven subjects after watching a two-minute video), execute the following command:

```
python -m wta config.VIDEO
```

By default, the tool will create a directory ```wta``` in the user's home directory where it will store the output files. The output path can be changed by modifying the ```output_path```in the ```VIDEO``` configuration in ```config.py```.




