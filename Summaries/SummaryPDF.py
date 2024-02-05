import json
import openai
import re
import pdfplumber
import os

def read_text_file(file_path):
    with open(file_path, 'r',encoding='utf-8') as file:
        return file.read()

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



def create_json_with_Long_summary(json_file_path, summary):
    # Extracting the first sentence for the title
    title_match = re.match(r"([^.]*.)", summary)
    title = title_match.group(0).strip() if title_match else "Summary"

    # Creating a dictionary for JSON data
    summary_data = {
        
        'summary': summary
    }

    # Writing the dictionary to a JSON file
    with open(json_file_path, 'w') as file:
        json.dump(summary_data, file, indent=4)

def extract_text_from_pdf_plumber(pdf_path, txt_file_path):
    # Open the PDF file
    if not os.path.exists(txt_file_path):
     print("does not exists")
        # Create the directory, including any necessary parent directories
     with pdfplumber.open(pdf_path) as pdf:
        # Open the text file in write mode
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            # Iterate through each page in the PDF
            for page in pdf.pages:
                # Extract text from the page
                text = page.extract_text()
                
                # Write the text to the text file, if text was found
                if text:
                    txt_file.write(text)
                    
                    # Optionally, add a page break in the text file
                    txt_file.write('\n--- Page Break ---\n\n')
    
    print(f"Text extracted and saved to {txt_file_path}")

PDFFile='Summaries/test.pdf'
text_file_path = 'Summaries/transcribed_text_From_PDF.txt'
json_file_path = 'Summaries/Long_summary_From_PDF.json'

api_key = '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'
extract_text_from_pdf_plumber(PDFFile,text_file_path)
text = read_text_file(text_file_path)
summary = get_Long_summary_from_gpt3(text, api_key)

create_json_with_Long_summary(json_file_path, summary)