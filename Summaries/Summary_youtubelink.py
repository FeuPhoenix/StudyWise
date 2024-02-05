from pytube import YouTube
import requests
import assemblyai as aai
import requests
import time
import json
import openai
import re
from pytube import YouTube
import os
aai.settings.api_key = "387c065c75c04214a0dd420085296a70"


upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': aai.settings.api_key}

headers = {
    "authorization": aai.settings.api_key,
    "content-type": "application/json"
}

  #




def download_audio_from_youtube(video_url, output_path):
    # Create a YouTube object with the URL
    yt = YouTube(video_url)
    
    # Get the audio stream with the highest quality
    audio_stream = yt.streams.get_audio_only()
    
    # Define the filename for the audio file
    filename = yt.title + '.mp3'

    # Download the audio stream
    audio_stream.download(output_path=output_path, filename=filename)
    
    # Construct the full path to the downloaded audio file
    audio_file_path = os.path.join(output_path, filename)

    # Return the full path of the downloaded audio file
    return audio_file_path

def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

# def get_Long_summary_from_gpt3(text, api_key):
#     openai.api_key = api_key

#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant."},
#             {"role": "user", "content": ''' You are provided audio that were transcribed from the youtube video's audio.
#     Summarize the current transcription to succint and clear bullet points of its contents.
#     : \n''' + text}
#         ]
#     )
#     return response['choices'][0]['message']['content'].strip()

    


def split_text(text, max_chunk_size=3800):  # Reduced max_chunk_size for safety
    """
    Dynamically splits the text into chunks that are less than max_chunk_size,
    trying to avoid cutting off in the middle of a sentence.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    current_chunk = ""
    for sentence in sentences:
        # Check if adding the next sentence would exceed the max chunk size
        if len(current_chunk) + len(sentence) > max_chunk_size:
            yield current_chunk
            current_chunk = sentence  # Start a new chunk
        else:
            current_chunk += " " + sentence
    yield current_chunk  # Yield the last chunk

def get_Long_summary_from_gpt3(text, api_key):
    openai.api_key = api_key
    summaries = []

    for chunk in split_text(text):
        while True:  # Keep trying until successful
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"Summarize the following text into concise bullet points, focusing only on essential information: \n{chunk}"}
                    ]
                )
                summaries.append(response['choices'][0]['message']['content'].strip())
                break  # Exit the loop if successful
            except openai.error.RateLimitError as e:
                print("Rate limit exceeded, waiting to retry...")
                time.sleep(20)  # Wait for 20 seconds before retrying

    full_summary = ' '.join(summaries)
    return full_summary






def main():
 video_url = 'https://www.youtube.com/watch?v=b1t41Q3xRM8'  # Replace with your YouTube video URL
 output_path = './'  # The directory where you want to save the audio file
 audio_file_path = download_audio_from_youtube(video_url, output_path)
 print(f"Audio file downloaded at: {audio_file_path}") 
 config = aai.TranscriptionConfig(auto_chapters=True)

# Transcribe the audio and get the result as a JSON object
 transcript = aai.Transcriber().transcribe(audio_file_path, config)
 
 transcript_filename = "Summaries/full_transcript.txt"
 with open(transcript_filename, 'w', encoding='utf-8') as transcript_file:
        transcript_file.write(transcript.text)
        print(f"Full transcript has been successfully saved to {transcript_filename}.")
 chapters_data = []

# Iterate over chapters and add their data to the list
 for chapter in transcript.chapters:
    chapters_data.append({
        "start": chapter.start,
        "end": chapter.end,
        "headline": chapter.headline
    })

# Define the filename for the JSON file
 json_filename = "chapters.json"

# Write the chapters data to a JSON file
 with open(json_filename, 'w') as json_file:
    json.dump(chapters_data, json_file, indent=4)

 print(f"Chapters have been successfully saved to {json_filename}.")
 text_file_path = 'Summaries/full_transcript.txt'
 json_file_path = 'Long_summary_From_Youtube.json'
 

 api_key = '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'

 text = read_text_file(text_file_path)
 long_summary = get_Long_summary_from_gpt3(text, api_key)
 summary_data = {
        'long_summary': long_summary
    }

    # Write the summary data to a JSON file
 with open(json_file_path, 'w') as json_file:
        json.dump(summary_data, json_file, indent=4)
        print(f"Long summary has been successfully saved to {json_file_path}.") 

if __name__ == "__main__":
  main()


