import os
import pdfplumber
import openai
import re
import random
import json
import textstat
from typing import List, Dict, Tuple, Optional

from app.Studywise.Model import Questions_Repo
openai.api_key = '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'

MAX_TOKENS_PER_REQUEST = 4096  # Safe limit for tokens per request
user_points = 0  # Initialize user points
class QuestionController:
    def __init__(self,question_repo:Questions_Repo):
        pass

    def is_conceptually_relevant(self,question):
        non_conceptual_patterns = [
            r"\bwho\b", r"\bwhen\b", r"\bwhere\b", r"\bpublication\b",
            r"\bauthor\b", r"\bpublished\b", r"\bbook\b", r"\bISBN\b",
            r"\bedition\b", r"\bhistory\b", r"\bhistorical\b",
        ]
        return not any(re.search(pattern, question.lower()) for pattern in non_conceptual_patterns)

    def clean_paragraph(self,text):
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if len(line) > 30 and not re.search(r'^\s*\d+\s*$', line) and not re.search(r'http[s]?://', line)]
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text

    def clean_text(self,text: str) -> str:
        """
        Cleans and prepares the text for processing.
        """
        # Remove references, special characters, and extra whitespace
        text = re.sub(r'\[\d+\]', '', text)  # Remove citation references like [1], [2], etc.
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        return text.strip()

    def split_text(self,text: str, max_length: int = 1000) -> List[str]:
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

    def generate_questions(self,text: str, model: str = "text-davinci-003", temperature: float = 0.7) -> List[str]:
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

    def determine_difficulty(self,paragraph):
        # Example logic based on paragraph length
        length = len(paragraph)
        if length < 500: return 'easy'
        elif length < 1000: return 'medium'
        else: return 'hard'

    def update_user_points(self,correct):
        global user_points
        if correct:
            user_points += 10  # Increase points for a correct answer
        else:
            user_points -= 5  # Decrease points for an incorrect answer (optional)
        user_points = max(user_points, 0)  # Ensure points don't go negative

    def generate_mcqs_with_chatgpt(self,text: str, num_questions: int = 5, difficulty: str = 'mixed') -> List[Dict]:
        """
        Generates multiple-choice questions (MCQs) from the input text.
        """
        clean_text = clean_text(text)
        text_chunks = self.split_text(clean_text)
        mcqs = []

        for chunk in text_chunks:
            # Adjust the prompt based on the desired difficulty level
            prompt_difficulty = {
                'easy': 'Create easy multiple-choice questions and answers from the following text:',
                'medium': 'Create medium-difficulty multiple-choice questions and answers from the following text:',
                'hard': 'Create hard multiple-choice questions and answers from the following text:',
                'mixed': 'Create multiple-choice questions and answers from the following text:'
            }.get(difficulty, 'mixed')

            prompt_text = f"{prompt_difficulty}\n{chunk}"

            # Generate questions from the chunk
            questions = self.generate_questions(prompt_text)

            # Extract MCQs from the generated questions
            for question in questions:
                if len(mcqs) < num_questions:
                    mcq = {
                        'question': None,
                        'options': [],
                        'answer': None
                    }
                    lines = question.split('\n')
                    if lines:
                        mcq['question'] = lines[0]
                        for line in lines[1:]:
                            option_match = re.match(r'^[A-D]\. (.+)$', line)
                            if option_match:
                                mcq['options'].append(option_match.group(1))
                            if line.startswith('*'):
                                mcq['answer'] = line[3:]  # Remove '* ' from the beginning
                    if mcq['question'] and mcq['options'] and mcq['answer']:
                        mcqs.append(mcq)
                else:
                    break
            if len(mcqs) >= num_questions:
                break

        return mcqs

    def determine_difficulty(self,text):
        difficulty_score = textstat.flesch_reading_ease(text)

        if difficulty_score > 60:
            return 'easy'
        elif difficulty_score > 30:
            return 'medium'
        else:
            return 'hard'

    def extract_paragraphs_from_pdf(self,pdf_path):
        paragraphs = {'easy': [], 'medium': [], 'hard': []}
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        clean_text = self.clean_paragraph(text)
                        for paragraph in clean_text.split('\n'):
                            difficulty = self.determine_difficulty(paragraph)
                            paragraphs[difficulty].append(paragraph)
            print(f"Extracted paragraphs from PDF.")
        except Exception as e:
            print(f"Error extracting paragraphs from PDF: {e}")
        return paragraphs

    def generate_mcqs_with_chatgpt(self,paragraphs, difficulty):
        mcqs = []
        batched_paragraphs = []
        current_batch = ""

        # Adjust the base prompt based on the difficulty level
        if difficulty == 'easy':
            base_prompt = "Generate easy multiple-choice questions that are straightforward and simple, focusing on basic concepts."
        elif difficulty == 'medium':
            base_prompt = "Generate medium-difficulty multiple-choice questions that require a moderate level of understanding and may involve more detailed concepts."
        else:  # hard
            base_prompt = "Generate hard multiple-choice questions that are complex, requiring in-depth understanding and critical thinking to answer."

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
                    if len(question_parts) >= 5 and self.is_conceptually_relevant(question_parts[0]):
                        options, correct_index = self.shuffle_options(question_parts[1:5])
                        mcqs.append({
                            'question': question_parts[0],
                            'options': options,
                            'correct_answer': options[correct_index]
                        })
            except openai.OpenAIError as e:
                print(f"OpenAI API error: {e}")
            except Exception as e:
                print(f"An unexpected error occurred: {e}")

        print(f"Generated {len(mcqs)} {difficulty} MCQs.")
        return mcqs

    def shuffle_options(self,options):
        correct_index = 0  # Assuming the first option is correct
        random.shuffle(options)  # Shuffle options
        new_index = options.index(options[correct_index])  # Find the new index of the correct option
        return options, new_index

    def save_mcqs_to_file(self,mcqs, filepath):
        with open(filepath, 'w') as file:
            json.dump(mcqs, file, indent=4)
        print(f"MCQs saved to {filepath}")

    def runMCQGenerator(self):
        file_path="assets/input_files/text-based/test.pdf"
        if not os.path.isfile(file_path):
            print(f"The file does not exist at the specified path: {file_path}")
            return

        paragraphs = self.extract_paragraphs_from_pdf(file_path)
        for difficulty in ['easy', 'medium', 'hard']:
            if paragraphs[difficulty]:
                mcqs = self.generate_mcqs_with_chatgpt(paragraphs, difficulty)
                if mcqs:
                    output_path = f'output_mcqs_{difficulty}.json'
                    self.save_mcqs_to_file(mcqs, output_path)
                else:
                    print(f"No {difficulty} MCQs were generated.")
            else:
                print(f"No {difficulty} content extracted from the file.")

    if __name__ == "__main__":
        runMCQGenerator()