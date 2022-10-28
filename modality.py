
class Modality:
    def __init__(self, conversation):
        self.modality_data = [] # list where each element represents a production/comprehension segment, with following structure: [start time, duration, production (1 if yes), comprehension (1 if yes)]
        participant_production = [segment for segment in conversation if segment[4] == 'participant' \
            if segment[2] != '#' if segment[2] != '***']
        participant_comprehension = [segment for segment in conversation if segment[4] == 'researcher' \
            if segment[2] != '#' if segment[2] != '***']
        confederate_speech = [segment for segment in conversation \
            if segment[4] == 'researcher' and segment[2] != '#']
        confederate_silence = [segment for segment in conversation \
            if segment[4] == 'researcher' and segment[2] == '#']

        comprehension = self.get_simultaneous(participant_comprehension, confederate_speech, 'comp')
        production = self.get_simultaneous(participant_production, confederate_silence, 'prod')
        self.modality_data = comprehension + production
    
    def get_simultaneous(self, vocal_tier_a, vocal_tier_b, modality): #Takes two lists with utterances from respective speakers\
        # and computes the duration of overlaps of utterances if there are any. Output is a list where each section has the following structure:
        # duration, production (1 if yes), comprehension (1 if yes), pmod (n words in utterance).
        simultaneous = []
        if modality == 'comp':
            comp = 1
        else: comp = 0
        if modality == 'prod':
            prod = 1
        else: prod = 0

        for utterance in vocal_tier_a:
            utter_starttime = utterance[0]
            utter_endtime = utterance[1]
            duration = utter_endtime - utter_starttime
            pmod = self.pmod(utterance)
            simultaneous.append([utter_starttime, duration, prod, comp, pmod])
            #----------- If overlaps are not to be ignored:
            # for segm in vocal_tier_b:
            #     seg_starttime = segm[0]
            #     silence_endtime = segm[1]
            #     if utter_starttime < seg_starttime < utter_endtime or \
            #         utter_starttime < silence_endtime < utter_endtime or \
            #             utter_starttime < seg_starttime and utter_endtime > silence_endtime or \
            #                 utter_starttime > seg_starttime and utter_endtime < silence_endtime:
            #         latest_starttime = max(utter_starttime, seg_starttime)
            #         earliest_endtime = min (utter_endtime, silence_endtime)

            #         duration = earliest_endtime - latest_starttime
            #         #print(latest_starttime, earliest_endtime, duration)
            #         simultaneous.append([latest_starttime, duration, prod, comp])

        return simultaneous
    
    def pmod(self, utterance):
        return len(utterance[2].replace("'", " ").split(" "))
