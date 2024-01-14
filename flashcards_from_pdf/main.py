import pdfplumber
import openai
import time
import json

openai.api_key = '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'
MAX_TOKENS_PER_REQUEST = 1000  # Define a safe limit for tokens per request

def extract_paragraphs_from_pdf(pdf_path):
    paragraphs = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                paragraphs.extend(text.split('\n'))
    return paragraphs

def generate_qa_pairs_with_chatgpt(paragraphs):
    qa_pairs = []
    batched_paragraphs = []
    current_batch = ""

    for paragraph in paragraphs:
        if len(paragraph) > 20 and "http" not in paragraph:
            if len(current_batch) + len(paragraph) < MAX_TOKENS_PER_REQUEST:
                current_batch += f"{paragraph}\n\n"
            else:
                batched_paragraphs.append(current_batch)
                current_batch = f"{paragraph}\n\n"
    
    if current_batch:
        batched_paragraphs.append(current_batch)

    for batch in batched_paragraphs:
        prompt = [{"role": "system", "content": "You are a helpful assistant."},
                  {"role": "user", "content": f"Generate questions and answers based on this text: {batch}"}]
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
            response_text = response.choices[0].message['content'].strip()
            qa_pairs.extend(response_text.split('\n\n'))
        except openai.error.RateLimitError:
            print("Rate limit reached, waiting for 30 seconds...")
            time.sleep(30)
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
            response_text = response.choices[0].message['content'].strip()
            qa_pairs.extend(response_text.split('\n\n'))
    
    return qa_pairs

def format_flash_cards(qa_pairs):
    formatted_cards = []
    for pair in qa_pairs:
        if pair.count('\n') == 1:  # Expecting each pair to be two lines: question and answer
            question, answer = pair.split('\n')
            formatted_cards.append({'front': question, 'back': answer})
    return formatted_cards

def save_flash_cards_to_file(formatted_cards, filename):
    with open(filename, 'w') as file:
        json.dump(formatted_cards, file, indent=4)

def main(pdf_path, output_file):
    paragraphs = extract_paragraphs_from_pdf(pdf_path)
    qa_pairs = generate_qa_pairs_with_chatgpt(paragraphs)
    formatted_cards = format_flash_cards(qa_pairs)
    save_flash_cards_to_file(formatted_cards, output_file)

pdf_path = 'flashcards_from_pdf/test.pdf'
output_file = 'flashcards_from_pdf/JS/flash_cards.json'
main(pdf_path, output_file)
print(f"Flash cards saved to {output_file}")
