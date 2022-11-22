from math import prod
from scipy.io import savemat
import sys
from onset_and_durations import OnsetsDurations
import csv

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output

    for run in mdic:
        for name in mdic[run]['names']:
            onsets = mdic[run]['onsets'][mdic[run]['names'].index(name)]
            durations = mdic[run]['durations'][mdic[run]['names'].index(name)]
            n_words = onsets = mdic[run]['onsets'][mdic[run]['names'].index(name)]

            
#python3 write_events_to_csv.py [sökväg till katalog]

