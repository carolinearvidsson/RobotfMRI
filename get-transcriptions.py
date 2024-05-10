from google.cloud import speech

client = speech.SpeechClient()
subs = ['sub-01']
runs = ['run-02', 'run-03']
for sub in subs:
    for run in runs:
        audiofilename = sub + '_operator_' + run
        uri = "gs://robotfmri/audio-files/" + audiofilename + '.wav' # path to the audio file in google cloud storage

        audio = speech.RecognitionAudio(uri=uri)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=44100,
            language_code="sv-SE",
            enable_automatic_punctuation=True,
            enable_word_time_offsets=True
        )

        operation = client.long_running_recognize(config=config, audio=audio)

        print("Waiting for operation to complete...")
        response = operation.result(timeout=1800)

        transcript_builder = []
        # Each result is for a consecutive portion of the audio. Iterate through
        # them to get the transcripts for the entire audio file.
        print(response.results)

        word_list = []
        start_time_list = []
        end_time_list = []
        for ind,result in enumerate(response.results):
            for word_info in response.results[ind].alternatives[0].words:
                    word = word_info.word
                    word_list.append(word)
                    start_time = word_info.start_time
                    start_microsecs = start_time.microseconds
                    start_secs = start_time.seconds % 60
                    start_mins = start_time.seconds//60
                    hours = 0
                    start_timestamp = f"{hours}:{start_mins}:{start_secs}.{start_microsecs}"
                    start_time_list.append(start_timestamp)
                    end_time = word_info.end_time
                    end_microsecs = end_time.microseconds
                    end_secs = end_time.seconds % 60
                    end_mins = end_time.seconds//60
                    end_timestamp = f"{hours}:{end_mins}:{end_secs}.{end_microsecs}"
                    end_time_list.append(end_timestamp)

        word_level_transcription_timestamps = list(zip(word_list,start_time_list,end_time_list))

        #save the transcriptions to a csv file in which each line contation the transcription and the start and end time of the transcription. make sure that Sweidsh characters are readable in the csv file
        import csv
        with open(audiofilename + '-word_level_transcriptions.csv', 'w', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["transcription","start_time","end_time"])
            for row in word_level_transcription_timestamps:
                writer.writerow(row)

        transcriptions = []
        for index,i in enumerate(response.results):
            transcriptions.append(response.results[index].alternatives[0].transcript)
        transcriptions

        end_timestamps = []
        for ind,i in enumerate(response.results):
            end_time = response.results[ind].result_end_time
            microsecs = end_time.microseconds
            secs = end_time.seconds % 60
            mins = end_time.seconds//60
            hours = 0
            end_timestamp = f"{hours}:{mins}:{secs}.{microsecs}"
            end_timestamps.append(end_timestamp)

        start_times = []

        for ind,result in enumerate(response.results):
            start_delta = response.results[ind].alternatives[0].words[0].start_time
            microsecs = start_delta.microseconds
            secs = start_delta.seconds % 60
            mins = start_delta.seconds//60
            hours = 0
            start_time = f"{hours}:{mins}:{secs}.{microsecs}"
            start_times.append(start_time)
        
        end_times = []

        for ind,result in enumerate(response.results):
            end_delta = response.results[ind].alternatives[0].words[-1].end_time
            microsecs = end_delta.microseconds
            secs = end_delta.seconds % 60
            mins = end_delta.seconds//60
            hours = 0
            end_time = f"{hours}:{mins}:{secs}.{microsecs}"
            end_times.append(end_time)

        transcription_timestamps = list(zip(transcriptions,start_times,end_times))

        #save the transcriptions to a csv file in which each line contation the transcription and the start and end time of the transcription. make sure that Sweidsh characters are readable in the csv file
        import csv
        with open(audiofilename + '-transcriptions.csv', 'w', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(["transcription","start_time","end_time"])
            for row in transcription_timestamps:
                writer.writerow(row)
