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
from typing import List
from langdetect import detect
from dotenv import load_dotenv
load_dotenv()
from backend.Classes.FirestoreDB import FirestoreDB
# from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST
# from FirestoreDB import FirestoreDB

MAX_TOKENS_PER_REQUEST = int(os.getenv('MAX_TOKENS_PER_REQUEST'))

openai.api_key = os.getenv('OPENAI_API_KEY')


user_points = 0  # Initialize user points
class Questions_Repo:

    def __init__(self,filepath,userid,materialid,Type):
        self.filepath=filepath
        self.ProcessedMaterial=filepath  
        self.Questions_id=uuid.uuid4().hex
        self.userid=userid
        self.materialid=materialid
        self.runMCQGenerator(self.ProcessedMaterial,Type)
    @staticmethod
    def clean_mcq(text):
            """Cleans the input text by removing specific leading patterns."""
            return re.sub(r"^(Q:|A:|\s*\-\s*|\s*\d+\.\s*|\s*\d+\-\s*|[A-Za-z]\.\s*|[A-Za-z]\)\s*|\s*\d+\)\s*)", "", text)
    @staticmethod
    def post_process_questions(mcq):
        """Post-processes a list of questions to clean up the text."""
        for question_data in mcq:
            # Clean the question text
            question_data['question'] = Questions_Repo.clean_mcq(question_data['question'])
            
            # Clean each option in the options list
            question_data['options'] = [Questions_Repo.clean_mcq(option) for option in question_data['options']]
            
            # Clean the correct answer
            question_data['correct_answer'] = Questions_Repo.clean_mcq(question_data['correct_answer'])
            
        return mcq

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
    def detect_language(text):
        return detect(text)
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
      if Type!="TRANSCRIPT":
            if not os.path.isfile(file_path):
                print(f"The file does not exist at the specified path: {file_path}")
                return

            paragraphs =Questions_Repo.extract_paragraphs_from_pdf(file_path)
            for difficulty in ['easy', 'medium', 'hard']:
                if paragraphs[difficulty]:
                    mcqs = Questions_Repo.generate_mcqs(paragraphs, difficulty)
                    mcqs=Questions_Repo.post_process_questions(mcqs)


                    
                    if mcqs:
                        output_path = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+difficulty+'.json'
                        output_path = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+difficulty+'.json'
                        if not os.path.isfile(output_path):
                            os.makedirs(os.path.dirname(output_path), exist_ok=True)
                        Questions_Repo.save_mcqs_to_file(mcqs, output_path)
                    else:
                        print(f"No {difficulty} MCQs were generated.")
                else:
                    print(f"No {difficulty} content extracted from the file.")
            self.output_mcqs_easy = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'easy.json'
            self.output_mcqs_medium = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'medium.json'
            self.output_mcqs_hard = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'hard.json'
            self.output_mcqs_easy = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'easy.json'
            self.output_mcqs_medium = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'medium.json'
            self.output_mcqs_hard = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'hard.json'

            if not os.path.exists(self.output_mcqs_easy):
                self.output_mcqs_easy = None

            if not os.path.exists(self.output_mcqs_medium):
                self.output_mcqs_medium = None

            if not os.path.exists(self.output_mcqs_hard):
                self.output_mcqs_hard = None
            self.addDocumentQuestionsToFirestore()
            # Questions_Repo.close_file_if_open("mainServerTest/assets/input_files/text-based/"+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+".pdf")
            # Questions_Repo.close_file_if_open("mainServerTest/assets/input_files/text-based/"+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+".pdf")
            # Questions_Repo.close_file_if_open("mainServerTest/assets/output_files/text_files/"+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+".txt")
            # Questions_Repo.close_file_if_open("mainServerTest/assets/output_files/text_files/"+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+".txt")    
   
  
      else:
        transcript_text = self.read_text_file(file_path)
        cleaned_transcript = Questions_Repo.clean_text(transcript_text)
        paragraphs = Questions_Repo.split_text(cleaned_transcript)

        transcript_paragraphs = {'easy': [], 'medium': [], 'hard': []}
        for paragraph in paragraphs:
            difficulty = Questions_Repo.determine_difficulty(paragraph)
            transcript_paragraphs[difficulty].append(paragraph)
        
        for difficulty in ['easy', 'medium', 'hard']:
            if transcript_paragraphs[difficulty]:
                mcqs = Questions_Repo.generate_mcqs(transcript_paragraphs, difficulty)
                print("MCQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ",mcqs)
                mcqs=Questions_Repo.post_process_questions(mcqs)
                if mcqs:
                   
                    output_path = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+difficulty+'_transcript.json'
                    output_path = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+difficulty+'_transcript.json'
                    if not os.path.isfile(output_path):
                        os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    Questions_Repo.save_mcqs_to_file(mcqs, output_path)
                else:
                    print(f"No {difficulty} MCQs were generated for the transcript.")
            else:
                print(f"No {difficulty} content extracted from the transcript.")
            
            self.output_mcqs_easy = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'easy_transcript.json'
            self.output_mcqs_medium = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'medium_transcript.json'
            self.output_mcqs_hard = 'mainServerTest/assets/output_files/mcq/'+Questions_Repo.getFileNameFromPathWithOutExtension(file_path)+'hard_transcript.json'            
            
            if not os.path.exists(self.output_mcqs_easy):
               self.output_mcqs_easy = None

            if not os.path.exists(self.output_mcqs_medium):
                self.output_mcqs_medium = None

            if not os.path.exists(self.output_mcqs_hard):
                self.output_mcqs_hard = None
            self.addVideoQuestionsToFirestore()

             
    
 
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
        expiration = datetime.now() + timedelta(days=36500)
        # Constructing the full path for the folder using the material name
        folder_path = f"user/{user_id}/Uploaded Materials/{material_name}/"

        # Creating a folder with the material name as the folder name
        folder_blob = storage_instance.blob(folder_path)
        folder_blob.upload_from_string('')  # Upload an empty string to create the folder
        if output_mcqs_medium is not None:
            output_mcqs_medium_blob_path = folder_path  +"output_mcqs_medium.json"
            output_mcqs_medium_blob = storage_instance.blob(output_mcqs_medium_blob_path)
            output_mcqs_medium_blob.upload_from_filename(output_mcqs_medium,timeout=600)
            link_m=output_mcqs_medium_blob.generate_signed_url(expiration=expiration)
        else:
            link_m=None
        if output_mcqs_hard is not None:
            output_mcqs_hard_blob_path = folder_path  +"output_mcqs_hard.json"
            output_mcqs_hard_blob = storage_instance.blob(output_mcqs_hard_blob_path)
            output_mcqs_hard_blob.upload_from_filename(output_mcqs_hard,timeout=600)
            link_h=output_mcqs_hard_blob.generate_signed_url(expiration=expiration)
        else:
            link_h=None
        if output_mcqs_easy is not None:
            output_mcqs_easy_blob_path = folder_path  +"output_mcqs_easy.json"
            output_mcqs_easy_blob = storage_instance.blob(output_mcqs_easy_blob_path)
            output_mcqs_easy_blob.upload_from_filename(output_mcqs_easy,timeout=600)
            link_E=output_mcqs_easy_blob.generate_signed_url(expiration=expiration)
        else:
            link_E=None
        


        print("Successfully uploaded material to Storage")
        return link_E,link_m,link_h
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
    def addVideoQuestionsToFirestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id
        
        Questions_easy_location,Questions_medium_location,Questions_hard_location=self.upload_material_to_storage(self.userid,Questions_Repo.getFileNameFromPathWithOutExtension(self.ProcessedMaterial),self.output_mcqs_easy,self.output_mcqs_medium,self.output_mcqs_hard)
        Questions_medium_location,Questions_hard_location

        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id
        try:
            # doc_ref=firestore_instance.collection('Users').document(self.userid).collection('VideoMaterial').document(self.materialid).collection('Questions').document(self.Questions_id).set({
            doc_ref=firestore_instance.collection('Users').document(self.userid).collection('VideoMaterial').document(self.materialid).collection('Questions').document(self.Questions_id).set({

                "Questions_easy_location": Questions_easy_location,
                "Questions_medium_location": Questions_medium_location,
                "Questions_hard_location": Questions_hard_location,
            })
            print("Successfully added processed material to firestore")
        except Exception as e:
            print(e)

    def addDocumentQuestionsToFirestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id
        
        Questions_easy_location,Questions_medium_location,Questions_hard_location=self.upload_material_to_storage(self.userid,Questions_Repo.getFileNameFromPathWithOutExtension(self.ProcessedMaterial),self.output_mcqs_easy,self.output_mcqs_medium,self.output_mcqs_hard)
        Questions_medium_location,Questions_hard_location

        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id
        try:
            doc_ref=firestore_instance.collection('Users').document(self.userid).collection('DocumentMaterial').document(self.materialid).collection('Questions').document(self.Questions_id).set({

                "Questions_easy_location": Questions_easy_location,
                "Questions_medium_location": Questions_medium_location,
                "Questions_hard_location": Questions_hard_location,
            })
            print("Successfully added processed material to firestore")
        except Exception as e:
            print(e)
    @staticmethod
    def close_file_if_open(file_path):
        try:
                # Open the file to close it if it's open
                with open(file_path, 'r') as file:
                    file.close()
                    print(f"Closed the file {file_path} before deleting.")

                # Now delete the file
                os.remove(file_path)
                print(f"Deleted the file {file_path} successfully.")
        except FileNotFoundError:
                print(f"File {file_path} not found.")
        except Exception as e:
                print(f"An error occurred: {e}")
# if __name__ == "__main__":
#     Questions_Repo("mainServerTest/assets/input_files/text-based/test.pdf",None)