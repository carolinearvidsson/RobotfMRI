import pysrt
from pydub import AudioSegment, silence
import pandas as pd
import os

os.chdir("C:/Users/k1230")

#######################
### chop audio file ###
#######################

#get each audio file
triggers = AudioSegment.from_wav("pilot20231117-trigger-3.wav")
participant = AudioSegment.from_wav("pilot20231117-Participant-2.wav")
operator = AudioSegment.from_wav("pilot20231117-Operator-1.wav")

#read log files
log_run00 = pd.read_csv('pilot-04_run-00.log', sep='\t', engine='python', header=None)
log_run01 = pd.read_csv('pilot-04_run-01.log', sep='\t', engine='python', header=None)
log_run02 = pd.read_csv('pilot-04_run-02.log', sep='\t', engine='python', header=None)
log_run03 = pd.read_csv('pilot-04_run-03.log', sep='\t', engine='python', header=None)

#count number of triggers in each run
trigger_count_run00 = len(log_run00.loc[log_run00[2] == "Keypress: 5"])
trigger_count_run01 = len(log_run01.loc[log_run01[2] == "Keypress: 5"])
trigger_count_run02 = len(log_run02.loc[log_run02[2] == "Keypress: 5"])
trigger_count_run03 = len(log_run03.loc[log_run03[2] == "Keypress: 5"])

#in the triggers audio, find silence. 
dBFS=triggers.dBFS
silent = silence.detect_silence(triggers, min_silence_len=100, silence_thresh=dBFS-16) ### this takes a few minutes ###
silent = [((start/1000),(stop/1000)) for start,stop in silent] #convert to sec

#get long pauses (>5 sec). end of each long silence indicates the first trigger
long_pauses = []
for ind,item in enumerate(silent):
    if item[1] - item[0] > 5:
        long_pauses.extend([ind,item])

#get starting point of each run by locating the first trigger
run01_start = long_pauses[3][1]
run02_start = long_pauses[5][1]
run03_start = long_pauses[7][1]

#get ending point of each run
run01_end = silent[trigger_count_run00+trigger_count_run01][0]
run02_end = silent[trigger_count_run00+trigger_count_run01+trigger_count_run02][0]
run03_end = silent[trigger_count_run00+trigger_count_run01+trigger_count_run02+trigger_count_run03][0]

#load chopped audio
participant_run01 = participant[run01_start*1000:run01_end*1000]
participant_run02 = participant[run02_start*1000:run02_end*1000]
participant_run03 = participant[run03_start*1000:run03_end*1000]
operator_run01 = operator[run01_start*1000:run01_end*1000]
operator_run02 = operator[run02_start*1000:run02_end*1000]
operator_run03 = operator[run03_start*1000:run03_end*1000]

#save each run as individual file
# participant_run01.export("pilot-04_participant_run-01.mp3", format="mp3")
# participant_run02.export("pilot-04_participant_run-02.mp3", format="mp3")
# participant_run03.export("pilot-04_participant_run-03.mp3", format="mp3")
# operator_run01.export("pilot-04_operator_run-01.mp3", format="mp3")
# operator_run02.export("pilot-04_operator_run-02.mp3", format="mp3")
# operator_run03.export("pilot-04_operator_run-03.mp3", format="mp3")
# operator_run03.close()

######################
### chop subtitles ###
######################

