from scipy.io import savemat
import sys
from onset_and_durations import OnsetsDurations

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output
    for run in mdic:
        # if run == 'subj-17_1':
        #     print(run)
        #     for cat in mdic[run]:
        #         print(cat)
        #         print(mdic[run][cat])
        #filename = 'marseille_onsdurs_' + run[0:3] + '-' + run[5:7] + '_' + 'run' + run[-1] + '.mat'
        filename = 'onset_and_durations_' + run[0:3] + '-' + run[5:7] + '_' + 'run' + run[-1] + '.mat'
        savemat(filename, mdic[run])

        #python3 write_NamesOnsetDurations_to_m.py ~/Desktop/MasterYearOne/VT22/Thesis/Data/Resampled/