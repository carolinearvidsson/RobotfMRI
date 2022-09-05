import pickle
import re

class NonOverlappingModel:

    def __init__(self):
        a_file = open("onsdurs_collapsed_cropped.pkl", "rb") #read the self.onsdurs file into a dictionary
        self.onsdurs = pickle.load(a_file)
        
        print('Sorting onsets and durations...')
        onsdurs_sorted = self.prioritize_events(self.onsdurs)

        print('Removing overlaps...')
        overlaps_removed = self.remove_overlaps(onsdurs_sorted)

        print('Getting data ready for matlab format...')
        matlab_structure = self.get_matlab_structure(overlaps_removed)
        
        a_file = open("onsdurs_collapsed_cropped_noovrl.pkl", "wb")
        pickle.dump(matlab_structure, a_file)
        a_file.close()
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

    def prioritize_events(self, onsdurs):
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
                        if name == 'INSTR' or name == 'ISI':
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
        for subjrun in onsdurs_sorted:
            print('Removing overlaps fron run: ', subjrun)
            for conv in onsdurs_sorted[subjrun].keys():

                events = list(onsdurs_sorted[subjrun][conv].keys())
                print(events)

                for current_event_index, event in enumerate(events):
                    less_prioritized_events = events[current_event_index +1:]

                    for lp_event in less_prioritized_events:
                        if event[-1] != lp_event[-1]:
                            continue

                        print('Checking if ', event, ' overlaps with ', lp_event, 'in run: ', subjrun, ' conversation: ', conv, '...')
                        new_lp_times = []
                        seen = 0
                        new_seen = 0

                        if lp_event[-1] != event[-1]:

                            continue
 
                        for event_time in onsdurs_sorted[subjrun][conv][event]:
                            event_start, event_end = event_time[0], event_time[1]

                            for lp_event_time in onsdurs_sorted[subjrun][conv][lp_event]:
                                lp_event_start, lp_event_end = lp_event_time[0], lp_event_time[1]
                                
                                if new_seen > 0 and seen == new_seen:
                                    new_lp_times.append(lp_event_time)

                                else: 
                                    new_times, new_seen = self.check_overlap(event_start, event_end, lp_event_start, lp_event_end)
                                    seen += new_seen
                                    for new_time in new_times:
                                        new_lp_times.append(new_time)
            
                        onsdurs_sorted[subjrun][conv][lp_event] = new_lp_times       
        return onsdurs_sorted

    def check_overlap(self, e_start, e_end, lpe_start, lpe_end):
        '''Removes overlaps of less prioritized events and create new 
        that do not overlap with the prioritized event'''
        if e_start < lpe_start < e_end and e_end < lpe_end:
            print('the less prioritized event overlaps with the right side of the prioritized event')
            print('overlaps with ', e_end - lpe_start, ' seconds')
            return [(e_end, lpe_end)], 1
        elif lpe_start < e_start < lpe_end and lpe_end < e_end:
            print('the less prioritized event overlaps with the left side of the prioritized event')
            print('overlaps with ', lpe_end - e_end, ' seconds')
            return [(lpe_start, e_start)], 1
        elif (e_start < lpe_start or e_start == lpe_start) and (lpe_end < e_end or lpe_end == e_end):
            print('the less prioritized event is fully within the prioritized event')
            return [], 1
        elif lpe_start < e_start and e_end < lpe_end:
            print('the prioritized event is fully within the less prioritized event')
            return [(lpe_start, e_start), (e_end, lpe_end)], 1
        else:
            #print('no overlap')
            #print('...')
            return [(lpe_start, lpe_end)], 0

    def get_matlab_structure(self, overlaps_removed):
        non_overlapping_model = {}

        for subjrun in overlaps_removed:
            run = {}

            eventnames = sorted(list(set([event for conv in overlaps_removed[subjrun] \
                for event in overlaps_removed[subjrun][conv]])))

            missing_names, missing_onsets, missing_durations = self.get_missing_conditions(subjrun, eventnames)
            run['names'] = missing_names
            for name in eventnames:
                run['names'].append([name])

            all_run_onsets = missing_onsets
            all_run_durations = missing_durations

            for name in eventnames:
                onsets = [time[0] for conv in overlaps_removed[subjrun] \
                        for time in overlaps_removed[subjrun][conv][name]]
                
                all_run_onsets.append(onsets)
                        
            
                durations = [time[1] - time[0] for conv in overlaps_removed[subjrun] \
                    for time in overlaps_removed[subjrun][conv][name]] #time[0] is event starttime and time[1] is event endtime
                all_run_durations.append(durations)
        
            run['onsets'] = all_run_onsets
            run['durations'] = all_run_durations

            non_overlapping_model[subjrun] = run
        return non_overlapping_model
        
    def get_missing_conditions(self, subjrun, eventnames): # missing conditions will probably just be ISI and INSTR
        missing_names, missing_onsets, missing_durations = [], [], []
        for name in self.onsdurs[subjrun]['names']:

            try: name = ''.join(name)
            except TypeError: continue

            if name not in eventnames:
                missing_names.append(name)
                missing_onsets.append(self.onsdurs[subjrun]['onsets'][self.onsdurs[subjrun]['names'].index(name)])
                missing_durations.append(self.onsdurs[subjrun]['durations'][self.onsdurs[subjrun]['names'].index(name)])

        return missing_names, missing_onsets, missing_durations

m = NonOverlappingModel()