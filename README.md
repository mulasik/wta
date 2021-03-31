# A tool for Linguistic Modeling of Written Text Production

An open-source application implemented in Python for parsing raw keystroke logging data, processing it, and generating text and sentence histories based on the collected information. The input file processed by the tool is an idfx file in XML format.

The central building block of THE TOOL is \emph{TPSF data structure} (\emph{TDS}). It is used to store the text version together with further details. 

Since the interpretation of version may differ according to research questions, our approach uses two main modes to capture versions from idfx files: the \term{Pause Capturing Mode} (PCM), which relies on a preset pause duration to yield versions, and the \term{Edit Capturing Mode} (ECM), which uses a change production mode to determine versions.  As soon as a new version is detected, it is stored in a TDS. In PCM, a TDS consists of the captured text version and the preceding pause duration.  In ECM, a TDS additionally contains the previous text version, revision number, the transforming sequence (see section \ref{sec:transforming-sequences}), categorized list of sentences which make up this version, and the result of morphosyntactic relevance evaluation. 

## Main Outputs

## Processing Pipeline

#### Keystroke logging data processing
#### Sentence processing
#### Text history generation
#### Sentence histories generation
#### Filtering according to morphosyntactic relevancy

The following figure illustrates the processing pipeline:

![Processing Pipeline](https://github.com/mulasik/wta/blob/main/docs/charts/Concept_Overview.png)

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




