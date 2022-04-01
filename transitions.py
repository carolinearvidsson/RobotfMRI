class Transitions:
    def __init__(self, conversation):
        self.transitions_data = [] # list where each element represents a silence or speech overlap, with following structure: [start time, duration, condition, within speaker, speaker of the prior turn, speaker of the subsequent turn]
        speaker_pauses = [pause for pause in conversation if pause[2] == '#']
        silences = self.get_segment_overlap(speaker_pauses, 'silence')
        speech = [overl for overl in conversation if overl[2][0].isalnum()]
        
        #---------- Commented out to ignore overlaps:
        #speech_overlaps = self.get_segment_overlap(speech, 'speech')

        #self.get_segment_overlap_type([silences, speech_overlaps], conversation)
        self.get_segment_overlap_type([silences], conversation)

        
    def get_segment_overlap(self, segments, s_type):  
        segm_overl = [] 
        segments_copy = segments
        for pause in segments:
            pause_starttime = pause[0]
            pause_endtime = pause[1]
            for s in segments_copy:
                copy_starttime = s[0]
                copy_endtime = s[1]
                if pause_starttime < copy_starttime < pause_endtime or \
                    pause_starttime < copy_endtime < pause_endtime or \
                        pause_starttime < copy_starttime and pause_endtime > copy_endtime or \
                            pause_starttime > copy_starttime and pause_endtime < copy_endtime:
                    latest_starttime = max(pause_starttime, copy_starttime)
                    earliest_endtime = min (pause_endtime, copy_endtime)
                    duration = earliest_endtime - latest_starttime
                    o = [latest_starttime, earliest_endtime, duration, s_type]
                    if o not in segm_overl:
                        segm_overl.append(o)
        return segm_overl

    def get_segment_overlap_type(self, segm_overlaps, convers):
        #Segm_overlaps is a list with 2 elements: overlapping speech and overlapping silences
        for segm_type in segm_overlaps:
            for segm in segm_type:
                duration = segm[2]
                s_type = segm[3]
                surrounding_utterances = [] # List with two elements. \
                                            #First element is the preceding turn \
                                            # and second element is the subsequent turn
                starttime, endtime = segm[0], segm[1]
                convers = [utterance for utterance in convers if utterance[2] != '#' or utterance[2] != '***']
                for utterance in convers:
                    utterance_starttime = utterance[0]
                    utterance_endtime = utterance[1]
                    if s_type == 'silence':
                        if starttime == utterance_endtime:
                            surrounding_utterances.append(utterance)
                        if endtime == utterance_starttime:
                            surrounding_utterances.append(utterance)
                    elif s_type == 'speech':
                        if starttime == utterance_starttime:
                            surrounding_utterances.append(utterance)
                        if endtime == utterance_endtime:
                            surrounding_utterances.append(utterance)
                within_speaker = 0
                speaker_first_turn = 'n/a'
                speaker_second_turn = 'n/a'
                try:
                    speaker_first_turn = surrounding_utterances[0][4]
                    speaker_second_turn = surrounding_utterances[1][4]
                    if speaker_first_turn == speaker_second_turn:
                        within_speaker = 1
                except: continue
                
                self.transitions_data.append([starttime, duration, within_speaker, speaker_first_turn, speaker_second_turn, s_type])
