import pickle
import re
import gc

class NonOverlappingModel:

    def __init__(self):
        a_file = open("pickles/onsdurs_collapsed_cropped.pkl", "rb") #read the self.onsdurs file into a dictionary
        self.od_file = pickle.load(a_file)

        #--------Only run for one participant------------#
        onsdurs = {}
        onsdurs['subj-08_1'] = self.od_file['subj-08_1']
        ###--------------------------------------------###

        print('Sorting onsets and durations...')
        onsdurs_sorted = self.sort_onsdurs(onsdurs)
        del onsdurs
        gc.collect()

        print('Removing overlaps...')
        overlaps_removed, self.eventnames = self.remove_overlaps(onsdurs_sorted)
        del onsdurs_sorted
        gc.collect()

        print('Getting data ready for matlab format...')
        matlab_structure = self.get_matlab_structure(overlaps_removed)
        del overlaps_removed
        gc.collect()

        output_file = open('pickles/nonoverlapping_model.pkl', 'wb')
        pickle.dump(matlab_structure, output_file)
        output_file.close()
        print('Model with no overlaps have successfully been pickled!')

    def endtime(self, onset, duration):
        return onset + duration

    def split_runs(self, isi_times):
        '''Split runs into smaller chunks (conversations) in time'''
        chunks = []
        for i, conv_time in enumerate(isi_times):
            if i < len(isi_times) - 1:
                if isi_times[i+1] - conv_time > 50: # Check if the chunk is larger than 50 seconds, i.e., if the chunk contains a conversation.
                    chunks.append((conv_time, isi_times[i+1]))
        return chunks

    def sort_onsdurs(self, onsdurs):
        prioritized_order = ['^TI*', '^PROD*', '^COMP*', '^SILENCE*']
        onsdurs_sorted = {}
        for subj_run in onsdurs:
            conversations = {}
            names, ons, durs = onsdurs[subj_run].get('names'), onsdurs[subj_run].get('onsets'), onsdurs[subj_run].get('durations')
            conversation_times = self.split_runs(ons[names.index('ISI')])

            for e, conversation in enumerate(conversation_times):
                conversation_start, conversation_end = conversation[0], conversation[1]
                events = {}
                for event in prioritized_order:
                    for name in names:
                        if name == 'INSTR1' or name == 'ISI':
                            continue

                        else:
                            name = ''.join(name)
                            if re.compile(event).match(name): # Check if the current name is the prioritized event
                                event_times = [(o, self.endtime(o,d)) for o, d in zip(ons[names.index([name])], \
                                    durs[names.index([name])]) if conversation_start < o and \
                                        self.endtime(o,d) < conversation_end]
                                events[name] = event_times

                conversations.setdefault('CONV' + str(e + 1), events)
            onsdurs_sorted.setdefault(subj_run, conversations)
        return onsdurs_sorted

    def remove_overlaps(self, onsdurs_sorted):
        human_conversations = ['CONV1', 'CONV3', 'CONV5']
        robot_conversations = ['CONV2', 'CONV4', 'CONV6']

        for subjrun in onsdurs_sorted:
            print('Removing overlaps fron run: ', subjrun)
            for conv in onsdurs_sorted[subjrun].keys():

                events = list(onsdurs_sorted[subjrun][conv].keys())

                for current_event_index, event in enumerate(events):
                    # Only check overlaps for events in the current condition:
                    if (event.endswith('r') and conv in human_conversations) or\
                        (event.endswith('h') and conv in robot_conversations):
                        continue

                    less_prioritized_events = events[current_event_index +1:]

                    for lp_event in less_prioritized_events:
                        # Only check overlaps for less prioritized events that match the event's condition
                        if event[-1] != lp_event[-1]:
                            continue

                        print('Checking if ', event, ' overlaps with ', lp_event, 'in run: ', subjrun, ' conversation: ', conv, '...')
 
                        for event_time in onsdurs_sorted[subjrun][conv][event]:
                            event_start, event_end = event_time[0], event_time[1]

                            new_lp_times = []

                            for lp_event_time in onsdurs_sorted[subjrun][conv][lp_event]:
                                lp_event_start, lp_event_end = lp_event_time[0], lp_event_time[1]
                                if lp_event_end - lp_event_start > 0.3: # Only include events > 300 ms:

                                
                                    if (lp_event_end < event_start) or (event_end < lp_event_start): # If the events do not overlap
                                            new_lp_times.append(lp_event_time)

                                    else: 
                                        new_times = self.check_overlap(event_start, event_end, lp_event_start, lp_event_end)
                                        for new_time in new_times:
                                            if new_time[1] - new_time[0] > 0.3:
                                                new_lp_times.append(new_time)
            
                            onsdurs_sorted[subjrun][conv][lp_event] = new_lp_times       
        return onsdurs_sorted, events

    def check_overlap(self, e_start, e_end, lpe_start, lpe_end):
        '''Removes overlaps of less prioritized events and create new 
        that do not overlap with the prioritized event'''
        if e_start <= lpe_start <= e_end and e_end <= lpe_end:
            print('the less prioritized event overlaps with the right side of the prioritized event')
            print('overlaps with ', e_end - lpe_start, ' seconds')
            return [(e_end, lpe_end)]
        elif lpe_start <= e_start <= lpe_end and lpe_end <= e_end:
            print('the less prioritized event overlaps with the left side of the prioritized event')
            print('overlaps with ', lpe_end - e_start, ' seconds')
            return [(lpe_start, e_start)]
        elif e_start <= lpe_start and lpe_end <= e_end:
            print('the less prioritized event is fully within the prioritized event')
            return []
        elif lpe_start <= e_start and e_end <= lpe_end:
            print('the prioritized event is fully within the less prioritized event')
            return [(lpe_start, e_start), (e_end, lpe_end)]
        else:
            print('lp event: ', lpe_start, lpe_end, ' event: ', e_start, e_end)
            return [(lpe_start, lpe_end)]

    def get_matlab_structure(self, overlaps_removed):
        non_overlapping_model = {}

        for subjrun in overlaps_removed:
            run = {}

            #----Add the INSTR and ISI conditions first----#
            run['names'], all_run_onsets, all_run_durations = self.get_missing_conditions(subjrun)
            #----------------------------------------------#

            for name in self.eventnames:
                run['names'].append([name])
                'Added names to the new model'

                onsets = [time[0] for conv in overlaps_removed[subjrun] \
                        for time in overlaps_removed[subjrun][conv][name]]
                all_run_onsets.append(onsets)
                'Added onsets to the new model'
                        
                durations = [time[1] - time[0] for conv in overlaps_removed[subjrun] \
                    for time in overlaps_removed[subjrun][conv][name]] # Time[0] is event starttime and time[1] is event endtime
                all_run_durations.append(durations)
                'Added durations to the new model'
        
            run['onsets'] = all_run_onsets
            run['durations'] = all_run_durations

            non_overlapping_model[subjrun] = run
        return non_overlapping_model
        
    def get_missing_conditions(self, subjrun): # Missing conditions will be ISI and INSTR in this case
        print('Inside get_missing_conditions')
        missing_names, missing_onsets, missing_durations = ['ISI', 'INSTR1'], [], []

        for name in missing_names:
            missing_onsets.append(self.od_file[subjrun]['onsets'][self.od_file[subjrun]['names'].index(name)])
            missing_durations.append(self.od_file[subjrun]['durations'][self.od_file[subjrun]['names'].index(name)])

        return missing_names, missing_onsets, missing_durations

m = NonOverlappingModel()