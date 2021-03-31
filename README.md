# A tool for Linguistic Modeling of Written Text Production

An open-source application implemented in Python for parsing raw keystroke logging data from a writing session, processing it to retrieve all relevant text versions produced during this session, and eventually generating text and sentence histories based on the collected information. 

The input file processed by the tool is an idfx file in XML format.

The tool uses two main modes to capture text versions from idfx files: 
* the Pause Capturing Mode (PCM), which relies on a preset pause duration in the text production to yield versions, 
* and the Edit Capturing Mode (ECM), which uses a change production mode to determine versions. A  change  in  production  mode  is  defined  as switching between one of the modes (a) writing at the edge of the text, (b) deleting something, (c) inserting something.

## Tool Outputs

The main outputs of the tool are:
* complete text history in ECM in JSON format
* all text versions in ECM exported to TXT format
* visualisation of text history in ECM in SVG format
* complete text history in PCM in JSON format
* sentence history in JSON format
* sentence history visualisation in SVG format

In case filtering has been activated in the configuration:
* filtered text history in JSON format
* filtered text versions exported to TXT format 
* filtered sentence history in JSON format
* visualisation of filtered text history in ECM in SVG format
* filtered sentence history visualisation in SVG format

## Processing Pipeline

Generating a complete TPSF comprises the following steps: 
* First the input file is parsed and the keystroke logging data is processed to capture all details on the particular text version. 
* This data is next used to create a TPSF instance and subsequently to retrieve information on the sentences constituting this version. 
* Finally, the version is evaluated for its morphosyntactic relevance. 

In each step, the TPSF instance is enriched with the newly collected details.

An accomplished collection of TPSF instances results in a text history which constitutes the basis for another output: the sentence history. Based on the relevancy label of each TPSF instance, both the text and the sentence history can be filtered. 

The following figure illustrates the processing pipeline:

![Processing Pipeline](https://github.com/mulasik/wta/blob/main/docs/charts/Concept_Overview.png)

#### Keystroke logging data processing
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




