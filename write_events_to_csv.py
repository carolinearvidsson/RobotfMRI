from math import prod
from scipy.io import savemat
import sys
from onset_and_durations import OnsetsDurations
import csv

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output