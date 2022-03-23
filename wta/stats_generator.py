import os
from bs4 import BeautifulSoup
import json
import numpy as np


'''
Statistics contain:
    Events
    - Number events, number keystrokes, replacements and inserts
    Text versions
    - Edit Capturing Mode: number text revisions (all)
    - Pause Capturing Mode: number text revisions (all)
    - Edit Capturing Mode: number text revisions (filtered)
    Pauses
    - Pauses (avg, min, max)
    Transforming sequences
    - TS length (avg)
    - Insertions number
    - Number inserted characters
    - Deletions number
    - Number deleted characters
    Sentences
    - Number detected sentences
    - Number sentences in the final version
    - Mean number versions per sentence
    - Number unchanged sentences
    - Number changed sentences * 
    - Number deleted sentences *
'''


def retrieve_events_stats(idfx):
    soup = BeautifulSoup(open(idfx), features="lxml")
    events = soup.find_all('event')
    number_events = len(events)
    number_keystrokes, number_replacements, number_insertions = 0, 0, 0
    for e in events:
        if e['type'] == 'keyboard':
            number_keystrokes += 1
        if e['type'] == 'replacement':
            number_replacements += 1
        if e['type'] == 'insert':
            number_insertions += 1
    return number_events, number_keystrokes, number_replacements, number_insertions


def retrieve_pause_stats(data):
    pauses = []
    total_pauses_duration = 0
    for d in data:
        if d['preceeding_pause']:
            pauses.append(d['preceeding_pause'])
            total_pauses_duration += d['preceeding_pause']
    avg_pause_duration = round(total_pauses_duration / len(pauses))
    return avg_pause_duration, max(pauses), min(pauses)


def retrieve_ts_stats(data):
    transforming_sequences_texts = []
    number_nonempty_ts = 0
    number_insertions, number_deletions, number_appends = 0, 0, 0
    number_inserted_chars, number_deleted_chars, number_appended_chars = 0, 0, 0
    for d in data:
        if len(d['edit']['transforming_sequence']['text']) > 0:
            number_nonempty_ts += 1
            transforming_sequences_texts.append(d['edit']['transforming_sequence']['text'])
        if d['edit']['transforming_sequence']['label'] == 'insertion':
            number_insertions += 1
            number_inserted_chars += len(d['edit']['transforming_sequence']['text'])
        if d['edit']['transforming_sequence']['label'] == 'deletion':
            number_deletions += 1
            number_deleted_chars += len(d['edit']['transforming_sequence']['text'])
        if d['edit']['transforming_sequence']['label'] == 'append':
            number_appends += 1
            number_appended_chars += len(d['edit']['transforming_sequence']['text'])
    total_ts_length = 0
    for tst in transforming_sequences_texts:
        total_ts_length += len(tst)
    avg_ts_length = round(total_ts_length / len(transforming_sequences_texts))

    return number_nonempty_ts, avg_ts_length, number_insertions, number_deletions, number_appends, number_inserted_chars, number_deleted_chars, number_appended_chars


def retrieve_senteces_stats(data_sentences, data_ecm):
    detected_sentences = len(data_sentences)
    number_unchanged_senteces = 0
    number_sentence_versions = []
    max_number_sen_versions = 0
    number_potentially_erroneous_sentences = 0
    for ds in data_sentences.values():
        if len(ds) == 1:
            number_unchanged_senteces += 1
        if len(ds) == 2:
            number_potentially_erroneous_sentences += 1
        if len(ds) > max_number_sen_versions:
            max_number_sen_versions = len(ds)
            sen_with_most_versions = ds[-1]['text']
        number_sentence_versions.append(len(ds))
    mean_number_sentence_versions = round(np.mean(number_sentence_versions), 2)
    final_number_sentences = len(data_ecm[-1]['sentences']['current_sentence_list'])
    return detected_sentences, final_number_sentences, number_potentially_erroneous_sentences, max_number_sen_versions, sen_with_most_versions, mean_number_sentence_versions, number_unchanged_senteces


def generate_statistics(idfx, output_dir, filename):
    number_events, number_keystrokes, number_replacements, number_insert_events = retrieve_events_stats(idfx)
    json_file_ecm = os.path.join(output_dir, filename + '_text_history_ecm.json')
    json_file_ecm_filtered = os.path.join(output_dir, filename + '_text_history_ecm_filtered.json')
    json_file_pcm = os.path.join(output_dir, filename + '_text_history_pcm.json')
    json_file_sentences = os.path.join(output_dir, filename + '_sentence_history.json')
    with open(json_file_ecm, 'r') as jf:
        data_ecm = json.load(jf)
    with open(json_file_ecm_filtered, 'r') as jf:
        data_ecm_filtered = json.load(jf)
    with open(json_file_pcm, 'r') as jf:
        data_pcm = json.load(jf)
    with open(json_file_sentences, 'r') as jf:
        data_sentences = json.load(jf)
    detected_sentences, final_number_sentences, number_potentially_erroneous_sentences, max_number_sen_versions, sen_with_most_versions, mean_number_sentence_versions, number_unchanged_senteces = retrieve_senteces_stats(data_sentences, data_ecm)
    avg_pause_duration, max_pause_duration, min_pause_duration = retrieve_pause_stats(data_ecm)
    number_nonempty_ts, avg_ts_length, number_insertions, number_deletions, number_appends, number_inserted_chars, number_deleted_chars, number_appended_chars = retrieve_ts_stats(data_ecm)
    task_name = os.path.split(os.path.split(idfx)[0])[-1]
    user_name = filename.split('_', 1)[0]
    txt_file_path = os.path.join(output_dir, filename + '_basic_statistics.txt')
    with open(txt_file_path, 'w') as f:
        f.write(f'''TASK: {task_name}
USER: {user_name}
SOURCE FILE: {filename + '.idfx'}

- EVENTS IN THE LOG FILE -
    Number events of type keyboard, replacement, insert: {number_events}
    Number keystrokes: {number_keystrokes} 
    Number replacements: {number_replacements}
    Number insert events: {number_insert_events}

- TEXT VERSIONS -
    Number text versions in edit capturing mode (unfiltered): {len(data_ecm)}
    Number text versions in edit capturing mode (filtered): {len(data_ecm_filtered)}
    Number text versions in pause capturing mode: {len(data_pcm)}

- PAUSES -
    Average pauses duration: {avg_pause_duration}
    Maximum pauses duration: {max_pause_duration}
    Minimum pauses duration: {min_pause_duration}

- TRANSFORMING SEQUENCES -
    Number transforming sequences: {number_nonempty_ts} 
    Average transforming sequence length: {avg_ts_length}
    Number insertions: {number_insertions}
    Number inserted characters: {number_inserted_chars}
    Number deletions: {number_deletions}
    Number deleted characters: {number_deleted_chars}
    Number appends: {number_appends}
    Number appended characters: {number_appended_chars}

- SENTENCES -
    Number detected sentences in total: {detected_sentences}
    Number sentences in the final text: {final_number_sentences}
    Potentially erroneous sentences due to segmentation problems: {number_potentially_erroneous_sentences}
    Maximum number sentence versions: {max_number_sen_versions}. 
    The sentence with most versions: "{sen_with_most_versions}"
    Mean number sentence versions: {mean_number_sentence_versions}
    Number unchanged sentences: {number_unchanged_senteces}
''')

