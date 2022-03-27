import textgrid 
from operator import itemgetter
from modality import Modality
from transitions import Transitions

class Conversations:
            
        def __init__(self, datastr, path):  
            self.transitions_data = []
            self.modality = []

            self.get_conversation(datastr, path)

        def get_conversation(self, datastr, path):
            for participant in datastr:
                print(participant)
                for session in datastr[participant]:
                    print(session)
                    for convers in datastr[participant][session]:
                        condition = self.check_condition(convers)
                        grids_merged = []
                        for tgfilename in datastr[participant][session][convers]:
                            speaker = self.check_tier(tgfilename.split('_')[4][0] == 'p')
                            tgo = textgrid.TextGrid.fromFile(path + tgfilename)
                            for intervals in tgo:
                                for interval in intervals:
                                    grids_merged.append(self.get_utterance(interval, condition, speaker))

                        grids_merged = sorted(grids_merged, key=itemgetter(0)) # A sorted list with all utterances during a conversation\
                                                                                    # each utterance is a tuple: (min_time, max_time, \
                                                                                        # transcription, condition, speaker)
                        
                        
                        for transition in Transitions(grids_merged).transitions_data:
                            transitions_datarows = [participant, condition, session, convers] + transition
                            #print(transitions_datarows)
                            self.transitions_data.append(transitions_datarows)
                            
                        for mod_data_row in Modality(grids_merged).modality_data:
                            modality_datarow = [participant, condition, session, convers] + mod_data_row
                            self.modality.append(modality_datarow)
                            #print(transitions_datarows)
    
                        

        def get_utterance(self, inter, human, speaker): 
            utterance = (inter.minTime, inter.maxTime, inter.mark, human, speaker)
            return utterance

        def check_condition(self, conversant):
            human = ["1", "3", "5"]
            if conversant in human:
                return "human"
            else: return "robot"

        def check_tier(self, bool):
            tier = "participant"
            if bool == False:
                tier = "researcher"
            return tier