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

start_time = time.time()

def getMaxVolume(s): # get max volume of a given audio file (we also find the min volume because audio signals signals can have negative values)
    maxv = float(np.max(s))
    minv = float(np.min(s)) 
    return max(maxv,-minv) 

def copyFrame(inputFrame,outputFrame): # copy frame inputFrame and save it as outputFrame
    src = TEMP_FOLDER+"/frame{:06d}".format(inputFrame+1)+".jpg"
    dst = TEMP_FOLDER+"/newFrame{:06d}".format(outputFrame+1)+".jpg"
    if not os.path.isfile(src):
        return False
    copyfile(src, dst)
    if outputFrame%20 == 19:
        print(str(outputFrame+1)+" time-altered frames saved.")
    return True

def createPath(s): # create directory structure for a given path
    try:
        os.mkdir(s)
    except OSError:
        assert False, "Creation of the directory %s failed. (The TEMP folder may already exist. Delete or rename it, and try again.)"

def deletePath(s): # Dangerous! Watch out!
    try:
        rmtree(s,ignore_errors=False)
    except OSError:
        print ("Deletion of the directory %s failed" % s)
        print(OSError)

#Parameters
INPUT_FILE = 'smlexample.mp4'
OUTPUT_FILE = 'smlexample_altered.mp4'
SILENT_THRESHOLD = 0.03
SOUNDED_SPEED = 1.0
SILENT_SPEED = 5.0
FRAME_QUALITY = 3
SAMPLE_RATE = 44100
frameRate = 30
FRAME_SPREADAGE = 1
NEW_SPEED = [SILENT_SPEED, SOUNDED_SPEED]

assert INPUT_FILE != None , "you forgot to put an input file"

AUDIO_FADE_ENVELOPE_SIZE = 400 # smooth out transitiion's audio by quickly fading in/out

TEMP_FOLDER = "TEMP"  # Example temporary folder path in Colab
createPath(TEMP_FOLDER)

command = "ffmpeg -i "+INPUT_FILE+" -qscale:v "+str(FRAME_QUALITY)+" "+TEMP_FOLDER+"/frame%06d.jpg -hide_banner" # extract frames from input video
subprocess.call(command, shell=True)

command = "ffmpeg -i "+INPUT_FILE+" -ab 160k -ac 2 -ar "+str(SAMPLE_RATE)+" -vn "+TEMP_FOLDER+"/audio.wav" # extract audio from input video

subprocess.call(command, shell=True) 

command = "ffmpeg -i "+TEMP_FOLDER+"/input.mp4 2>&1" # get video info
f = open(TEMP_FOLDER+"/params.txt", "w") # write video info to file
subprocess.call(command, shell=True, stdout=f)



sampleRate, audioData = wavfile.read(TEMP_FOLDER+"/audio.wav") # read audio file
audioSampleCount = audioData.shape[0] # number of audio samples
maxAudioVolume = getMaxVolume(audioData) # max volume of audio file

f = open(TEMP_FOLDER+"/params.txt", 'r+') 
pre_params = f.read()
f.close() 
params = pre_params.split('\n') 
for line in params: # get frame rate of input video
    m = re.search('Stream #.*Video.* ([0-9]*) fps',line)
    if m is not None:
        frameRate = float(m.group(1))

samplesPerFrame = sampleRate/frameRate # number of audio samples per video frame

audioFrameCount = int(math.ceil(audioSampleCount/samplesPerFrame)) # number of frames in audio file

hasLoudAudio = np.zeros((audioFrameCount)) # array of booleans, True if audio frame has loud audio



for i in range(audioFrameCount): # check if audio frame has loud audio
    start = int(i*samplesPerFrame)
    end = min(int((i+1)*samplesPerFrame),audioSampleCount)
    audiochunks = audioData[start:end] # audio data for a given frame
    maxchunksVolume = float(getMaxVolume(audiochunks))/maxAudioVolume # max volume of audio data for a given frame
    if maxchunksVolume >= SILENT_THRESHOLD:
        hasLoudAudio[i] = 1

