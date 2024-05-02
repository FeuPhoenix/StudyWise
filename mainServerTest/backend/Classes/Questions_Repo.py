from datetime import datetime, timedelta
import os
import sys
import time
import uuid
import pdfplumber
import openai
import re
import random
import json
import textstat
from typing import List, Dict, Tuple, Optional
from Constants import OPENAI_API_KEY
from FirestoreDB import FirestoreDB
openai.api_key = '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'


MAX_TOKENS_PER_REQUEST = 4096  # Safe limit for tokens per request
user_points = 0  # Initialize user points
class Questions_Repo:
    output_mcqs_easy=""
    output_mcqs_medium=""
    output_mcqs_hard=""
    def __init__(self,filepath,Type):
        self.filepath=filepath
        self.ProcessedMaterial=filepath  
        self.Questions_id=uuid.uuid4().hex
        self.runMCQGenerator(self.ProcessedMaterial,Type)
    @staticmethod
    def read_text_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    @staticmethod
    def is_conceptually_relevant(question):
        non_conceptual_patterns = [
        r"\bwho\b", r"\bwhen\b", r"\bwhere\b", r"\bpublication\b",
        r"\bauthor\b", r"\bpublished\b", r"\bbook\b", r"\bISBN\b",
        r"\bedition\b", r"\bhistory\b", r"\bhistorical\b",
        ]
        return not any(re.search(pattern, question.lower()) for pattern in non_conceptual_patterns)
    @staticmethod
    def clean_paragraph(text):
        lines = text.split('\n')
        cleaned_lines = [line for line in lines if len(line) > 30 and not re.search(r'^\s*\d+\s*$', line) and not re.search(r'http[s]?://', line)]
        cleaned_text = '\n'.join(cleaned_lines)
        return cleaned_text
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Cleans and prepares the text for processing.
        """
        # Remove references, special characters, and extra whitespace
        text = re.sub(r'\[\d+\]', '', text)  # Remove citation references like [1], [2], etc.
        text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with a single space
        return text.strip()
    @staticmethod
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
    @staticmethod
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
    @staticmethod
    def determine_difficulty(text: str) -> str:
        # Calculate readability scores and text metrics
        flesch_score = textstat.flesch_reading_ease(text)
        fog_index = textstat.gunning_fog(text)
        complex_word_density = textstat.difficult_words(text) / textstat.lexicon_count(text) * 100
        sentence_complexity = textstat.sentence_count(text) / textstat.lexicon_count(text) * 100

        # Define thresholds for difficulty levels (these can be adjusted based on further analysis or requirements)
        if flesch_score > 70 and fog_index < 8 and complex_word_density < 5 and sentence_complexity < 15:
            return 'easy'
        elif flesch_score > 50 and fog_index < 12 and complex_word_density < 10 and sentence_complexity < 20:
            return 'medium'
        else:
            return 'hard'
    @staticmethod
    def update_user_points(correct):
        global user_points
        if correct:
            user_points += 10  # Increase points for a correct answer
        else:
            user_points -= 5  # Decrease points for an incorrect answer (optional)
        user_points = max(user_points, 0)  # Ensure points don't go negative
    @staticmethod
    def determine_difficulty(text):
        difficulty_score = textstat.flesch_reading_ease(text)

        if difficulty_score > 60:
            return 'easy'
        elif difficulty_score > 30:
            return 'medium'
        else:
            return 'hard'
    @staticmethod
    def extract_paragraphs_from_pdf(pdf_path):
        paragraphs = {'easy': [], 'medium': [], 'hard': []}
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        clean_text = Questions_Repo.clean_paragraph(text)
                        for paragraph in clean_text.split('\n'):
                            difficulty = Questions_Repo.determine_difficulty(paragraph)
                            paragraphs[difficulty].append(paragraph)
            print(f"Extracted paragraphs from PDF.")
        except Exception as e:
            print(f"Error extracting paragraphs from PDF: {e}")
        return paragraphs
    @staticmethod
    def generate_mcqs(paragraphs, difficulty):
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
                    if len(question_parts) >= 5 and Questions_Repo.is_conceptually_relevant(question_parts[0]):
                        options, correct_index = Questions_Repo.shuffle_options(question_parts[1:5])
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
    @staticmethod
    def shuffle_options(options):
        correct_index = 0  # Assuming the first option is correct
        random.shuffle(options)  # Shuffle options
        new_index = options.index(options[correct_index])  # Find the new index of the correct option
        return options, new_index
    @staticmethod
    def save_mcqs_to_file(mcqs, filepath):
        with open(filepath, 'w') as file:
            json.dump(mcqs, file, indent=4)
        print(f"MCQs saved to {filepath}")

    def runMCQGenerator(self,file_path,Type):
      if Type!="Transcript":
        if not os.path.isfile(file_path):
            print(f"The file does not exist at the specified path: {file_path}")
            return

        paragraphs =Questions_Repo.extract_paragraphs_from_pdf(file_path)
        for difficulty in ['easy', 'medium', 'hard']:
            if paragraphs[difficulty]:
                mcqs = Questions_Repo.generate_mcqs(paragraphs, difficulty)
                if mcqs:
                    output_path = f'assets/output_files/mcq/{difficulty}.json'
                    if not os.path.isfile(output_path):
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    Questions_Repo.save_mcqs_to_file(mcqs, output_path)
                else:
                    print(f"No {difficulty} MCQs were generated.")
            else:
                print(f"No {difficulty} content extracted from the file.")
        self.output_mcqs_easy = 'assets/output_files/mcq/easy.json'
        self.output_mcqs_medium = 'assets/output_files/mcq/medium.json'
        self.output_mcqs_hard = 'assets/output_files/mcq/hard.json'

        if not os.path.exists(self.output_mcqs_easy):
            output_mcqs_easy = None

        if not os.path.exists(self.output_mcqs_medium):
            output_mcqs_medium = None

        if not os.path.exists(self.output_mcqs_hard):
            output_mcqs_hard = None
        self.addQuestionsToFirestore()
        self.get_Questions_from_firestore()
      else:
          pass
            
    @staticmethod
    def getUser_level_from_Firestore(ID):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        user_doc_ref = firestore_instance.collection('Users').document(ID)

        # Get the document snapshot
        doc_snapshot = user_doc_ref.get()

        # Check if the document exists
        if doc_snapshot.exists:
            # Get the data of the document
            user_data = doc_snapshot.to_dict()
            
            # Get the value of the User_Level field
            user_level = user_data.get('User_Level')

            # Print the data of the document
            print("User data retrieved from Firestore:")
            print(user_data)

            # Return the User_Level value
            return user_level
        else:
            # If no document is found for the user's ID
            print(f"No document found for user with ID {ID} in Firestore.")
            return None
    @staticmethod
    def updateUserLevelInFirestore(user_id, new_level):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        user_doc_ref = firestore_instance.collection('Users').document(user_id)

        # Get the document snapshot
        doc_snapshot = user_doc_ref.get()

        # Check if the document exists
        if doc_snapshot.exists:
            # Update the user's level in Firestore
            user_doc_ref.update({'User_Level': new_level})
            print(f"User level updated to {new_level} for user with ID {user_id} in Firestore.")
        else:
            # If no document is found for the user's ID
            print(f"No document found for user with ID {user_id} in Firestore.")
    def upload_material_to_storage(self,user_id, material_name, output_mcqs_easy, output_mcqs_medium, output_mcqs_hard):
        db_instance = FirestoreDB.get_instance()
        storage_instance = db_instance.get_storage_instance()

        # Constructing the full path for the folder using the material name
        folder_path = f"user/{user_id}/Uploaded Materials/{material_name}/"

        # Creating a folder with the material name as the folder name
        folder_blob = storage_instance.blob(folder_path)
        folder_blob.upload_from_string('')  # Upload an empty string to create the folder

        output_mcqs_medium_blob_path = folder_path  +"output_mcqs_medium.json"
        output_mcqs_medium_blob = storage_instance.blob(output_mcqs_medium_blob_path)
        output_mcqs_medium_blob.upload_from_filename(output_mcqs_medium,timeout=600)

        output_mcqs_hard_blob_path = folder_path  +"output_mcqs_hard.json"
        output_mcqs_hard_blob = storage_instance.blob(output_mcqs_hard_blob_path,timeout=600)
        output_mcqs_hard_blob.upload_from_filename(output_mcqs_hard)

        output_mcqs_easy_blob_path = folder_path  +"output_mcqs_easy.json"
        output_mcqs_easy_blob = storage_instance.blob(output_mcqs_easy_blob_path,timeout=600)
        output_mcqs_easy_blob.upload_from_filename(output_mcqs_easy)
        
        expiration = datetime.now() + timedelta(days=36500)
        # download_urls = {
        #     "material_url": material_blob.generate_signed_url(expiration=expiration),
        #     "text_url": text_blob.generate_signed_url(expiration=expiration),
        #     "summary_url": summary_blob.generate_signed_url(expiration=expiration)
        # }

        print("Successfully uploaded material to Storage")
        return output_mcqs_easy_blob.generate_signed_url(expiration=expiration),output_mcqs_medium_blob.generate_signed_url(expiration=expiration),output_mcqs_hard_blob.generate_signed_url(expiration=expiration)
    @staticmethod
    def getFileNameFromPathWithOutExtension(input_string):
        last_slash_index = input_string.rfind('/')
        result_string = input_string[last_slash_index + 1:]
        result_string=result_string.replace('.mp4','')
        result_string=result_string.replace('.docx','')
        result_string=result_string.replace('.doc','')
        result_string=result_string.replace('.pptx','')
        result_string=result_string.replace('.ppt','')
        result_string=result_string.replace('.pdf','')
        result_string=result_string.replace('.json','')
        result_string=result_string.replace('.txt','')
        return result_string
    def addQuestionsToFirestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id
        
        Questions_easy_location,Questions_medium_location,Questions_hard_location=self.upload_material_to_storage("13ffe4704e2d423ea7751cb88d599db7",Questions_Repo.getFileNameFromPathWithOutExtension(self.ProcessedMaterial),self.output_mcqs_easy,self.output_mcqs_medium,self.output_mcqs_hard)
        Questions_medium_location,Questions_hard_location

        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id
        try:
            doc_ref=firestore_instance.collection('Users').document('13ffe4704e2d423ea7751cb88d599db7').collection('DocumentMaterial').document("rmk3SGTciwNRdo9pT4CO").collection('Questions').document(self.Questions_id).set({

                "Questions_easy_location": Questions_easy_location,
                "Questions_medium_location": Questions_medium_location,
                "Questions_hard_location": Questions_hard_location,
            })
            print("Successfully added processed material to firestore")
        except Exception as e:
            print(e)
    def get_Questions_from_firestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
        # Reference to the document
            doc_ref = firestore_instance.collection('Users').document('13ffe4704e2d423ea7751cb88d599db7') \
                .collection('DocumentMaterial').document("rmk3SGTciwNRdo9pT4CO") \
                .collection('Questions').document(self.Questions_id)
            
            # Get the document snapshot
            doc = doc_ref.get()
            
            # Check if the document exists
            if doc.exists:
                # Get the data from the document
                data = doc.to_dict()
                print("Questions Data:", data)  # Print the data

                return data
            else:
                print("Document does not exist")
                return None
        except Exception as e:
            print("Error:", e)
            return None
    def get_easy_Questions_from_firestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
        # Reference to the document
            doc_ref = firestore_instance.collection('Users').document('13ffe4704e2d423ea7751cb88d599db7') \
                .collection('DocumentMaterial').document("rmk3SGTciwNRdo9pT4CO") \
                .collection('Questions').document(self.Questions_id)
            
            # Get the document snapshot
            doc = doc_ref.get()
            
            # Check if the document exists
            if doc.exists:
                # Get the data from the document
                data = doc.to_dict()
                print("Questions Data:", data)  # Print the data
                specific_attribute = data.get('Questions_easy_location')
                return specific_attribute
            else:
                print("Document does not exist")
                return None
        except Exception as e:
            print("Error:", e)
            return None
    def get_medium_Questions_from_firestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
        # Reference to the document
            doc_ref = firestore_instance.collection('Users').document('13ffe4704e2d423ea7751cb88d599db7') \
                .collection('DocumentMaterial').document("rmk3SGTciwNRdo9pT4CO") \
                .collection('Questions').document(self.Questions_id)
            
            # Get the document snapshot
            doc = doc_ref.get()
            
            # Check if the document exists
            if doc.exists:
                # Get the data from the document
                data = doc.to_dict()
                specific_attribute = data.get('Questions_medium_location')
                return specific_attribute
            else:
                print("Document does not exist")
                return None
        except Exception as e:
            print("Error:", e)
            return None
    def get_hard_Questions_from_firestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
        # Reference to the document
            doc_ref = firestore_instance.collection('Users').document('13ffe4704e2d423ea7751cb88d599db7') \
                .collection('DocumentMaterial').document("rmk3SGTciwNRdo9pT4CO") \
                .collection('Questions').document(self.Questions_id)
            
            # Get the document snapshot
            doc = doc_ref.get()
            
            # Check if the document exists
            if doc.exists:
                # Get the data from the document
                data = doc.to_dict()
                specific_attribute = data.get('Questions_hard_location')
                return specific_attribute
            else:
                print("Document does not exist")
                return None
        except Exception as e:
            print("Error:", e)
            return None
