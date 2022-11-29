from scipy.io import savemat
import sys
from giglio_replication_onsdur import OnsetsDurations
import csv

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output #check what is saved
    for run in mdic:
        filename = 'matfiles/giglio_onset_and_durations_ovrl_' + run[0:3] + '-' + run[5:7] + '_' + 'run' + run[-1] + '.mat'
        savemat(filename, mdic[run])

        #python3 giglio_replication_main.py ~/Desktop/Dissertation/RobotfMRI/Resampled/