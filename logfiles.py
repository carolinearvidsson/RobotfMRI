from cmath import log
import csv
import glob

class LogFiles:

    def __init__(self):
        path_eventfiles = 'logfiles/*.tsv'
        self.onsdurs_from_eventfiles = self.get_logfile_data(path_eventfiles) # Nested dict where each key is tuple(partID, run) and each element is {names = ['ISI', 'CONV1', 'INSTR'], onsets = [[onsets ISI], [onsets CONV1], ...], durations = [[durations ISI], [durations CONV1], ...]}

    def get_logfile_data(self, path):
        logfile_data = dict()
        for logfilename in glob.glob(path):
            with open(logfilename) as logfile:
                subj_ID, run_nr = 'subj' + logfilename.split('_')[0].split('/')[-1][-3:], logfilename.split('_')[2][-1]
                file_ID = subj_ID + '_' + run_nr
                logfile_data[file_ID] = {}
                lfile = csv.reader(logfile, delimiter = '\t')
                logfilerows = [row for row in lfile]
                names = list(set([name[2] for name in logfilerows if name[2] != 'trial_type']))
                onsets = []
                durations = []
                del logfilerows[0]
                for name in names:
                    name_onsets = []
                    name_durations = []
                    for row in logfilerows:
                        onset, duration = float(row[0]), float(row[1])
                        if row[2] == name:
                            name_onsets.append(onset)
                            name_durations.append(duration)
                    onsets.append(name_onsets)
                    durations.append(name_durations)
            logfile_data[file_ID] = {}
            logfile_data[file_ID]['names'] = names
            logfile_data[file_ID]['onsets'] = onsets
            logfile_data[file_ID]['durations'] = durations
        return logfile_data