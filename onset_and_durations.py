from hashlib import new
import pickle
from re import sub 
from logfiles import LogFiles
from filereader import FilesList
from ds import DataStructure
from conversations import Conversations
from itertools import repeat
import numpy as np

class OnsetsDurations: 
    def __init__(self, path):

        transfiles = FilesList.get_transfiles(path)
        datastr = DataStructure(transfiles)
        l = LogFiles()
        print('Parsing logfiles...')

        self.pmod = self.set_pmod(l.onsdurs_from_eventfiles)
        self.onsdurs_output = l.onsdurs_from_eventfiles
        
        c = Conversations(datastr.structure, path)
        print('Creating onsets and durations for production and comprehension periods...')
        self.get_events_times(c.modality, 'modality')
        
        print('Creating onsets and durations for transition periods...')
        self.get_events_times(c.transitions_data, 'transitions')

        print('Removing old events from original event files...')
        self.remove_old_events(['CONV1', 'CONV2'])

        collapsed = self.collapse_conditions(self.onsdurs_output, [['PAUSE_c_h'], ['PAUSE_p_h'], ['GAP_p2c_h'], ['GAP_c2p_h'], ['TI_h']], ['SILENCE_h'])
        self.final_output = self.collapse_conditions(collapsed, [['PAUSE_c_r'], ['PAUSE_p_r'], ['GAP_p2c_r'], ['GAP_c2p_r'], ['TI_r']], ['SILENCE_r'])

        # Add eventual orthogonalization info
        #orths = self.set_orth(collapsed)

        #self.final_output = self.crop_duration(collapsed) #remove events <300 ms

        #self.check_if_pmod_code_works(self.final_output)

        #this piece saves ons durs output in a file that can be loaded later in the notebook
        a_file = open("pickles/onsdurs_collapsed_cropped.pkl", "wb")
        pickle.dump(self.final_output, a_file)
        a_file.close()
        
        #------------------------------------------------------------------#
        #this is an optional function for a model with 600ms events
        #self.final_output_600 = self.model_600ms()  
        #------------------------------------------------------------------#

        #------------------------------------------------------------------#
        #For onsdurs.mat files for marseille replication
        #self.final_output = self.replicate_marseille() 
        #------------------------------------------------------------------#]

    def set_orth(self, d):
        if self.pmod == True:
            for subjrun in d:
                for name in d[subjrun]['names']:
                    if name in self.with_pmod:
                        d[subjrun].setdefault('orth', []).append(1)
                    else: 
                        d[subjrun].setdefault('orth', []).append(0)
        return d

    def add_pmod(self, logfiledict):
        '''This function adds pmods as an additional category, apart from names, onsets and durations'''
        self.with_pmod = [['PROD_h'], ['COMP_h']] #, ['TI_h']]
        # self.without_pmod = ['ISI', 'INSTR1', ['PROD_r'], ['']]
        subjectandruns = list(set([subjrun for subjrun in logfiledict]))
        subjectandruns.sort()

        for subjrun in subjectandruns:
            logfiledict[subjrun]['pmod'] = {}

    def get_events_times(self, events_data, event_type):  
        '''Gets new events (name, onsets, durations, and optional pmod) from the logfiles and the transcription data '''
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


                    ### THESE WILL BE USED WHEN WE TRY PMOD FOR ONLY  word utterances
                    prod_h_npmod_name, self.prod_h_npmod_onsets, self.prod_h_npmod_durs = 'prod_npmod_h', [], []
                    comp_h_npmod_name, self.comp_h_npmod_onsets, self.comp_h_npmod_durs = 'comp_npmod_n', [], []
                    ###

                    names = (comp_h_name, prod_h_name, comp_r_name, prod_r_name, comp_h_npmod_name, prod_h_npmod_name)
                    onsets = (self.comp_h_onsets, self.prod_h_onsets, self.comp_r_onsets, self.prod_r_onsets, self.comp_h_npmod_onsets, self.prod_h_npmod_onsets)
                    durations = (self.comp_h_durs, self.prod_h_durs, self.comp_r_durs, self.prod_r_durs, self.comp_h_npmod_durs, self.prod_h_npmod_durs)

                    ###----------PMODS----------###
                    if self.pmod == True:
                        self.comp_h_tdl, self.prod_h_tdl, self.comp_r_tdl, self.prod_r_tdl = [], [], [], []
                        self.comp_r_ul, self.prod_r_ul, self.comp_h_ul, self.prod_h_ul = [], [], [], []
                        self.comp_h_mtdl, self.prod_h_mtdl, self.comp_r_mtdl, self.prod_r_mtdl = [], [], [], []
                        #pmods is now a list of lists where the first list is ul and second list is tdl
                        pmods = ([self.comp_h_ul,self.comp_h_tdl, self.comp_h_mtdl], [self.prod_h_ul, self.prod_h_tdl, self.prod_h_mtdl], \
                                                    [self.comp_r_ul, self.comp_r_tdl, self.comp_r_mtdl], [self.prod_r_ul, self.prod_r_tdl, self.prod_r_mtdl])
                    ###-------------------------###
                    
                elif event_type == 'transitions':
                    gap_p2c_name_h, self.gap_p2c_onsets_h, self.gap_p2c_durs_h = 'GAP_p2c_h', [], []
                    gap_c2p_name_h, self.gap_c2p_onsets_h, self.gap_c2p_durs_h = 'GAP_c2p_h', [], []
                    pause_c_name_h, self.pause_c_onsets_h, self.pause_c_durs_h = 'PAUSE_c_h', [], []
                    pause_p_name_h, self.pause_p_onsets_h, self.pause_p_durs_h = 'PAUSE_p_h', [], []
                    
                    turn_init_h_name, self.turn_init_h_onsets, self.turn_init_h_durs = 'TI_h', [], []

                    gap_p2c_name_r, self.gap_p2c_onsets_r, self.gap_p2c_durs_r = 'GAP_p2c_r', [], []
                    gap_c2p_name_r, self.gap_c2p_onsets_r, self.gap_c2p_durs_r = 'GAP_c2p_r', [], []
                    pause_c_name_r, self.pause_c_onsets_r, self.pause_c_durs_r = 'PAUSE_c_r', [], []
                    pause_p_name_r, self.pause_p_onsets_r, self.pause_p_durs_r = 'PAUSE_p_r', [], []

                    turn_init_r_name, self.turn_init_r_onsets, self.turn_init_r_durs = 'TI_r', [], []

                    names = (gap_p2c_name_h, gap_c2p_name_h, pause_c_name_h, pause_p_name_h,
                        turn_init_h_name, 

                        gap_p2c_name_r, gap_c2p_name_r, pause_c_name_r, pause_p_name_r,
                        turn_init_r_name)

                    onsets = (self.gap_p2c_onsets_h, self.gap_c2p_onsets_h, self.pause_c_onsets_h,
                        self.pause_p_onsets_h, 
                        self.turn_init_h_onsets,
                            
                        self.gap_p2c_onsets_r, self.gap_c2p_onsets_r, self.pause_c_onsets_r,
                        self.pause_p_onsets_r, 
                        self.turn_init_r_onsets)

                    durations = (self.gap_p2c_durs_h, self.gap_c2p_durs_h, self.pause_c_durs_h, 
                        self.pause_p_durs_h, 
                        self.turn_init_h_durs,
                           
                        self.gap_p2c_durs_r, self.gap_c2p_durs_r, self.pause_c_durs_r, 
                        self.pause_p_durs_r, self.turn_init_r_durs)
                    
                    ###----------PMODS----------###
                    if self.pmod == True:
                        self.gap_p2c_pmod_h, self.gap_c2p_pmod_h, self.pause_c_pmod_h, \
                            self.pause_p_pmod_h, self.turn_init_r_ul = [], [], [], [], []
                        
                        self.gap_p2c_pmod_r, self.gap_c2p_pmod_r, self.pause_c_pmod_r, \
                            self.pause_p_pmod_r, self.turn_init_r_ul = [], [], [], [], [] 
                        self.turn_init_r_tdl, self.turn_init_h_tdl = [], []

                        pmods = (self.gap_p2c_pmod_h, self.gap_c2p_pmod_h, self.pause_c_pmod_h, 
                            self.pause_p_pmod_h, self.turn_init_r_ul, self.turn_init_r_tdl, self.turn_init_h_tdl,
                           
                            self.gap_p2c_pmod_r, self.gap_c2p_pmod_r, self.pause_c_pmod_r, 
                            self.pause_p_pmod_r, self.turn_init_r_ul)
                    ###-------------------------###

                for conv in conversations:
                    for row in events_data:
                        onset = float(row[4])
                        duration = float(row[5])
                        n_words = row[8]

                        if row[0] == sub and row[2] == run and row[3] == conv: 
                            if conv in human_CONV1:
                                name_index = self.onsdurs_output[SubjRunID]['names'].index('CONV1')
                                conv_onset = float(self.onsdurs_output[SubjRunID]['onsets'][name_index][human_CONV1.index(conv)])
                                
                                if event_type == 'modality' and duration > 0.29: 
                                    tdl = row[10]
                                    if self.check_modality((row[6], row[7])) == 'comprehension':  
                                        if self.pmod == True:
                                            if tdl >= 4 and tdl <= 50:
                                                self.comp_h_ul.append(n_words)
                                                self.comp_h_tdl.append(tdl)
                                                self.comp_h_mtdl.append(tdl/n_words)
                                                self.comp_h_onsets.append(conv_onset + onset)
                                                self.comp_h_durs.append(duration)
                                            else: 
                                                self.comp_h_npmod_onsets.append(conv_onset + onset)
                                                self.comp_h_npmod_durs.append(duration)
                                        else: 
                                            self.comp_h_onsets.append(conv_onset + onset)
                                            self.comp_h_durs.append(duration)

                                    elif self.check_modality((row[6], row[7])) == 'production':
                                        if self.pmod == True:
                                            if tdl >= 4 and tdl <= 50:
                                                self.prod_h_ul.append(n_words)
                                                self.prod_h_tdl.append(tdl)
                                                self.prod_h_mtdl.append(tdl/n_words)
                                                self.prod_h_onsets.append(conv_onset + onset)
                                                self.prod_h_durs.append(duration)
                                            else: 
                                                self.prod_h_npmod_onsets.append(conv_onset + onset)
                                                self.prod_h_npmod_durs.append(duration)
                                        else: 
                                            self.prod_h_onsets.append(conv_onset + onset)
                                            self.prod_h_durs.append(duration)

                                elif event_type == 'transitions' and duration > 0.29: 
                                    trans_pmod = row[10]
                                    self.append_transition_parameters(row, onset, duration, conv_onset, 'human', SubjRunID, trans_pmod)

                            elif conv in robot_CONV2:
                                name_index = self.onsdurs_output[SubjRunID]['names'].index('CONV2')
                                conv_onset = float(self.onsdurs_output[SubjRunID]['onsets'][name_index][robot_CONV2.index(conv)])
                                
                                if event_type == 'modality' and duration > 0.29: 
                                    if self.check_modality((row[6], row[7])) == 'comprehension':  
                                        self.comp_r_onsets.append(conv_onset + onset)
                                        self.comp_r_durs.append(duration)

                                    elif self.check_modality((row[6], row[7])) == 'production':
                                        self.prod_r_onsets.append(conv_onset + onset)
                                        self.prod_r_durs.append(duration)

                                elif event_type == 'transitions' and duration > 0.29: 
                                    trans_pmod = row[10]
                                    self.append_transition_parameters(row, onset, duration, conv_onset, 'robot', SubjRunID, trans_pmod)
                
                if self.pmod == True: 
                    print(names)
                    for name, ons_list, dur_list, pmod_list in zip(names, onsets, durations, pmods):
                        self.append_name_onset_duration_pmod(SubjRunID, [name], ons_list, dur_list, pmod_list)

                else:
                    for name, ons_list, dur_list in zip(names, onsets, durations):
                        self.append_name_onset_duration(SubjRunID, [name], ons_list, dur_list)

    def append_transition_parameters(self, row, onset, duration, conv_onset, condition, SubjRunID, n_token):
        new_onset = float(conv_onset + onset)
        if condition == 'human':
            if self.check_transition(row) == 'GAP_p2c':
                self.gap_p2c_onsets_h.append(new_onset)
                self.gap_p2c_durs_h.append(duration)
                if self.pmod == True:
                    self.gap_p2c_pmod_h.append(0)

            elif self.check_transition(row) == 'GAP_c2p':
                prod_onset = new_onset + duration
                self.gap_c2p_onsets_h.append(new_onset)
                self.gap_c2p_durs_h.append(duration)
                if self.pmod == True:
                    self.gap_c2p_pmod_h.append(0)

                TI_onset = new_onset + duration - 0.6
                self.turn_init_h_onsets.append(TI_onset)
                self.turn_init_h_durs.append(0.6)
                if self.pmod == True:
                    self.turn_init_r_ul.append(n_token)

            elif self.check_transition(row) == 'PAUSE_p':
                self.pause_p_onsets_h.append(new_onset)
                self.pause_p_durs_h.append(duration)
                if self.pmod == True:
                    self.pause_p_pmod_h.append(0)
                
                ###-------Include turn continuations------###
                # TC_onset = new_onset + duration - 0.6
                # self.turn_cont_h_onsets.append(TC_onset)
                # self.turn_cont_h_durs.append(0.6)
                #-------------------------------------------#

            elif self.check_transition(row) == 'PAUSE_c':
                self.pause_c_onsets_h.append(new_onset)
                self.pause_c_durs_h.append(duration)
                if self.pmod == True:
                    self.pause_c_pmod_h.append(0)
            
            elif self.check_transition(row) == 'OVRL_c2p':
                TI_onset = new_onset - 0.6
                self.turn_init_h_onsets.append(TI_onset)
                self.turn_init_h_durs.append(0.6)
                if self.pmod == True:
                    self.turn_init_r_ul.append(n_token)

        elif condition == 'robot':
            if self.check_transition(row) == 'GAP_p2c':
                self.gap_p2c_onsets_r.append(new_onset)
                self.gap_p2c_durs_r.append(duration)
                if self.pmod == True:
                    self.gap_p2c_pmod_r.append(0)

            elif self.check_transition(row) == 'GAP_c2p':
                self.gap_c2p_onsets_r.append(new_onset)
                self.gap_c2p_durs_r.append(duration)
                if self.pmod == True:
                    self.gap_c2p_pmod_r.append(0)

                TI_onset = new_onset + duration - 0.6
                self.turn_init_r_onsets.append(TI_onset)
                self.turn_init_r_durs.append(0.6)
                if self.pmod == True:
                    self.turn_init_r_ul.append(n_token)

            elif self.check_transition(row) == 'PAUSE_p':
                self.pause_p_onsets_r.append(new_onset)
                self.pause_p_durs_r.append(duration)
                if self.pmod == True:
                    self.pause_p_pmod_r.append(0)

                ###-------Include turn continuations------###
                # TC_onset = new_onset + duration - 0.6
                # self.turn_cont_r_onsets.append(TC_onset)
                # self.turn_cont_r_durs.append(0.6)
                #-------------------------------------------#

            elif self.check_transition(row) == 'PAUSE_c':
                self.pause_c_onsets_r.append(new_onset)
                self.pause_c_durs_r.append(duration)
                if self.pmod == True:
                    self.pause_c_pmod_r.append(0)

            elif self.check_transition(row) == 'OVRL_c2p':
                TI_onset = new_onset - 0.6
                self.turn_init_r_onsets.append(TI_onset)
                self.turn_init_r_durs.append(0.6)
                if self.pmod == True:
                    self.turn_init_r_ul.append(n_token)

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
        self.onsdurs_output[subjrunid]['names'].append(n)#np.array(name, dtype=str))
        self.onsdurs_output[subjrunid]['onsets'].append(o)#np.array(onsets, dtype=float))
        self.onsdurs_output[subjrunid]['durations'].append(d)#np.array(durations, dtype=float))

    def append_name_onset_duration_pmod(self, subjrunid, n, o, d, p):
        self.onsdurs_output[subjrunid]['names'].append(n)#np.array(name, dtype=str))
        self.onsdurs_output[subjrunid]['onsets'].append(o)#np.array(onsets, dtype=float))
        self.onsdurs_output[subjrunid]['durations'].append(d)#np.array(durations, dtype=float))

        #This chunks adds the pmod and orth stats to the mat-files.

        if n in self.with_pmod:
            self.onsdurs_output[subjrunid]['pmod'][''.join(n)] = {}
            #wl is first list and tdl is second list in p
            pmods = ['wl', 'tdl', 'mtdl']
            for i, pmodname in enumerate(pmods):
                self.onsdurs_output[subjrunid]['pmod'][''.join(n)].setdefault(pmodname, p[i])

    def check_transition(self, l):
        previous_speaker = l[7]
        subsequent_speaker = l[8]
        typ = l[9]
        patterns = [['GAP_p2c', 'participant', 'researcher', 'silence'],
            ['GAP_c2p', 'researcher', 'participant', 'silence'],
            ['PAUSE_c', 'researcher', 'researcher', 'silence'],
            ['PAUSE_p', 'participant', 'participant', 'silence'],

            ['OVRL_p2c', 'participant', 'researcher', 'speech'],
            ['OVRL_c2p', 'researcher', 'participant', 'speech'],
            ['OVRL_wp', 'participant', 'participant', 'speech'],
            ['OVRL_wc', 'researcher', 'researcher', 'speech']]
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
            if self.pmod == True:
                pmods = self.onsdurs_output[subjrun]['pmod']
            for evnt  in old_events:
                evnt_indx = names.index(evnt)
                del names[evnt_indx]
                del onsets[evnt_indx]
                del durations[evnt_indx]
                # if self.pmod == True and evnt in self.with_pmod:
                #     del pmods[evnt_indx]

    def replicate_marseille(self):
        for subj in self.onsdurs_output:
            self.onsdurs_output[subj]['names'] = [name for name in self.onsdurs_output[subj]['names']]
        return self.onsdurs_output

    def crop_duration(self, onsdurs): #remove events less than 300 ms
        cropped_onsdurs = onsdurs

        for key in onsdurs:

            current_subj = onsdurs[key]
            for cat, name in enumerate(current_subj['names']):

            # save the indexes of all the elements in testing_list['durations'][0] that are greater than 0.3 in a new list
                indexes_to_keep = [i for i, x in enumerate(current_subj['durations'][cat]) if x > 0.29]
                cropped_onsdurs[key]['durations'][cat] = [current_subj['durations'][cat][i] for i in indexes_to_keep]
                cropped_onsdurs[key]['onsets'][cat] = [current_subj['onsets'][cat][i] for i in indexes_to_keep]
                
                if self.pmod == True and name in self.with_pmod:
                    for e, pname in enumerate(cropped_onsdurs[key]['pmod']):
                        if name == [pname]:
                            for l, pmodname in enumerate(cropped_onsdurs[key]['pmod'][pname]):
                                cropped_onsdurs[key]['pmod'][pname][pmodname] = [current_subj['pmod'][pname][pmodname][i] for i in indexes_to_keep]

        return cropped_onsdurs

    def check_if_pmod_code_works(self, d):
        '''Check if the goddamn pmod code worked after collapsing conditions'''
        wrong = set()
        for sub in d:
            for nameind, name in enumerate(d[sub]['names']):
                if self.pmod == True:
                    if len(d[sub]['onsets'][nameind]) == len(d[sub]['durations'][nameind]) == len(d[sub]['pmod'][nameind][0]):

                        continue
                    else: wrong.add(sub)
                else:
                    if len(d[sub]['onsets'][nameind]) == len(d[sub]['durations'][nameind]):
                        continue
                    else: wrong.add(sub)

        if len(wrong) == 0:
            print('\nEverything seems to work!\n')
        else: 
            print('Ooops, smth is wrong with ', len(wrong), ' subjruns: ', wrong)
    
    def set_pmod(self, logfiles):
        pmod = False
        print('Include Pmods? (y/n)')
        pmodinput = input()
        if pmodinput == 'y':
            pmod = True
            print("Pmods included")
            self.add_pmod(logfiles)
        else: print('Pmods excluded')
        return pmod

