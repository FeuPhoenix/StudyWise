import json
import re
import time
import assemblyai as aai
import openai

def read_text_file(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def split_text_with_timestamps(text, max_chunk_size=3800):
    """
    Dynamically splits the text into chunks that are less than max_chunk_size,
    including both the sentence and its timestamp, trying to avoid cutting off
    in the middle of a sentence or in the middle of a timestamp.
    """
    # Split the text into sentences and timestamps
    sentence_timestamps = re.findall(r'Timestamp: (\d+) - (\d+)\n(.*?)\n', text, re.DOTALL)

    current_chunk = ""
    current_chunk_size = 0

    for timestamp_start, timestamp_end, sentence in sentence_timestamps:
        timestamp = f"Timestamp: {timestamp_start} - {timestamp_end}"
        chunk = f"{timestamp}\n{sentence}"

        # Check if adding the next chunk would exceed the max chunk size
        if current_chunk_size + len(chunk) > max_chunk_size:
            yield current_chunk
            current_chunk = chunk  # Start a new chunk
            current_chunk_size = len(chunk)
        else:
            if current_chunk:
                current_chunk += "\n" + chunk
            else:
                current_chunk = chunk

            current_chunk_size += len(chunk)

    if current_chunk:
        yield current_chunk  # Yield the last chunk
def get_Topics_from_gpt3(text, api_key, max_topics=1
                         , max_chunk_size=3000):
    openai.api_key = api_key
    topics = []

    # Split the text into chunks
    text_chunks = [text[i:i+max_chunk_size] for i in range(0, len(text), max_chunk_size)]

    for chunk in text_chunks:
        while True:
            try:
                response = openai.ChatCompletion.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": f"You are provided with sentences, starting time of the sentence in millisecond, and the ending time of the sentence in millisecond transcribed from an audio file in chunks.\n{chunk}"},
                        {"role": "user", "content": f"I need you to provide a maximum of {max_topics} concise topics based on the sentences and write the starting and ending time of the topics only in the following format hour:minute:second."},
                    ]
                )
                topics.append(response['choices'][0]['message']['content'].strip())
                break  # Exit the loop if successful
            except openai.error.RateLimitError as e:
                print("Rate limit exceeded, waiting to retry...")
                time.sleep(20)  # Wait for 20 seconds before retrying

    full_topics = ' '.join(topics)
    return full_topics

# Your API keys and file path
aai.settings.api_key = "387c065c75c04214a0dd420085296a70"
api_key = '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'
file_path ="sentiment_results.txt"

# Read the text from the file
text = read_text_file(file_path)

# Get topics and their timestamps
topics_data = get_Topics_from_gpt3(text, api_key)

# Define the file path where you want to save the JSON file
json_file_path = "topics_data.json"

# Save the data to the JSON file
with open(json_file_path, "w") as json_file:
    json.dump({"topics": topics_data}, json_file, indent=4)

print(f"Topics data saved to {json_file_path}")
