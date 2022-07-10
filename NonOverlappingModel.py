import pickle
import re

class NonOverlappingModel:

    def __init__(self):

        a_file = open("onsdurs_collapsed_cropped.pkl", "rb") #read the onsdurs file into a dictionary
        onsdurs = pickle.load(a_file)
        onsdurs_sorted = self.get_event_times_in_prioritized_order(onsdurs)
        self.prioritize_events(onsdurs_sorted)

    def endtime(self, onset, duration):
        return onset + duration

    def get_event_times_in_prioritized_order(self, onsdurs):
        prioritized_order = ['^TI*', '^PROD*', '^COMP*', '^SILENCE*']
        onsdurs_sorted = {}
        for subj_run in onsdurs:
            events = {}
            names, ons, durs = onsdurs[subj_run].get('names'), onsdurs[subj_run].get('onsets'), onsdurs[subj_run].get('durations')
            for event in prioritized_order:
                for name in names:
                    
                    if name == 'INSTR' or name == 'ISI':
                        continue
                    else:
                        name = ''.join(name)
                        if re.compile(event).match(name): # Check if the current name is the prioritized event
                        #for o, d in zip(ons[names.index([name])], durs[names.index([name])]):
                            event_times = [(o, self.endtime(o,d)) for o, d in zip(ons[names.index([name])], durs[names.index([name])])]
                            events[name] = event_times
            onsdurs_sorted.setdefault(subj_run, events)
        return onsdurs_sorted

    def prioritize_events(self, onsdurs_sorted):
        for subjrun in onsdurs_sorted:
            events = list(onsdurs_sorted[subjrun].keys())
            for current_event_index, event in enumerate(events):
                less_prioritized_events = events[current_event_index +1:]
                if len(less_prioritized_events) > 0:
                    print(less_prioritized_events, event)
                    for event_times in onsdurs_sorted[subjrun][event]:
                        event_start, event_end = event_times[0], event_times[1]
                        for lp_event in less_prioritized_events:
                            for lp_event_times in onsdurs_sorted[subjrun][lp_event]:
                                lp_event_start, lp_event_end = lp_event_times[0], lp_event_times[1]
                                self.remove_overlap(event_start, event_end, lp_event_start, lp_event_end)


    def remove_overlap(self, e_start, e_end, lpe_start, lpe_end):
        '''Removes overlaps of less prioritized events and create new 
        that do not overlap with the prioritized event'''
        if e_start < lpe_start < e_end and e_end < lpe_end:
            print('event ', e_start, e_end)
            print('lp event ', lpe_start, lpe_end)
            print([(e_end, lpe_end)])
            return [(e_end, lpe_end)]
        elif lpe_start < e_start < lpe_end and lpe_end < e_end:
            print('event ', e_start, e_end)
            print('lp event ', lpe_start, lpe_end)
            print([(lpe_start, e_start)])
            return [(lpe_start, e_start)]
        elif e_start < lpe_start and lpe_end < e_end:
            print('event ', e_start, e_end)
            print('lp event ', lpe_start, lpe_end)
            print([])
            return []
        elif lpe_start < e_start and e_end < lpe_end:
            print('event ', e_start, e_end)
            print('lp event ', lpe_start, lpe_end)
            print([(lpe_start, e_start), (e_end, lpe_end)])
            return [(lpe_start, e_start), (e_end, lpe_end)]



m = NonOverlappingModel()