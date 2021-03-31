# A tool for Writing Timecourse Analysis (WTA)

An open-source application implemented in Python for parsing raw keystroke logging data, processing it, and generating text and sentence histories based on the collected information. The input file processed by WTA is an idfx file in XML format.

## Processing Pipeline

### Key Concepts

#### TPSF
#### Transforming sequence
#### Text history
#### Sentence histories

### Tool Modes

#### Edit Capturing Mode (ECM)
#### Pause Capturing Mode (PCM)

### Main processing steps

#### Keystroke logging data processing
#### Sentence processing
#### Text history generation
#### Sentence histories generation
#### Filtering according to morphosyntactic relevancy

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




