from scipy.io import savemat
import sys
from onset_and_durations import OnsetsDurations
import csv

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output #check what is saved
    for run in mdic:
        filename = 'matfiles/onset_and_durations_ovrl_' + run[0:3] + '-' + run[5:7] + '_' + 'run' + run[-1] + '.mat'
        savemat(filename, mdic[run])


        csvf = open('csvfiles/eventlines', 'w')
        for name, ons, dur, pmod in zip(mdic[run]['names'], mdic[run]['onsets'], mdic[run]['durations'], mdic[run]['pmods']):
            for o, d, p in zip(ons, dur, pmod):
                print('\n\n', name, o, d, p, '\n\n')
                



        #python3 main.py ~/Desktop/Master/VT22/Thesis/Data/Resampled/