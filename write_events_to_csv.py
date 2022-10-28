from math import prod
from scipy.io import savemat
import sys
from onset_and_durations import OnsetsDurations
import csv

if __name__== '__main__':
    mdic = OnsetsDurations(sys.argv[1]).final_output #check what is saved
    ti_dur = 0.6
    prod_human, prod_robot = ['PROD_h'], ['PROD_r']
    ti_human, ti_robot = ['TI_h'], ['TI_r']

    for run in mdic:
        prodhumanlist = []
        tihumanlist = []

        # prodhumanlist = [[name, o, d, p] for name, ons, dur, pmod in zip(mdic[run]['names'], mdic[run]['onsets'], mdic[run]['durations'], mdic[run]['pmods'])\
        #     for o, d, p in zip(ons, dur, pmod) if name == prod_human]

        # prodrobotlist = [[name, o, d, p] for name, ons, dur, pmod in zip(mdic[run]['names'], mdic[run]['onsets'], mdic[run]['durations'], mdic[run]['pmods'])\
        #     for o, d, p in zip(ons, dur, pmod) if name == prod_robot]

        # tihumanlist = [[name, o, d, p] for name, ons, dur, pmod in zip(mdic[run]['names'], mdic[run]['onsets'], mdic[run]['durations'], mdic[run]['pmods'])\
        #     for o, d, p in zip(ons, dur, pmod) if name == ti_human]

        # tirobotlist = [[name, o, d, p] for name, ons, dur, pmod in zip(mdic[run]['names'], mdic[run]['onsets'], mdic[run]['durations'], mdic[run]['pmods'])\
        #     for o, d, p in zip(ons, dur, pmod) if name == ti_robot]

        # for prodhumanevent in prodhumanlist:
        #     print(prodhumanevent)
        #     for i, tihumanevent in enumerate(tihumanlist):
        #         starttime_ind = 1
        #         duration_ind = 2
        #         if prodhumanevent[starttime_ind] == tihumanevent[starttime_ind] + tihumanevent[duration_ind]:
        #             print(mdic[run]['pmods'][mdic[run]['names'].index(ti_human)][i])
        #             mdic[run]['pmods'][mdic[run]['names'].index(ti_human)][i] == prodhumanevent[3]
        #             print(mdic[run]['pmods'][mdic[run]['names'].index(ti_human)][i])

        csvf = open('csvfiles/eventlines.csv', 'w')
        writer = csv.writer(csvf)

        for name, ons, dur, pmod in zip(mdic[run]['names'], mdic[run]['onsets'], mdic[run]['durations'], mdic[run]['pmods']):
            for o, d, p in zip(ons, dur, pmod):
                if name == prod_human:
                    prodhumanlist.append([run, name, o, d, p])
        
        for name, ons, dur, pmod in zip(mdic[run]['names'], mdic[run]['onsets'], mdic[run]['durations'], mdic[run]['pmods']):
            i = 0
            for o, d, p in zip(ons, dur, pmod):
                if name == ti_human:
                    for prodevent in prodhumanlist:
                        prod_starttime = prodevent[2]
                        prod_pmod = prodevent[-1]
                        if o + ti_dur == prod_starttime:
                            mdic[run]['pmods'][mdic[run]['names'].index(name)][i] = prod_pmod
                i += 1

                #writer.writerow([run, name, o, d, p])

#python3 write_events_to_csv.py ~/Desktop/Master/VT22/Thesis/Data/Resampled/