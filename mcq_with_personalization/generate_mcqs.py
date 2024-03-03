import os
import pdfplumber
import openai
import re
import random
import json
import textstat
import time
from typing import List, Dict, Tuple, Optional
openai.api_key = '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'

MAX_TOKENS_PER_REQUEST = 4096  
user_points = 0  # Initialize user points

def is_conceptually_relevant(question):
    non_conceptual_patterns = [
        r"\bwho\b", r"\bwhen\b", r"\bwhere\b", r"\bpublication\b",
        r"\bauthor\b", r"\bpublished\b", r"\bbook\b", r"\bISBN\b",
        r"\bedition\b", r"\bhistory\b", r"\bhistorical\b",
    ]
    return not any(re.search(pattern, question.lower()) for pattern in non_conceptual_patterns)

def clean_paragraph(text):
    lines = text.split('\n')
    cleaned_lines = [line for line in lines if len(line) > 30 and not re.search(r'^\s*\d+\s*$', line) and not re.search(r'http[s]?://', line)]
    cleaned_text = '\n'.join(cleaned_lines)
    return cleaned_text

def clean_text(text: str) -> str:
    """
    Cleans and prepares the text for processing.
    """
    # Remove references, special characters, and extra whitespace
    text = re.sub(r'\[\d+\]', '', text)  # Remove citation references like [1], [2], etc.
    text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
    return text.strip()

def split_text(text: str, max_length: int = 1000) -> List[str]:
    """
    Splits the text into chunks that are small enough for the model to process.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) < max_length and sentence not in current_chunk:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def generate_questions(text: str, model: str = "text-davinci-003", temperature: float = 0.7) -> List[str]:
    """
    Generates questions from the given text using the specified model.
    """
    try:
        response = openai.Completion.create(
            engine=model,
            prompt=text,
            temperature=temperature,
            max_tokens=100,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n", " Human:", " AI:"]
        )
        return response.choices[0].text.strip().split('\n')
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def determine_difficulty(paragraph):
    # Example logic based on paragraph length
    length = len(paragraph)
    if length < 500: return 'easy'
    elif length < 1000: return 'medium'
    else: return 'hard'

def update_user_points(correct):
    global user_points
    if correct:
        user_points += 10  # Increase points for a correct answer
    else:
        user_points -= 5  # Decrease points for an incorrect answer (optional)
    user_points = max(user_points, 0)  # Ensure points don't go negative

def determine_difficulty(text):
    difficulty_score = textstat.flesch_reading_ease(text)

    if difficulty_score > 60:
        return 'easy'
    elif difficulty_score > 30:
        return 'medium'
    else:
        return 'hard'

def extract_paragraphs_from_pdf(pdf_path):
    paragraphs = {'easy': [], 'medium': [], 'hard': []}
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    clean_text = clean_paragraph(text)
                    for paragraph in clean_text.split('\n'):
                        difficulty = determine_difficulty(paragraph)
                        paragraphs[difficulty].append(paragraph)
        print(f"Extracted paragraphs from PDF.")
    except Exception as e:
        print(f"Error extracting paragraphs from PDF: {e}")
    return paragraphs

def generate_mcqs_with_chatgpt(paragraphs, difficulty):
    mcqs = []
    batched_paragraphs = []
    current_batch = ""

    # Adjust the base prompt based on the difficulty level
    if difficulty == 'easy':
        base_prompt = "Generate 10 easy multiple-choice questions that are straightforward and simple, focusing on basic concepts."
    elif difficulty == 'medium':
        base_prompt = "Generate 10 medium-difficulty multiple-choice questions that require a moderate level of understanding and may involve more detailed concepts."
    else:  # hard
        base_prompt = "Generate 10 hard multiple-choice questions that are complex, requiring in-depth understanding and critical thinking to answer."

    for paragraph in paragraphs[difficulty]:
        if len(current_batch) + len(paragraph) < MAX_TOKENS_PER_REQUEST:
            current_batch += f"{paragraph}\n\n"
        else:
            batched_paragraphs.append(current_batch)
            current_batch = f"{paragraph}\n\n"
    
    if current_batch:
        batched_paragraphs.append(current_batch)

    for batch in batched_paragraphs:
        user_prompt = {"role": "user", "content": base_prompt + ": " + batch}
        try:
            response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[user_prompt])
            response_text = response['choices'][0]['message']['content'].strip()
            potential_mcqs = response_text.split('\n\n')
            for mcq in potential_mcqs:
                question_parts = mcq.split('\n')
                if len(question_parts) >= 5 and is_conceptually_relevant(question_parts[0]):
                    options, correct_index = shuffle_options(question_parts[1:5])
                    mcqs.append({
                        'question': question_parts[0],
                        'options': options,
                        'correct_answer': options[correct_index]
                    })
        except openai.error.RateLimitError:
                print("Rate limit exceeded, waiting before retrying...")
                time.sleep(20)
        except openai.OpenAIError as e:
            print(f"OpenAI API error: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

    print(f"Generated {len(mcqs)} {difficulty} MCQs.")
    return mcqs

def shuffle_options(options):
    correct_index = 0  # Assuming the first option is correct
    random.shuffle(options)  # Shuffle options
    new_index = options.index(options[correct_index])  # Find the new index of the correct option
    return options, new_index

def save_mcqs_to_file(mcqs, filepath):
    with open(filepath, 'w') as file:
        json.dump(mcqs, file, indent=4)
    print(f"MCQs saved to {filepath}")

def runMCQGenerator():
    file_path = input("Enter the path to the PDF file: ")
    if not os.path.isfile(file_path):
        print(f"The file does not exist at the specified path: {file_path}")
        return

    paragraphs = extract_paragraphs_from_pdf(file_path)
    for difficulty in ['easy', 'medium', 'hard']:
        if paragraphs[difficulty]:
            mcqs = generate_mcqs_with_chatgpt(paragraphs, difficulty)
            if mcqs:
                output_path = f'output_mcqs_{difficulty}.json'
                save_mcqs_to_file(mcqs, output_path)
            else:
                print(f"No {difficulty} MCQs were generated.")
        else:
            print(f"No {difficulty} content extracted from the file.")

if __name__ == "__main__":
    runMCQGenerator()
