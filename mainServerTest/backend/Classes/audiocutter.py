import subprocess
from audiotsm import phasevocoder
from audiotsm.io.wav import WavReader, WavWriter
from scipy.io import wavfile
import numpy as np
import re
import math
from shutil import copyfile, rmtree
import os
import time
import shutil

class AudioCutter:
    def __init__(self, input_file, temp_folder="mainServerTest/assets/output_files/Temp_Files/TEMP"):
        self.input_file = input_file
        self.temp_folder = temp_folder
        self.start_time = time.time()
    
    def get_max_volume(self, s):  # get max volume of a given audio file (we also find the min volume because audio signals signals can have negative values)
        maxv = float(np.max(s))
        minv = float(np.min(s))
        return max(maxv, -minv)

    def copy_frame(self, input_frame, output_frame):  # copy frame inputFrame and save it as outputFrame
        src = self.temp_folder + "/frame{:06d}".format(input_frame + 1) + ".jpg"
        dst = self.temp_folder + "/newFrame{:06d}".format(output_frame + 1) + ".jpg"
        if not os.path.isfile(src):
            return False
        copyfile(src, dst)
        if output_frame % 20 == 19:
            print(str(output_frame + 1) + " time-altered frames saved.")
        return True

    def create_path(self, s):  # Create directory structure for a given path
        try:
            if os.path.exists(s):
                # Remove folder, along with contents if it already exists
                self.delete_path(s)
            # Create the folder, including any necessary directories
            os.makedirs(s)
        except OSError:
            # Raise an exception with a message if there's an error
            print(f"Creation of the directory {s} failed.")
            print(OSError)

    def delete_path(self, s):  # Dangerous! Watch out!
        try:
            rmtree(s, ignore_errors=False)
        except OSError:
            print("Deletion of the directory %s failed" % s)
            print(OSError)

    def get_file_name_from_path(self, input_string):
        # Find the last occurrence of '/'
        last_slash_index = input_string.rfind('\\')

        # Slice the string from the character after the last '/'
        # If '/' is not found, rfind returns -1, and slicing starts from index 0
        result_string = input_string[last_slash_index + 1:]

        return result_string

    def get_file_name_from_path_without_extension(self, input_string):
        # Find the last occurrence of '/'
        last_slash_index = input_string.rfind('\\')

        # Slice the string from the character after the last '/'
        # If '/' is not found, rfind returns -1, and slicing starts from index 0
        result_string = input_string[last_slash_index + 1:]
        result_string = result_string.replace('.mp4', '')
        return result_string

    def run_audio_cutter(self):
        # Parameters
        FILE_NAME = self.get_file_name_from_path_without_extension(self.input_file)
        OUTPUT_FILE = 'mainServerTest/assets/output_files/video/' + FILE_NAME + '_AUDIOCUT.mp4'
        SILENT_THRESHOLD = 0.03
        SOUNDED_SPEED = 1.0
        SILENT_SPEED = 5.0
        FRAME_QUALITY = 3
        SAMPLE_RATE = 44100
        frame_rate = 30
        FRAME_SPREADAGE = 1
        NEW_SPEED = [SILENT_SPEED, SOUNDED_SPEED]

        assert self.input_file is not None, "you forgot to put an input file"

        # smooth out transition's audio by quickly fading in/out
        AUDIO_FADE_ENVELOPE_SIZE = 400

        # Example temporary folder path in Colab
        self.create_path(self.temp_folder)

        command = f"ffmpeg -i {self.input_file} -qscale:v {FRAME_QUALITY} {self.temp_folder}/frame%06d.jpg -hide_banner"  # extract frames from input video
        subprocess.call(command, shell=True)

        command = f"ffmpeg -i {self.input_file} -ab 160k -ac 2 -ar {SAMPLE_RATE} -vn {self.temp_folder}/audio.wav"  # extract audio from input video
        subprocess.call(command, shell=True)

        command = f"ffmpeg -i {self.temp_folder}/input.mp4 2>&1"  # get video info
        with open(self.temp_folder + "/params.txt", "w") as f:  # write video info to file
            subprocess.call(command, shell=True, stdout=f)

        sample_rate, audio_data = wavfile.read(self.temp_folder + "/audio.wav")  # read audio file
        audio_sample_count = audio_data.shape[0]  # number of audio samples
        max_audio_volume = self.get_max_volume(audio_data)  # max volume of audio file

        with open(self.temp_folder + "/params.txt", 'r+') as f:
            pre_params = f.read()
        params = pre_params.split('\n')
        for line in params:  # get frame rate of input video
            m = re.search('Stream #.*Video.* ([0-9]*) fps', line)
            if m is not None:
                frame_rate = float(m.group(1))

        samples_per_frame = sample_rate / frame_rate  # number of audio samples per video frame
        audio_frame_count = int(math.ceil(audio_sample_count / samples_per_frame))  # number of frames in audio file
        has_loud_audio = np.zeros((audio_frame_count))  # array of booleans, True if audio frame has loud audio

        for i in range(audio_frame_count):  # check if audio frame has loud audio
            start = int(i * samples_per_frame)
            end = min(int((i + 1) * samples_per_frame), audio_sample_count)
            audio_chunks = audio_data[start:end]  # audio data for a given frame
            max_chunks_volume = float(self.get_max_volume(audio_chunks)) / max_audio_volume  # max volume of audio data for a given frame
            if max_chunks_volume >= SILENT_THRESHOLD:
                has_loud_audio[i] = 1

        chunks = [[0, 0, 0]]  # 2D array of chunks, each chunk has [start, end, shouldInclude]
        should_include_frame = np.zeros((audio_frame_count))
        for i in range(audio_frame_count):  # determine which audio frames should be included
            start = int(max(0, i - FRAME_SPREADAGE))
            end = int(min(audio_frame_count, i + 1 + FRAME_SPREADAGE))
            should_include_frame[i] = np.max(has_loud_audio[start:end])  # should_include_frame[i] = 1 if audio frame has loud audio
            if (i >= 1 and should_include_frame[i] != should_include_frame[i - 1]):  # if should_include_frame changes, add a new chunk
                chunks.append([chunks[-1][1], i, should_include_frame[i - 1]])

        chunks.append([chunks[-1][1], audio_frame_count, should_include_frame[i - 1]])
        chunks = chunks[1:]  # remove first empty chunk

        output_audio_data = np.zeros((0, audio_data.shape[1]))
        output_pointer = 0
        last_existing_frame = None

        # for each chunk, speed up or slow down audio to match video frame rate
        for chunk in chunks:
            audio_chunk = audio_data[int(chunk[0] * samples_per_frame):int(chunk[1] * samples_per_frame)]  # audioData is an array that has a start (chunk[0]) and end (chunk[1]) point, we multiply by samplesPerFrame to get the audio data for that chunk
            s_file = self.temp_folder + "/tempStart.wav"
            e_file = self.temp_folder + "/tempEnd.wav"
            wavfile.write(s_file, SAMPLE_RATE, audio_chunk)
            with WavReader(s_file) as reader:  # read audio file
                with WavWriter(e_file, reader.channels, reader.samplerate) as writer:  # write audio file
                    tsm = phasevocoder(reader.channels, speed=NEW_SPEED[int(chunk[2])])  # time-scale modification
                    tsm.run(reader, writer)
            _, altered_audio_data = wavfile.read(e_file)
            leng = altered_audio_data.shape[0]
            end_pointer = output_pointer + leng
            output_audio_data = np.concatenate((output_audio_data, altered_audio_data / max_audio_volume))  # combine audio data for all chunks

            # smooth out transition's audio by quickly fading in/out
            if leng < AUDIO_FADE_ENVELOPE_SIZE:
                output_audio_data[output_pointer:end_pointer] = 0  # audio is less than 0.01 sec, let's just remove it.
            else:
                premask = np.arange(AUDIO_FADE_ENVELOPE_SIZE) / AUDIO_FADE_ENVELOPE_SIZE  # create fade-envelope mask
                mask = np.repeat(premask[:, np.newaxis], 2, axis=1)
                output_audio_data[output_pointer:output_pointer + AUDIO_FADE_ENVELOPE_SIZE] *= mask  # fade in
                output_audio_data[end_pointer - AUDIO_FADE_ENVELOPE_SIZE:end_pointer] *= 1 - mask

            start_output_frame = int(math.ceil(output_pointer / samples_per_frame))
            end_output_frame = int(math.ceil(end_pointer / samples_per_frame))
            for output_frame in range(start_output_frame, end_output_frame):  # copy frames from input video to output video
                input_frame = int(chunk[0] + NEW_SPEED[int(chunk[2])] * (output_frame - start_output_frame))
                did_it_work = self.copy_frame(input_frame, output_frame)
                if did_it_work:
                    last_existing_frame = input_frame
                else:
                    self.copy_frame(last_existing_frame, output_frame)

            output_pointer = end_pointer

        wavfile.write(self.temp_folder + "/audioNew.wav", SAMPLE_RATE, output_audio_data)  # write audio data to file

        # OUTPUT VIDEO CREATION
        command = f"ffmpeg -framerate {frame_rate} -i {self.temp_folder}/newFrame%06d.jpg -i {self.temp_folder}/audioNew.wav -strict -2 {OUTPUT_FILE}"  # combine frames and audio to create output video
        subprocess.call(command, shell=True)

        # After everything is done, calculate the time taken
        end_time = time.time()
        execution_time = end_time - self.start_time

        # Calculate the reduction in video length
        original_duration = float(audio_sample_count) / sample_rate
        new_duration = float(output_pointer) / sample_rate
        reduction_percentage = ((original_duration - new_duration) / original_duration) * 100

        # Print statistics
        print("Process finished in {:.2f} seconds".format(execution_time))
        print("Original video duration: {:.2f} seconds".format(original_duration))
        print("New video duration: {:.2f} seconds".format(new_duration) + " (saved in {OUTPUT_FILE})")
        print("Percentage reduction in video length: {:.2f}%".format(reduction_percentage))

        # Takes a Video Frame and saves it to the output video's path
        # to be used as the video's poster/thumbnail when displaying in html

        SAVED_FRAME = 'mainServerTest/assets/output_files/Temp_Files/TEMP/frame000069.jpg'
        VIDEO_POSTER_PATH = 'mainServerTest/assets/output_files/video/frame000069.jpg'
        # shutil.copy(SAVED_FRAME, VIDEO_POSTER_PATH)
        # os.rename(VIDEO_POSTER_PATH, 'mainservertest/assets/output_files/videos/(Video-Poster)_' + FILE_NAME + '.jpg')

        # ↓ Uncomment if you need to keep Temp Files (and comment deletePath below)
        # os.rename(TEMP_FOLDER, "mainservertest/assets/output_files/Temp_Files/" + FILE_NAME + "_Processing-Files")

        self.delete_path(self.temp_folder)
        return OUTPUT_FILE