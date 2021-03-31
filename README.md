# A tool for Writing Timecourse Analysis (WTA)

An open-source application implemented in Python for parsing raw keystroke logging data, processing it, and generating text and sentence histories based on the collected information. The input file processed by WTA is an idfx file in XML format.

## Processing Pipeline

### Key Concepts
* TPSF
* Transforming sequence
* Text history
* Sentence histories

### Tool Modes
* Edit Capturing Mode (ECM)
* Pause Capturing Mode (PCM)

### Main processing steps
* Keystroke logging data processing
* Sentence processing
* Text history generation
* Sentence histories generation
* Filtering according to morphosyntactic relevancy

The following figure illustrates the processing pipeline:

![Processing Pipeline](https://github.com/mulasik/wta/blob/main/docs/charts/Concept_Overview.png)

## WTA Configuration

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

## Running WTA

* To install all dependencies, run: 

```
pip install -r requirements.txt
```

* To run the tool, execute:

```
python -m wta config.<YOUR CONFIGURATION NAME>
```


## Text Produced So Far (TPSF)
TPSF is the text produced up to the moment where either the author initializes an edit (ECM) or when the author makes a longer pause (PCM). The text is stored as a data structure called tpsf with the following structure:
```
tpfs = {
	'revision_id': int,
	'preceeding_pause': int,
	'prev_text_version': '',
	'result_text': '',
	'edit': {
		'edit_start_position': int,
		'transforming_sequence': {
			'label': "
			'text': '',
			'tags': []
		},
	},
	'sentences‘: {
		'previous_sentence_list': [],
		'current_sentence_list': [],
		'new_sentences': [],
		'changed_sentences': [],
		'deleted_sentences': [],
		'unchanged_sentences': []
	}
	'morphosyn_relevance_evaluation': [],
	'morphosyntactic_relevance': bool
}
```
* There is always only one edit per TPSF but it may contain multiple tokens.
* All tpsfs are stored in a JSON file. There are two versions of the JSON file: filtered and not filtered.
* The text versions are exported to a TXT file. There are two versions of the TXT file: filtered and not filtered.

### TPSF Example:

```
{
	"revision_id": 5, 
	"prev_text_version": "An edit operation is either removing or inserting a sequence in the beginning, mif without interruption.", 
	"preceeding_pause": 0.45, 
	"result_text": "An edit operation is either removing or inserting a sequence in the beginning, mi without interruption.", 
	"edit": {
		"edit_start_position": 81, 
		"transforming_sequence": {
			"label": "deletion",
			"text": "f", 
			"tags": [{"text": "f", "pos": "X", "pos_details": "LS", "dep": "ROOT", "lemma": "f", "oov": false, "is_punct": false, "is_space": false}]}, 
	"sentences": {
		"previous_sentence_list": [
			{
				"text": "An edit operation is either removing or inserting a sequence in the beginning, mif without interruption.", 
				"start_index": 0, 
				"end_index": 103, 
				"revision_id": 5, 
				"pos_in_text": 0
			}
		], 
		"current_sentence_list": [
			{
				"text": "An edit operation is either removing or inserting a sequence in the beginning, mi without interruption.", 
				"start_index": 0, 
				"end_index": 19, 
				"revision_id": 5, 
				"pos_in_text": 0, 
				"label": "modified"
			}, 
		"new_sentences": [], 
		"edited_sentences": [
			{
				"previous_sentence": {
					"text": "An edit operation is either removing or inserting a sequence in the beginning, mif without interruption.", 
					"start_index": 0, 
					"end_index": 103, 
					"revision_id": 5, 
					"pos_in_text": 0
				}, 
				"current_sentence": {
					"text": "An edit operation is either removing or inserting a sequence in the beginning, mi without interruption.", 
				"start_index": 0, 
				"end_index": 19, 
				"revision_id": 5, 
				"pos_in_text": 0, 
				"label": "modified"
				}
			}
		], 
		"deleted_sentences": [], 
		"unchanged_sentences": []
	}, 
	"morphosyn_relevance_evaluation": [], 
	"morphosyntactic_relevance": true
}
```


## Additional Scripts

### Output Testing
* You can check the outputs for all idfx files stored in the example_data directoy against the reference files also stored in the example_data directory by running the following script: 

```
python tests.py
```


### Checking XML structure
* In order to output the XML structure in the console, run the following script:
```
python xml_content_check.py --xml <path to the xml file to test>
```

## Data Processing Step by Step

### 1. Parse XML
In the first step, the output file of the ScriptLog, the idfx file, is parsed in order to collect the basic tpsf data based on the key logs:

```
tpsf = {
        'revision_id': int,
        'event_description': '',
        'prev_text_version': '',
        'preceeding_pause': int,
        'result_text': '',
        'edit': {
            'edit_start_position': int,
            'edit_beginnging_of_edited_text': '',
            'edit_beginnging_of_result_text': '',
            'removed_sequence': {
                'text': '',
            },
            'inserted_sequence': {
                'text': '',
            },
        },
    }
 ```

### 2. Retrieve Edit Details

Based on the basic data collected in the step "Parsing XML", more detailed data on the edit is retrieved:
* the removed and inserted sequences are tagged
* the entered sequence is retrieved
* the edit operation is defined based on the content of the removed and inserted sequences

**Entered sequence**: the difference between current ```tpsf['result_text']``` and ```current tpsf['prev_text_version']```

There are five edit operation types:
* DEL = 'deletion'
* REPL = 'replacement'
* INS_PAST = 'insertion by pasting'
* INS_ENT = 'insertion by entering'
* NO_EDIT = 'non-edit operation'

```
tpfs = {
	...
	'edit': {
		...
		'edit_operation': '',
		'removed_sequence': {
			'text': '',
			'tags': []
		},
		'inserted_sequence': {
			'text': '',
			'tags': []
		},
		'entered_sequence': {
			'text': '',
			'tags': []
		},
	},
}
```

### 3. Evaluate Morphosyntactic Relevance

Each TPSF is evaluated for its morphosyntactic relevance. 

A TPSF is relevant if any of its sentences have changed and the following conditions are met:
* None of the affected tokens are OOV (neither previous nor current sentence tokens)
* The edit is within one token but the edit distance is more than 3
* The edit comprises multiple tokens (and none of them is OOV)

As a result the tpsf is enriched with:
* details of the morphosyntactic relevance evaluation for each changed sentence
* the final evaluation result indicating morphosyntactic relevance or irrelevance

```
tpfs = {
	...
	'morphosyn_relevance_evaluation': [
		{changed_sentence_pos_in_text:
			'number_affected_tokens': int,
			'affected_tokens': [],
			'is_any_tok_oov': bool,
			'edit_distance': int}
	]
	'morphosyntactic_relevance': bool
}
```
### 4. Retrieve Sentence Data

In this step both the previous text version and the current text version are segmented into sentences using Spacy model and the sentence-level differences are identified. The following steps are performed:

1. Perform sentence segmentation with Spacy
2. Verify sentence segmentation.
3. Improve sentence segmentation: merging segmented and splitting unsegmented sentences which have been evaluated as incorrect.
4. Identify differences on sentence level by:
* retrieving all sentences which haven't occured in the previous text version (-> edited or new sentences) 
* and identifying deleted sentences.
5. Investigate the group of edited and new sentences in order to distinguish between the new and the changed ones, including the merged and the split ones. For changed sentences store the previous sentence version and the current sentence version together. Flag the sentences accordingly. Possible flags: 
* 'new'
* 'merge_result'
* 'split_result'
* 'edited'
* 'deleted'
* 'deleted_due_to_merge'
* 'reinserted'
* 'unchanged'

In order to distinguish between new and edited sentences the transforming sequence is compared either with the current sentence version (for insertion operations) or with the previous sentence version (for deletion operations).

For insertion operations:
* If transforming sequence is the same as the current sentence version, the transforming sequence is a **new sentence**.
* If transforming sequence is longer than the current sentence version and the current sentence is part of the transforming sequence, the current sentence is a **new sentence**.
* If transforming sequence is contained in the current sentence, the sentence is a **changed sentence**.
* If transforming sequence spreads across multiple sentences and the current sentence contains a subsequence of the transforming sequence, the current sentence is a **changed sentence**.

For deletion operations:
* If transforming sequence is contained in the previous sentence version, the sentence is a **changed sentence**.
* If transforming sequence spreads across multiple sentences and the previous sentence version contains a subsequence of the transforming sequence, the corresponding current sentence is a **changed sentence**.

**Deleted sentences** are the ones which occured in the previous TPSF but don't occur in the current sentences and are not classified as changed sentences.

6. Identify sentences which seem to be a result of an erroneous segmentation. Flag them with the flag 'erroneous_sentence'.
7. Retrieve previous sentence version for the edited sentences. The previous sentence candidates are retrieved based on the "affected range". The affected range is calculated as follows:
```
affected_range = range(changed_sentence_start - transforming_seq_len, changed_sentence_end + transforming_seq_len +1)
```
If there is more than one sentence in the affected range, the best candidate is selected.

8. Exclude candidates which belong to the erroneous sentences. Select the best candidate based on the following criteria:

* Insertion operation

As the transforming sequence may be very short, e.g. may contain only two characters which may occur multiple times in more than one candidate sentences, it cannot be used as a basis for best candidate selection. Hence, the best candidate selection is based on the similarity between the unchanged segments of the sentence edited in the TPSF and each candidate sentence. The unchanged segments are defined as the ones which do not contain the transforming sequence.

The candidate with the maximum similarity is selected as the best candidate.

* Deletion operation

For selecting the best candidate, either the transforming sequence or the edited sentence is compared with the sentence candidate and the overlap between the two sequences is calculated. The decision between the transforming sequence and the edited sentence is based on their length: the longer sequence is selected for calculating the overlap.

The candidate with the maximum overlap is selected as the best candidate.

9. Enrich the tpsf with the sentence data.

```
tpfs = {
	...
	'sentences‘: {
		'previous_sentence_list': [],
		'current_sentence_list': [],
		'new_sentences': [],
		'changed_sentences': [],
		'deleted_sentences': [],
		'unchanged_sentences': []
	}
	...
}
```

### 5. Create sentence history

The sentence history is created based on the sentences lists in each TPSF. The tool iterates over the TPSFs list and retrieves new, changed, deleted and unchanged sentences per TPSF. Each new sentence which occur in a TPSF gets a unique id. The changed, deleted and unchanged sentences which occur in the following TPSFs are matched with the already existing sentences. For the changed sentences it is the previous sentence version which is matched with the sentence already existing in the sentence history. 

A sentence history is a dictionary containing sentence unique ids as keys and lists of sentence versions as values. Each sentence version contains the following data: 
* sentence text, 
* sentence start index, 
* sentence end index, 
* revision id where the sentence version occured, 
* sentence number in text, 
* flag describing the edit operation 
* and revision relevance.


```
sentence_history = {
	...
	sentence_uid: [
		{
			'text': '',
			'start_index': int,
			'end_index': int,
			'revision_id': int,
			'pos_in_text': int,
			'flag': '',
			'revision_relevance': bool,
        	},
		...
	]
	...
}
```

Example:

```

sentence_history = {
	"205519013811540311649025281626031925285": [
		{
			"text": "Ich habe einen Hund.", 
			"start_index": 0, 
			"end_index": 29, 
			"revision_id": 7, 
			"pos_in_text": 0, 
			"flag": "edit", 
			"revision_relevance": true
		}, 
		{
			"text": "Ich habe einen Hund, der ist braun.", 
			"start_index": 0, 
			"end_index": 34, 
			"revision_id": 8, 
			"pos_in_text": 0, 
			"flag": "edit", 
			"revision_relevance": true
		}, 
		{
			"text": "Ich habe einen Hund, der braun ist.", 
			"start_index": 0, 
			"end_index": 34, 
			"revision_id": 22, 
			"pos_in_text": 0, 
			"flag": "unchanged", 
			"revision_relevance": true
		}
	], 
	"205519032826299315072466304076580005925": [
		{
			"text": "Er ist braun.", 
			"start_index": 21, 
			"end_index": 33, 
			"revision_id": 2, 
			"pos_in_text": 1, 
			"flag": "new", 
			"revision_relevance": false
		},
		{
			"text": null, 
			"start_index": null, 
			"end_index": null, 
			"revision_id": 7, 
			"pos_in_text": null, 
			"flag": "del", 
			"revision_relevance": true
		}
	], 
	"205519036787707440785683183753777522725": [
		{
			"text": "Ich gehe mit ihm oft spazieren.", 
			"start_index": 35, 
			"end_index": 65, 
			"revision_id": 4, 
			"pos_in_text": 2, 
			"flag": "edit", 
			"revision_relevance": true
		}, 
		{
			"text": "Wenn ich Zeit, Ich gehe mit ihm oft spazieren.", 
			"start_index": 36, 
			"end_index": 81, 
			"revision_id": 16, 
			"pos_in_text": 1, 
			"flag": "edit", 
			"revision_relevance": true
		}, 
		{
			"text": "Wenn ich Zeit habe, gehe ich mit ihm oft spazieren.", 
			"start_index": 36, 
			"end_index": 86, 
			"revision_id": 22, 
			"pos_in_text": 1, 
			"flag": "edit", 
			"revision_relevance": true
		}
	]
}

```

### Filter sentence history

Out of all sentence versions stored in the ```sentence_history``` only the relevant ones are selected. The relevance criteria are:
* revision relevance is set to true
* revision relevance is not true but this is the only version of the sentence before it got deleted
* revision relevance is not true but this is the last sentence version

## Sentence-Level Operations

Each sentence-level operation is a result of the author inserting, entering or deleting a sequence. The added or removed sequence is called **transforming sequence**. The TPSF revisions are caputured after ONE edit operation, so there is only ONE position in the text where the edit operation starts and only ONE transforming sequence per TPSF. However, the transforming sequence may contain multiple sentences and hence result in a complexer edit operation.

### Example

Transforming the text:

*Texting is the act of composing and sending electronic messages. They may be sent via an Internet connection.*

Into:

*Texting is the act of composing and sending electronic messages, typically consisting of alphabetic and numeric characters. They can be sent between two or more users of mobile devices. Text messages may be sent over a cellular network and they may be sent via an Internet connection.*

#### TPSF 1

* Edit operation: deletion

* Transforming sequence: *.*

* Previous sentence version:

*Texting is the act of composing and sending electronic messages<ins>.</ins> They may be sent via an Internet connection.*

* Current sentence version:

*Texting is the act of composing and sending electronic messages They may be sent via an Internet connection.*


#### TPSF 2

* Edit operation: insertion

* Transforming sequence: 

*, typically consisting of alphabetic and numeric characters. They can be sent between two or more users of mobile devices. Text messages may be sent over a cellular network and*

* Previous sentence version

*Texting is the act of composing and sending electronic messages They may be sent via an Internet connection.*

* Current sentence version

*Texting is the act of composing and sending electronic messages <ins>, typically consisting of alphabetic and numeric characters. They can be sent between two or more users of mobile devices. Text messages may be sent over a cellular network and</ins> They may be sent via an Internet connection.*


#### TPSF 3

* Edit operation: deletion

* Transforming sequence: *T*

* Previous sentence version

*Texting is the act of composing and sending electronic messages, typically consisting of alphabetic and numeric characters. They can be sent between two or more users of mobile devices. Text messages may be sent over a cellular network and <ins>T</ins>hey may be sent via an Internet connection.*

* Current sentence version

*Texting is the act of composing and sending electronic messages, typically consisting of alphabetic and numeric characters. They can be sent between two or more users of mobile devices. Text messages may be sent over a cellular network and hey may be sent via an Internet connection.*

#### TPSF 4

* Edit operation: insertion

* Transforming sequence: *t*

* Previous sentence version

*Texting is the act of composing and sending electronic messages, typically consisting of alphabetic and numeric characters. They can be sent between two or more users of mobile devices. Text messages may be sent over a cellular network and hey may be sent via an Internet connection.*

* Current sentence version

*Texting is the act of composing and sending electronic messages, typically consisting of alphabetic and numeric characters. They can be sent between two or more users of mobile devices. Text messages may be sent over a cellular network and <ins>t</ins>hey may be sent via an Internet connection.*

### Sentence-Level Operations Handling

There are nine sentence-level operations handled by the tool:
* complete sentence deletion and reinsertion -> the same sentence occurs again after deletion  at a SAME position in the text 
* complete sentence deletion & reinsertion with transposition -> the same sentence occurs again after deletion at a DIFFERENT position in the text 
* complete sentence insertion -> a whole sentence is inserted
* complete sentence deletion -> a whole sentence is deleted
* sentences merge -> two sentences are merged
* sentences split -> two sentences are split
* sentence edit -> a sentence gets modified
* sentence insertion and edit of the following sentence -> one sentence gets inserted and the following sentence gets changed (a sequence is added to the sentence)
* sentence deletion and edit of the following sentence -> one sentence gets deleted and the following sentence gets changed (a sequence is removed from the sentence)

The following chart presents the sentece-level operations in relation to the content of the transforming sequence.

Please note, that the transforming sequence is either included in the previous sentence version (for deletion operations) or in the current sentence versions (for insertion operations).

![Sentence-Level Operations Diagramm](https://github.com/mulasik/wta/blob/main/docs/charts/Sentence-Level_Operations.png)


