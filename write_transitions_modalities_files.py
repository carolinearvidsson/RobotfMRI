from filereader import FilesList
from ds import DataStructure
from conversations import Conversations
import csv
import sys

if __name__ == '__main__':
    path = sys.argv[1]
    transfiles = FilesList.get_transfiles(path)
    datastr = DataStructure(transfiles)
    c = Conversations(datastr.structure, path)

    with open(path + 'transitions.csv', 'w') as f:
        transitions_header = ['participantid', 'condition', 'session', 'conversation', 'onset', 'duration', 'within_speaker', 'speaker_prior_turn', 'speaker_subsequent_turn', 'type', 'n_token', 'subsequent_utterance']
        c.transitions_data.insert(0, transitions_header)
        writer = csv.writer(f)
        for row in c.transitions_data:
            print(row)
            writer.writerow(row)
    f.close()

    with open(path + 'modalities.csv', 'w') as f:
        modality_header = ['participantid', 'condition', 'session', 'conversation', 'onset', 'duration', 'production', 'comprehension', 'n_token', 'utterance', 'tdl']
        c.modality.insert(0, modality_header)
        writer = csv.writer(f)
        for row in c.modality:
            writer.writerow(row)
    f.close()
    
    