def model_600ms(self): 
        onsdurs_600ms = {}
        for run in self.final_output:
            # get onsets durations and name for each event
            onsets = [i for i in self.final_output[run]['onsets']]
            names = [i for i in self.final_output[run]['names']]
            durations = [i for i in self.final_output[run]['durations']]
            len_onsets = []
            for i in onsets:
                len_onsets.append(len(i))
            names_ext = []
            for ind,i in enumerate(names):
                names_ext.extend(repeat(i, len_onsets[ind]))
            #get onsets and endtimes sorted in time order
            onsets_flat = [x for xs in self.final_output[run]['onsets'] for x in xs]
            durations_flat = [x for xs in self.final_output[run]['durations'] for x in xs]
            end_times = [a + b for a, b in zip(onsets_flat, durations_flat)]
            onsets_endtimes = []
            onsets_endtimes.extend([list(a) for a in zip(onsets_flat, end_times, names_ext)])
            onsets_endtimes = sorted(onsets_endtimes, key=lambda x: x[0])
            onsets_endtimes
            #save only PROD_h nd PROD_r in a variable called prod_events
            prod_events = []
            for event in onsets_endtimes:
                for item in event:
                    if item == ['PROD_h'] or item == ['PROD_r']:
                        prod_events.append(event)
            #save only COMP_h and COMP_r in a variable called comp_events
            comp_events = []
            for event in onsets_endtimes:
                for item in event:
                    if item == ['COMP_h'] or item == ['COMP_r']:
                        comp_events.append(event)
            #if prod_events are longer than 600 ms, crop it to 600 ms and save as prod_events_cropped, and save the rest as prod_res. otherwise, extend it to 600 ms. check that each event in prod_res is > 0.3 sec. 
            prod_events_cropped = []
            prod_res = []
            for event in prod_events:
                if event[1] - event[0] > 0.6:
                    prod_events_cropped.append([event[0], event[0] + 0.6, event[2]])
                    if event[1] - (event[0] + 0.6) > 0.3:
                        prod_res.append([event[0] + 0.6, event[1], event[2]])
                else:
                    prod_events_cropped.append([event[0], event[0] + 0.6, event[2]])
            
            #if comp_events are longer than 600 ms, crop it to 600 ms and save as comp_events_cropped, and save the rest as comp_res. otherwise, extend it to 600 ms. check that each event in comp_res is > 0.3 sec. 
            comp_events_cropped = []
            comp_res = []
            for event in comp_events:
                if event[1] - event[0] > 0.6:
                    comp_events_cropped.append([event[0], event[0] + 0.6, event[2]])
                    if event[1] - (event[0] + 0.6) > 0.3:
                        comp_res.append([event[0] + 0.6, event[1], event[2]])
                else:
                    comp_events_cropped.append([event[0], event[0] + 0.6, event[2]])

            onsets_ISI = [i for i in onsets[0]]
            durations_ISI = [i for i in durations[0]]
            onsets_INSTR1 = [i for i in onsets[1]]
            durations_INSTR1 = [i for i in durations[1]]
            onsets_prod_h = [i[0] for i in prod_events_cropped if i[2] == ['PROD_h']]
            durations_prod_h = [i[1] - i[0] for i in prod_events_cropped if i[2] == ['PROD_h']]
            onsets_prod_r = [i[0] for i in prod_events_cropped if i[2] == ['PROD_r']]
            durations_prod_r = [i[1] - i[0] for i in prod_events_cropped if i[2] == ['PROD_r']]
            onsets_comp_h = [i[0] for i in comp_events_cropped if i[2] == ['COMP_h']]
            durations_comp_h = [i[1] - i[0] for i in comp_events_cropped if i[2] == ['COMP_h']]
            onsets_comp_r = [i[0] for i in comp_events_cropped if i[2] == ['COMP_r']]
            durations_comp_r = [i[1] - i[0] for i in comp_events_cropped if i[2] == ['COMP_r']]
            onsets_TI_h = [i for i in onsets[6]]
            durations_TI_h = [i for i in durations[6]]
            onsets_TI_r = [i for i in onsets[7]]
            durations_TI_r = [i for i in durations[7]]
            onsets_SILENCE_h = [i for i in onsets[8]]
            durations_SILENCE_h = [i for i in durations[8]]
            onsets_SILENCE_r = [i for i in onsets[9]]
            durations_SILENCE_r = [i for i in durations[9]]
            onsets_prod_h_res = [i[0] for i in prod_res if i[2] == ['PROD_h']]
            durations_prod_h_res = [i[1] - i[0] for i in prod_res if i[2] == ['PROD_h']]
            onsets_prod_r_res = [i[0] for i in prod_res if i[2] == ['PROD_r']]
            durations_prod_r_res = [i[1] - i[0] for i in prod_res if i[2] == ['PROD_r']]
            onsets_comp_h_res = [i[0] for i in comp_res if i[2] == ['COMP_h']]
            durations_comp_h_res = [i[1] - i[0] for i in comp_res if i[2] == ['COMP_h']]
            onsets_comp_r_res = [i[0] for i in comp_res if i[2] == ['COMP_r']]
            durations_comp_r_res = [i[1] - i[0] for i in comp_res if i[2] == ['COMP_r']]

            #combine prod_events_cropped, comp_events_cropped, TI_h, TI_h, SILENCE_h, SILENCE_r into the dictionary similar to onsdurs_to_crop
            onsdurs_600ms[run] = {'names': [], 'onsets': [], 'durations': []}
            names_600ms = self.final_output[run]['names']
            names_600ms.append(['PROD_h_res'])
            names_600ms.append(['PROD_r_res'])
            names_600ms.append(['COMP_h_res'])
            names_600ms.append(['COMP_r_res'])
            onsdurs_600ms[run]['names'] = names_600ms
            onsdurs_600ms[run]['onsets'].extend([onsets_ISI, onsets_INSTR1, onsets_comp_h, onsets_prod_h, onsets_comp_r, onsets_prod_r, onsets_TI_h, onsets_TI_r, onsets_SILENCE_h, onsets_SILENCE_r, onsets_prod_h_res, onsets_prod_r_res, onsets_comp_h_res, onsets_comp_r_res])
            onsdurs_600ms[run]['durations'].extend([durations_ISI, durations_INSTR1, durations_comp_h, durations_prod_h, durations_comp_r, durations_prod_r, durations_TI_h, durations_TI_r, durations_SILENCE_h, durations_SILENCE_r, durations_prod_h_res, durations_prod_r_res, durations_comp_h_res, durations_comp_r_res])
            
        return onsdurs_600ms