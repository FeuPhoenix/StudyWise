import requests
import moviepy.editor as mp
import assemblyai as aai
import json
#using assemplyai
def main():
 aai.settings.api_key = "387c065c75c04214a0dd420085296a70"



# Load the video and extract audio
 video = mp.VideoFileClip("Sumaries/How I'd Learn AI in 2023 (if I could start over).mp4")
 audio = video.audio
 audio.write_audiofile("extracted_audio.wav")

# Initialize transcriber and configuration
 audio_url = "extracted_audio.wav"
 config = aai.TranscriptionConfig(auto_chapters=True)

# Transcribe the audio and get the result as a JSON object
 transcript = aai.Transcriber().transcribe(audio_url, config)
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

if __name__ == "__main__":
  main()