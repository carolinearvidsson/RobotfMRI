from scipy.io import savemat
import sys
from onset_and_durations import OnsetsDurations

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output #check what is saved
    for run in mdic:

        filename = 'matfiles/onset_and_durations_ovrl_' + run[0:3] + '-' + run[5:7] + '_' + 'run' + run[-1] + '.mat'
        savemat(filename, mdic[run])

        #python3 main.py resampled/