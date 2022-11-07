import textgrid 
from operator import itemgetter
from modality import Modality
from transitions import Transitions
import csv

class Conversations:
            
        def __init__(self, datastr, path):  
            self.transitions_data = []
            self.modality = []

            self.get_conversation(datastr, path)

        def get_conversation(self, datastr, path):
            for participant in datastr:
                for session in datastr[participant]:
                    for convers in datastr[participant][session]:
                        condition = self.check_condition(convers)
                        grids_merged = []
                        for tgfilename in datastr[participant][session][convers]:
                            speaker = self.check_tier(tgfilename.split('_')[4][0] == 'p')
                            tgo = textgrid.TextGrid.fromFile(path + tgfilename)
                            for intervals in tgo:
                                for interval in intervals:
                                    grids_merged.append(self.get_utterance(interval, condition, speaker))
                                    
                                    #HÄR ÄR LITE INFO SOM KAN VARA ANVÄNDBAR FÖR JOHANNA
                                    print(participant, session, interval, condition, speaker)

                        grids_merged = sorted(grids_merged, key=itemgetter(0)) # A sorted list with all utterances during a conversation\
                                                                                    # each utterance is a tuple: (min_time, max_time, \ 
                                                                                    # # transcription, condition, speaker)

                        grids_merged = self.trim(grids_merged) #remove short IPUs

                        for transition in Transitions(grids_merged).transitions_data:
                            transitions_datarows = [participant, condition, session, convers] + transition
                            #print(transitions_datarows)
                            self.transitions_data.append(transitions_datarows)
                                            
                        for mod_data_row in Modality(grids_merged).modality_data:
                            modality_datarow = [participant, condition, session, convers] + mod_data_row
                            self.modality.append(modality_datarow)


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

        def trim(self, gridfile): #function to remove short IPUs
            pauses = []
            utterances = []
            for i in gridfile:
                if '#' in i[2]:
                    pauses.append(i)
                else:
                    utterances.append(i)
            utterances = [list(x) for x in utterances]
            pauses = [list(x) for x in pauses]
            #####remove short IPUs####
            for ind_p,pause in enumerate(pauses): 
                for ind_u,utterance in enumerate(utterances): 
                    if float(pause[1]) - float(pause[0]) < 0.3: #if a pause is < 300 ms
                        if utterance[0] == pause[1] and utterances[ind_u-1][4] == utterances[ind_u][4]: #find the utterance with start time = this pause's end time and check that speaker is the same in this and previous utterance
                            utterances[ind_u-1][2] += utterances[ind_u][2] # add the content of the later utterance to the previous utterance
                            utterances[ind_u-1][1] = utterances[ind_u][1]  # change the end time of the previous utterance to the next utterance's end time
                            del utterances[ind_u] #remove the second utterance
                            del pauses[ind_p] #remove the pause 
            #combine them back
            pauses = [tuple(x) for x in pauses]
            utterances =[tuple(x) for x in utterances]
            gridfile = pauses+utterances
            gridfile = sorted(gridfile, key=itemgetter(0))
            return gridfile