chunks = [[0,0,0]] # 2D array of chunks, each chunk has [start, end, shouldInclude]
shouldIncludeFrame = np.zeros((audioFrameCount)) 
for i in range(audioFrameCount): # determine which audio frames should be included
    start = int(max(0,i-FRAME_SPREADAGE))
    end = int(min(audioFrameCount,i+1+FRAME_SPREADAGE))
    shouldIncludeFrame[i] = np.max(hasLoudAudio[start:end]) # shouldIncludeFrame[i] = 1 if audio frame has loud audio
    if (i >= 1 and shouldIncludeFrame[i] != shouldIncludeFrame[i-1]): # if shouldIncludeFrame changes, add a new chunk
        chunks.append([chunks[-1][1],i,shouldIncludeFrame[i-1]])

chunks.append([chunks[-1][1],audioFrameCount,shouldIncludeFrame[i-1]])
chunks = chunks[1:] # remove first empty chunk

outputAudioData = np.zeros((0,audioData.shape[1]))
outputPointer = 0

lastExistingFrame = None 
# for each chunk, speed up or slow down audio to match video frame rate
for chunk in chunks: 
    audioChunk = audioData[int(chunk[0]*samplesPerFrame):int(chunk[1]*samplesPerFrame)] #audioData is an array that has a start (chunk[0]) and end (chunk[1]) point, we multiply by samplesPerFrame to get the audio data for that chunk
    sFile = TEMP_FOLDER+"/tempStart.wav"
    eFile = TEMP_FOLDER+"/tempEnd.wav" 
    wavfile.write(sFile,SAMPLE_RATE,audioChunk)
    with WavReader(sFile) as reader: # read audio file
        with WavWriter(eFile, reader.channels, reader.samplerate) as writer: # write audio file
            tsm = phasevocoder(reader.channels, speed=NEW_SPEED[int(chunk[2])]) # time-scale modification
            tsm.run(reader, writer) 
    _, alteredAudioData = wavfile.read(eFile) 
    leng = alteredAudioData.shape[0]
    endPointer = outputPointer+leng 
    outputAudioData = np.concatenate((outputAudioData,alteredAudioData/maxAudioVolume)) # combine audio data for all chunks

    # smooth out transitiion's audio by quickly fading in/out
    if leng < AUDIO_FADE_ENVELOPE_SIZE: 
        outputAudioData[outputPointer:endPointer] = 0 # audio is less than 0.01 sec, let's just remove it.
    else:
        premask = np.arange(AUDIO_FADE_ENVELOPE_SIZE)/AUDIO_FADE_ENVELOPE_SIZE # create fade-envelope mask
        mask = np.repeat(premask[:, np.newaxis],2,axis=1)
        outputAudioData[outputPointer:outputPointer+AUDIO_FADE_ENVELOPE_SIZE] *= mask # fade in
        outputAudioData[endPointer-AUDIO_FADE_ENVELOPE_SIZE:endPointer] *= 1-mask 

    startOutputFrame = int(math.ceil(outputPointer/samplesPerFrame)) 
    endOutputFrame = int(math.ceil(endPointer/samplesPerFrame))
    for outputFrame in range(startOutputFrame, endOutputFrame): # copy frames from input video to output video
        inputFrame = int(chunk[0]+NEW_SPEED[int(chunk[2])]*(outputFrame-startOutputFrame))
        didItWork = copyFrame(inputFrame,outputFrame)
        if didItWork:
            lastExistingFrame = inputFrame
        else:
            copyFrame(lastExistingFrame,outputFrame)

    outputPointer = endPointer

wavfile.write(TEMP_FOLDER+"/audioNew.wav",SAMPLE_RATE,outputAudioData) # write audio data to file

command = "ffmpeg -framerate "+str(frameRate)+" -i "+TEMP_FOLDER+"/newFrame%06d.jpg -i "+TEMP_FOLDER+"/audioNew.wav -strict -2 "+OUTPUT_FILE # combine frames and audio to create output video
subprocess.call(command, shell=True)
# After everything is done, calculate the time taken
end_time = time.time()
execution_time = end_time - start_time

# Calculate the reduction in video length
original_duration = float(audioSampleCount) / sampleRate
new_duration = float(outputPointer) / sampleRate
reduction_percentage = ((original_duration - new_duration) / original_duration) * 100

# Print statistics
print("Process finished in {:.2f} seconds".format(execution_time))
print("Original video duration: {:.2f} seconds".format(original_duration))
print("New video duration: {:.2f} seconds".format(new_duration))
print("Percentage reduction in video length: {:.2f}%".format(reduction_percentage))
deletePath(TEMP_FOLDER)