#get the timing of first and last trigger, relative to the whole 
run01_start_mins = int(run01_start//60)
run01_start_secs = round(run01_start%60,2)
run01_end_mins = int(run01_end//60)
run01_end_secs = round(run01_end%60,2)
run02_start_mins = int(run02_start//60)
run02_start_secs = round(run02_start%60,2)
run02_end_mins = int(run02_end//60)
run02_end_secs = round(run02_end%60,2)
run03_start_mins = int(run03_start//60)
run03_start_secs = round(run03_start%60,2)
run03_end_mins = int(run03_end//60)
run03_end_secs = round(run03_end%60,2)

#read subtitles
subs_operator = pysrt.open('pilot-04-transcriptions-operator-segmented.srt', encoding='utf-8')
subs_participant = pysrt.open('pilot-04-transcriptions-participant-segmented.srt', encoding='utf-8')

#for each run, take only the parts that are between first and last trigger
subs_operator_run01 = subs_operator.slice(starts_after={'minutes': run01_start_mins, 'seconds': run01_start_secs}, ends_before={'minutes': run01_end_mins, 'seconds': run01_end_secs})
subs_operator_run02 = subs_operator.slice(starts_after={'minutes': run02_start_mins, 'seconds': run02_start_secs}, ends_before={'minutes': run02_end_mins, 'seconds': run02_end_secs})
subs_operator_run03 = subs_operator.slice(starts_after={'minutes': run03_start_mins, 'seconds': run03_start_secs}, ends_before={'minutes': run03_end_mins, 'seconds': run03_end_secs})
subs_participant_run01 = subs_participant.slice(starts_after={'minutes': run01_start_mins, 'seconds': run01_start_secs}, ends_before={'minutes': run01_end_mins, 'seconds': run01_end_secs})
subs_participant_run02 = subs_participant.slice(starts_after={'minutes': run02_start_mins, 'seconds': run02_start_secs}, ends_before={'minutes': run02_end_mins, 'seconds': run02_end_secs})
subs_participant_run03 = subs_participant.slice(starts_after={'minutes': run03_start_mins, 'seconds': run03_start_secs}, ends_before={'minutes': run03_end_mins, 'seconds': run03_end_secs})

#make a subtitle line that indicates start of run
run01_started = pysrt.SubRipItem(1, start=f"00:{run01_start_mins}:{str(run01_start_secs)}", end=f"00:{run01_start_mins}:{run01_start_secs}", text="run 01 started")
run02_started = pysrt.SubRipItem(1, start=f"00:{run02_start_mins}:{str(run02_start_secs)}", end=f"00:{run02_start_mins}:{run02_start_secs}", text="run 02 started")
run03_started = pysrt.SubRipItem(1, start=f"00:{run03_start_mins}:{str(run03_start_secs)}", end=f"00:{run03_start_mins}:{run03_start_secs}", text="run 03 started")

#insert this line to the subtitles
subs_operator_run01.insert(0,run01_started)
subs_operator_run02.insert(0,run02_started)
subs_operator_run03.insert(0,run03_started)
subs_participant_run01.insert(0,run01_started)
subs_participant_run02.insert(0,run02_started)
subs_participant_run03.insert(0,run03_started)

#shift the subtitles to start from 00:00
subs_operator_run01.shift(minutes = - subs_operator_run01[0].start.minutes)
subs_operator_run01.shift(seconds = - subs_operator_run01[0].start.seconds)
subs_operator_run02.shift(minutes = - subs_operator_run02[0].start.minutes)
subs_operator_run02.shift(seconds = - subs_operator_run02[0].start.seconds)
subs_operator_run03.shift(minutes = - subs_operator_run03[0].start.minutes)
subs_operator_run03.shift(seconds = - subs_operator_run03[0].start.seconds)

subs_participant_run01.shift(minutes = - subs_participant_run01[0].start.minutes)
subs_participant_run01.shift(seconds = - subs_participant_run01[0].start.seconds)
subs_participant_run02.shift(minutes = - subs_participant_run02[0].start.minutes)
subs_participant_run02.shift(seconds = - subs_participant_run02[0].start.seconds)
subs_participant_run03.shift(minutes = - subs_participant_run03[0].start.minutes)
subs_participant_run03.shift(seconds = - subs_participant_run03[0].start.seconds)

#save to individual srt files
subs_operator_run01.save('subs_operator_run01.srt', encoding='utf-8')
subs_operator_run02.save('subs_operator_run02.srt', encoding='utf-8')
subs_operator_run03.save('subs_operator_run03.srt', encoding='utf-8')
subs_participant_run01.save('subs_participant_run01.srt', encoding='utf-8')
subs_participant_run02.save('subs_participant_run02.srt', encoding='utf-8')
subs_participant_run03.save('subs_participant_run03.srt', encoding='utf-8')