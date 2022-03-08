from os import remove
from logfiles import LogFiles
from filereader import FilesList
from ds import DataStructure
from conversations import Conversations

class OnsetsDurations:
    def __init__(self, path):
        transfiles = FilesList.get_transfiles(path)
        datastr = DataStructure(transfiles)
        l = LogFiles()
        print('Parsing logfiles...')
        self.onsdurs_output = l.onsdurs_from_eventfiles
        
        c = Conversations(datastr.structure, path)
        print('Creating onsets and durations for production and comprehension periods...')
        self.get_events_times(c.modality, 'modality')
        print('Creating onsets and durations for transition periods...')
        self.get_events_times(c.transitions_data, 'transitions')
        print('Removing old events from original event files...')
        self.remove_old_events(['CONV1', 'CONV2'])
        
        self.final_output = self.collapse_conditions(self.onsdurs_output, [['OVRL_r2p'], ['OVRL_p2r'], ['OVRL_wr'], ['OVRL_wp']], ['OVRL'])

        #print(self.final_output['subj-17_4'])

    def get_events_times(self, events_data, event_type):  
        '''Gets new events (name, onsets, durations) from the logfiles and the transcription data '''
        subjects = list(set([subj[0].lower() for subj in events_data]))
        subjects.sort()

        runs = list(set([run[2] for run in events_data]))
        runs.sort()

        conversations = list(set([conv[3] for conv in events_data]))
        conversations.sort()

        human_CONV1 = ['1', '3', '5']
        robot_CONV2 = ['2', '4', '6']

        for sub in subjects:

            for run in runs:
                SubjRunID = sub + '_' + run

                if event_type == 'modality': 
                    comp_r_name, self.comp_r_onsets, self.comp_r_durs = 'COMP_r', [], []
                    comp_h_name, self.comp_h_onsets, self.comp_h_durs = 'COMP_h', [], []
                    prod_r_name, self.prod_r_onsets, self.prod_r_durs = 'PROD_r', [], []
                    prod_h_name, self.prod_h_onsets, self.prod_h_durs = 'PROD_h', [], []

                    names = (comp_r_name, comp_h_name, prod_r_name, prod_h_name)
                    onsets = (self.comp_r_onsets, self.comp_h_onsets, self.prod_r_onsets, self.prod_h_onsets)
                    durations = (self.comp_r_durs, self.comp_h_durs, self.prod_r_durs, self.prod_h_durs)
                    
                elif event_type == 'transitions':
                    gap_p2r_name, self.gap_p2r_onsets, self.gap_p2r_durs = 'GAP_p2r', [], []
                    gap_r2p_name, self.gap_r2p_onsets, self.gap_r2p_durs = 'GAP_r2p', [], []
                    pause_r_name, self.pause_r_onsets, self.pause_r_durs = 'PAUSE_r', [], []
                    pause_p_name, self.pause_p_onsets, self.pause_p_durs = 'PAUSE_p', [], []
                    ovrl_p2r_name, self.ovrl_p2r_onsets, self.ovrl_p2r_durs = 'OVRL_p2r', [], []
                    ovrl_r2p_name, self.ovrl_r2p_onsets, self.ovrl_r2p_durs = 'OVRL_r2p', [], []
                    ovrl_wp_name, self.ovrl_wp_onsets, self.ovrl_wp_durs = 'OVRL_wp', [], []
                    ovrl_wr_name, self.ovrl_wr_onsets, self.ovrl_wr_durs = 'OVRL_wr', [], []
                    
                    names = (gap_p2r_name, gap_r2p_name, pause_r_name, pause_p_name,
                        ovrl_p2r_name, ovrl_r2p_name, ovrl_wp_name, ovrl_wr_name)
                    onsets = (self.gap_p2r_onsets, self.gap_r2p_onsets, self.pause_r_onsets,
                        self.pause_p_onsets, self.ovrl_p2r_onsets, self.ovrl_r2p_onsets,
                            self.ovrl_wp_onsets, self.ovrl_wr_onsets)
                    durations = (self.gap_p2r_durs, self.gap_r2p_durs, self.pause_r_durs, 
                        self.pause_p_durs, self.ovrl_p2r_durs, self.ovrl_r2p_durs, 
                           self.ovrl_wp_durs, self.ovrl_wr_durs)

                for conv in conversations:
                    for row in events_data:
                        onset = float(row[4])
                        duration = float(row[5])
                        if row[0] == sub and row[2] == run and row[3] == conv:
                            if conv in human_CONV1:
                                name_index = self.onsdurs_output[SubjRunID]['names'].index('CONV1')
                                conv_onset = float(self.onsdurs_output[SubjRunID]['onsets'][name_index][human_CONV1.index(conv)])
                                if event_type == 'modality': 
                                
                                    if self.check_modality((row[-2], row[-1])) == 'comprehension':  
                                        self.comp_h_onsets.append(conv_onset + onset)
                                        self.comp_h_durs.append(duration)

                                    elif self.check_modality((row[-2], row[-1])) == 'production':
                                        self.prod_h_onsets.append(conv_onset + onset)
                                        self.prod_h_durs.append(duration)

                                elif event_type == 'transitions':
                                    self.append_transition_parameters(row, onset, duration, conv_onset)

                            elif conv in robot_CONV2:
                                name_index = self.onsdurs_output[SubjRunID]['names'].index('CONV2')
                                conv_onset = float(self.onsdurs_output[SubjRunID]['onsets'][name_index][robot_CONV2.index(conv)])
                                
                                if event_type == 'modality':
                                    if self.check_modality((row[-2], row[-1])) == 'comprehension':  
                                        self.comp_r_onsets.append(conv_onset + onset)
                                        self.comp_r_durs.append(duration)
                                    elif self.check_modality((row[-2], row[-1])) == 'production':
                                        self.prod_r_onsets.append(conv_onset + onset)
                                        self.prod_r_durs.append(duration)

                                elif event_type == 'transitions':
                                    self.append_transition_parameters(row, onset, duration, conv_onset)
                    
                for name, ons_list, dur_list in zip(names, onsets, durations):
                    self.append_name_onset_duration(SubjRunID, [name], ons_list, dur_list)
                    #print(SubjRunID, name, ons_list, dur_list)
                    #print(type(SubjRunID), type(name), type(ons_list), type(dur_list))
                #for name, ons_list, dur_list in zip(names, onsets, durations):
                #    print('name_type: ', type(name), 'ons_type: ','\n', [type(ons) for ons in ons_list if type(ons) == str], [type(dur) for dur in dur_list if type(dur) == str])


    def append_transition_parameters(self, row, onset, duration, conv_onset):
        new_onset = float(conv_onset + onset)
        if self.check_transition(row) == 'GAP_p2r':
            self.gap_p2r_onsets.append(new_onset)
            self.gap_p2r_durs.append(duration)
        elif self.check_transition(row) == 'GAP_r2p':
            self.gap_r2p_onsets.append(new_onset)
            self.gap_r2p_durs.append(duration)
        elif self.check_transition(row) == 'PAUSE_p':
            self.pause_p_onsets.append(new_onset)
            self.pause_p_durs.append(duration)
        elif self.check_transition(row) == 'PAUSE_r':
            self.pause_r_onsets.append(new_onset)
            self.pause_r_durs.append(duration)
        elif self.check_transition(row) == 'OVRL_p2r':
            self.ovrl_p2r_onsets.append(new_onset)
            self.ovrl_p2r_durs.append(duration)
        elif self.check_transition(row) == 'OVRL_r2p':
            self.ovrl_r2p_onsets.append(new_onset)
            self.ovrl_r2p_durs.append(duration)
        elif self.check_transition(row) == 'OVRL_wp':
            self.ovrl_wp_onsets.append(new_onset)
            self.ovrl_wp_durs.append(duration)
        elif self.check_transition(row) == 'OVRL_wr':
            self.ovrl_wr_onsets.append(new_onset)
            self.ovrl_wr_durs.append(duration)

    def collapse_conditions(self, d, to_collapse, new_name):
        print('Collapsing following conditions: ', to_collapse, ' into: ', new_name)
        for subjrun in d:
            hold_onsdurs = {}
            new_onsets = []
            new_durs = []
            old_durs = []
            old_ons = []
            for name in d[subjrun]['names']:
                if name in to_collapse:
                    name_index = d[subjrun]['names'].index(name)
                    name_onsets = d[subjrun]['onsets'][name_index]
                    name_durations = d[subjrun]['durations'][name_index]
                    old_ons.append(name_onsets)
                    old_durs.append(name_durations)
                    for ons, dur in zip(name_onsets, name_durations):
                        hold_onsdurs[ons] = dur
            for ons in sorted(hold_onsdurs):
                new_onsets.append(ons)
                new_durs.append(hold_onsdurs[ons])
            for na, on, du in zip(to_collapse, old_ons, old_durs):
                d[subjrun]['names'].pop(d[subjrun]['names'].index(na))
                d[subjrun]['onsets'].pop(d[subjrun]['onsets'].index(on))
                d[subjrun]['durations'].pop(d[subjrun]['durations'].index(du))
            d[subjrun]['names'].append(new_name)
            d[subjrun]['onsets'].append(new_onsets)
            d[subjrun]['durations'].append(new_durs)
        return d

    def append_name_onset_duration(self, subjrunid, n, o, d):
        #print(type(subjrunid), type(n), [type(ons) for ons in o], [type(dur) for dur in d])
        self.onsdurs_output[subjrunid]['names'].append(n)#np.array(name, dtype=str))
        self.onsdurs_output[subjrunid]['onsets'].append(o)#np.array(onsets, dtype=float))
        self.onsdurs_output[subjrunid]['durations'].append(d)#np.array(durations, dtype=float))

    def check_transition(self, l):
        previous_speaker = l[7]
        subsequent_speaker = l[8]
        typ = l[9]
        patterns = [['GAP_p2r', 'participant', 'researcher', 'silence'],
            ['GAP_r2p', 'researcher', 'participant', 'silence'],
            ['PAUSE_r', 'researcher', 'researcher', 'silence'],
            ['PAUSE_p', 'participant', 'participant', 'silence'],
            ['OVRL_p2r', 'participant', 'researcher', 'speech'],
            ['OVRL_r2p', 'researcher', 'participant', 'speech'],
            ['OVRL_wp', 'participant', 'participant', 'speech'],
            ['OVRL_wr', 'researcher', 'researcher', 'speech']]
        for pattern in patterns:
            if previous_speaker in pattern[1] and subsequent_speaker in pattern[2] and typ in pattern[3]:
                return pattern[0]


    def check_modality(self, t):
        modality = 'comprehension'
        if t[0] == 1:
            modality = 'production'
        return modality

    def remove_old_events(self, old_events):
        for subjrun in self.onsdurs_output:
            names = self.onsdurs_output[subjrun]['names']
            onsets = self.onsdurs_output[subjrun]['onsets']
            durations = self.onsdurs_output[subjrun]['durations']
            for evnt  in old_events:
                evnt_indx = names.index(evnt)
                del names[evnt_indx]
                del onsets[evnt_indx]
                del durations[evnt_indx]

