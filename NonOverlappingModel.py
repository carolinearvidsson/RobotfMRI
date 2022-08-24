import pickle
import re

class NonOverlappingModel:

    def __init__(self):
        a_file = open("onsdurs_collapsed_cropped.pkl", "rb") #read the onsdurs file into a dictionary
        onsdurs = pickle.load(a_file)
        
        print('Sorting onsets and durations...')
        onsdurs_sorted = self.prioritize_events(onsdurs)

        print('Removing overlaps...')
        overlaps_removed = self.remove_overlaps(onsdurs_sorted)

        print('Getting data ready for matlab format...')
        #matlab_structure = self.get_matlab_structure(overlaps_removed)

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
                                event_times = [(o, self.endtime(o,d)) for o, d in zip(ons[names.index([name])], durs[names.index([name])]) if conversation_start < o and self.endtime(o,d) < conversation_end]
                                events[name] = event_times

                conversations.setdefault('CONV' + str(e + 1), events)
            onsdurs_sorted.setdefault(subj_run, conversations)
        return onsdurs_sorted

    def remove_overlaps(self, onsdurs_sorted):
        for subjrun in onsdurs_sorted:
            print('')
            print('run:', subjrun)
            for conv in onsdurs_sorted[subjrun].keys():
                print('conv:', conv)
                events = list(onsdurs_sorted[subjrun][conv].keys())
                print('events:', events)
                for current_event_index, event in enumerate(events):
                    print('current event:', event)
                    less_prioritized_events = events[current_event_index +1:]
                    print('less prioritized events:', less_prioritized_events)
                    print('event times', onsdurs_sorted[subjrun][conv][event])

                    for lp_event in less_prioritized_events:
                        print('less prioritized event:', lp_event)
                        print('less prioritized event times:', onsdurs_sorted[subjrun][conv][lp_event])
                        new_lp_times = []

                        for event_times in onsdurs_sorted[subjrun][conv][event]:
                            event_start, event_end = event_times[0], event_times[1]

                            for lp_event_times in onsdurs_sorted[subjrun][conv][lp_event]:
                                lp_event_start, lp_event_end = lp_event_times[0], lp_event_times[1]

                                for new_event in self.check_overlap(event_start, event_end, lp_event_start, lp_event_end):
                                    new_lp_times.append(new_event)
            
                        onsdurs_sorted[subjrun][conv][lp_event] = new_lp_times

        return onsdurs_sorted

    def check_overlap(self, e_start, e_end, lpe_start, lpe_end):
        '''Removes overlaps of less prioritized events and create new 
        that do not overlap with the prioritized event'''
        if e_start < lpe_start < e_end and e_end < lpe_end:
            # print('the less prioritized event overlaps with the right side of the prioritized event')
            return [(e_end, lpe_end)]
        elif lpe_start < e_start < lpe_end and lpe_end < e_end:
            # print('the less prioritized event overlaps with the left side of the prioritized event')
            return [(lpe_start, e_start)]
        elif e_start < lpe_start and lpe_end < e_end or e_start == lpe_start and lpe_end == e_end:
            # print('the less prioritized event is fully within the prioritized event')
            return []
        elif lpe_start < e_start and e_end < lpe_end:
            # print('the prioritized event is fully within the less prioritized event')
            return [(lpe_start, e_start), (e_end, lpe_end)]
        else:
            # print('no overlap')
            # print('...')
            return [(lpe_start, lpe_end)]

    def get_matlab_structure(overlaps_removed):
        non_overlapping_model = []
        for subjrun in overlaps_removed:
            run = []
            # for conv in overlaps_removed[subjrun]

            events = list(overlaps_removed[subjrun].keys())

m = NonOverlappingModel()