from math import prod
from scipy.io import savemat
import sys
from onset_and_durations import OnsetsDurations
import csv

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output

#python3 write_events_to_csv.py [sökväg till katalog]

