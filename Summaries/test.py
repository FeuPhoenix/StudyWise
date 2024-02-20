import json
import re
import time
import assemblyai as aai
import openai
def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()
def split_text(text, max_chunk_size=200):  # Reduced max_chunk_size for safety
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

def get_Chapters_from_gpt3(text, api_key):
    openai.api_key = api_key
    chapters = []

    for chunk in split_text(text):
        while True:  # Keep trying until successful
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"You are provided with sentences, starting time of the sentence in milliseconds, and the ending time of the sentence in milliseconds transcribed from an audio file in chunks.\n{chunk}"},
                        {"role": "user", "content": "I need you to provide concise topics based on the sentences and write the starting and ending time of the topics in the following format hours:minutes:seconds."},
                    ]
                )
                chapters.append(response['choices'][0]['message']['content'].strip())
                break  # Exit the loop if successful
            except openai.error.RateLimitError as e:
                print("Rate limit exceeded, waiting to retry...")
                time.sleep(20)  # Wait for 20 seconds before retrying

    full_chapters = ' '.join(chapters)
    return full_chapters
aai.settings.api_key = "387c065c75c04214a0dd420085296a70"
api_key = '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'

audio_url = "Physics - Basic Introduction.mp3"

config = aai.TranscriptionConfig(sentiment_analysis=True)

# transcript = aai.Transcriber().transcribe(audio_url, config)

# with open("sentiment_results.txt", "w") as txt_file:
#     for sentiment_result in transcript.sentiment_analysis:
#         txt_file.write(sentiment_result.text + '\n')
#         txt_file.write(f"Timestamp: {sentiment_result.start} - {sentiment_result.end}\n")
text=read_text_file("sentiment_results.txt")
chapters_data = get_Chapters_from_gpt3(text,api_key)
# Define the file path where you want to save the JSON file
json_file_path = "chapters_data.json"

# Save the data to the JSON file
with open(json_file_path, "w") as json_file:
    json.dump({"chapters": chapters_data}, json_file, indent=4)

print(f"Data saved to {json_file_path}")
