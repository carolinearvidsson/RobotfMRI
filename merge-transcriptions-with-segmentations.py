import csv

class Merger:
    '''This program merges transcriptions from the Google cloud module 
    with segmentations (time stamps) from Silero VAD'''

    def __init__(self):
        subs = ['sub-01']
        runs = ['run-01', 'run-02', 'run-03']
        speakers = ['_operator_', '_participant_']

        for sub in subs:
            self.folder = sub + '/'
            for run in runs:
                for spk in speakers:
                    self.final_filename = sub + spk + run + '_merged-awaiting-manual-check.csv'
                    transcriptions = self.make_dicts(self.folder + 'transcribed-words/' + sub + spk + run + '-word_level_transcriptions.csv', 'transcription')
                    segmentations = self.make_dicts(self.folder + 'segmentations/' + sub + spk + run + '.csv', 'segmentation')
                    self.write_merged_file(self.merge_segmentations(transcriptions, segmentations)) 

    def make_dicts(self, filename, transorsegm):
        d = []
        with open(filename, 'r') as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                if transorsegm == 'segmentation':
                    row = [row[-1]] + row[:-1]
                if row[0] != '\ufefftranscription':
                    d.append({'annotation': row[0], \
                              'starttime': self.convert_times_to_secs(row[1]), \
                                'endtime': self.convert_times_to_secs(row[2])})
        return d
    
    def convert_times_to_secs(self, time):
        time = time.replace('.', ':').split(':')
        mins = int(time[1])
        minstosec = mins * 60
        secs = int(time[2].split('.')[0])
        try:
            millisecs = int(time[3])
        except IndexError: millisecs = 0
        return minstosec + secs + (millisecs/1000000)
    
    def merge_segmentations(self, transcriptions, segmentations):
        merged = []
        for i, segment in enumerate(segmentations):
            s_start, s_end = segment['starttime'], segment['endtime']
            try: 
                next_s_start, next_s_end = segmentations[i+1]['starttime'], segmentations[i+1]['endtime']
                previous_s_start, previous_s_end = segmentations[i-1]['starttime'], segmentations[i-1]['endtime']
            except IndexError: continue
            annotation = ''

            for transcription in transcriptions:
                t_start, t_end = transcription['starttime'], transcription['endtime']
                word = transcription['annotation'].lower().strip('.')
                
                #if transcribed word is inside segment or segment is inside transcribed word:
                if t_start < s_start and s_end < t_end or s_start < t_start and t_end < s_end:
                    annotation += word + ' '
                
                elif s_start < t_start and t_start < s_end:
                    if t_start < next_s_start and next_s_end < t_end:
                        continue
                    elif t_start < next_s_start and next_s_start < t_end:
                        current_overlap = s_start - t_start
                        next_overlap = t_end - next_s_start
                        if current_overlap > next_overlap:
                            annotation += word + ' '
                    else: annotation += word + ' '

                
                elif t_start < s_start and s_start < t_end:
                    if t_start < previous_s_start and previous_s_end < t_end:
                        continue
                    elif s_start < t_start and t_start < s_end:
                        current_overlap = t_end - s_start
                        previous_overlap = t_end - previous_s_end
                        if current_overlap > previous_overlap:
                            annotation += word + ' '
                    else: annotation += word + ' '

            annotation = annotation.strip()
            merged.append((annotation.replace(',', ''), self.convert_secs_to_time(s_start), self.convert_secs_to_time(s_end)))

        return merged

    def convert_secs_to_time(self, secs):
        hours = '00'
        mins = int(secs / 60)
        secs = str(secs - (mins * 60))
        time = hours + ':' + '0' + str(mins) + ':' + secs
        return time

    def write_merged_file(self, merged):
        folder = self.folder + 'merged-awaiting-manual-check/'
        with open(folder + self.final_filename, 'w') as finalfile:
            write = csv.writer(finalfile, delimiter ='\t')
            write.writerows(merged)

m = Merger()
m
