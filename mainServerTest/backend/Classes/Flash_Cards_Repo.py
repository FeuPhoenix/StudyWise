#needs to be improved
from datetime import datetime, timedelta
import os
import uuid
from langdetect import detect

from firebase_admin import firestore
import pdfplumber
import openai
import time
import json
import re

from backend.Classes.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
from backend.Classes.FirestoreDB import FirestoreDB # Assuming the Materials and Processed_Materials classes are defined in app.Studywise.Model

class Flash_Cards:
    def __init__(self,ProcessedMaterial,userid,materialid,content_type=''):
        openai.api_key = OPENAI_API_KEY
        self.content_type=content_type
        self.ProcessedMaterial=ProcessedMaterial 
        self.userid=userid
        self.materialid=materialid
        #self.db = FirestoreDB.get_instance()
        self.flashcard_id=uuid.uuid4().hex
        self.runFlashcards(self.ProcessedMaterial)
        if content_type=="TRANSCRIPT":
            self.add_FlashCards_Video_ToFirestore()
        

        else:
            self.addDocumentFlashCardsToFirestore()
        
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
   
    @staticmethod
    def upload_material_to_storage(user_id, material_name, flashcard_file_path):
        db_instance = FirestoreDB.get_instance()
        storage_instance = db_instance.get_storage_instance()

        # Constructing the full path for the folder using the material name
        folder_path = f"user/{user_id}/Uploaded Materials/{material_name}/"

        # Creating a folder with the material name as the folder name
        folder_blob = storage_instance.blob(folder_path)
        folder_blob.upload_from_string('')  # Upload an empty string to create the folder

        # Upload the material file inside the folder
        flashcard_blob_path = folder_path + "flashcards"
        flashcard_blob = storage_instance.blob(flashcard_blob_path)
        flashcard_blob.upload_from_filename(flashcard_file_path,timeout=600)
    
        expiration = datetime.now() + timedelta(days=36500)


        print("Successfully uploaded material to Storage")
        return flashcard_blob.generate_signed_url(expiration=expiration)
    def add_FlashCards_Video_ToFirestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        flash_card_location = Flash_Cards.upload_material_to_storage(
            self.userid,
            Flash_Cards.getFileNameFromPathWithOutExtension(self.ProcessedMaterial),
            self.Flashcards
        )
        
        try:
            # Reference to the FlashCards collection
            collection_ref = firestore_instance.collection('Users').document(self.userid).collection('VideoMaterial').document(self.materialid).collection('FlashCards')

            # Fetch all existing documents in the collection
            existing_docs = collection_ref.get()
            
            # Delete each existing document
            for doc in existing_docs:
                doc_ref = collection_ref.document(doc.id)
                doc_ref.delete()
            
            # Add the new document to the collection
            doc_ref = collection_ref.document(self.flashcard_id)
            doc_ref.set({
                "flash_card_location": flash_card_location,
            })
            print("Successfully added processed material to Firestore")
        except Exception as e:
            print(e)

    def addDocumentFlashCardsToFirestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        flash_card_location = Flash_Cards.upload_material_to_storage(
            self.userid,
            Flash_Cards.getFileNameFromPathWithOutExtension(self.ProcessedMaterial),
            self.Flashcards
        )
        
        try:
            # Reference to the FlashCards collection
            collection_ref = firestore_instance.collection('Users').document(self.userid).collection('DocumentMaterial').document(self.materialid).collection('FlashCards')

            # Fetch all existing documents in the collection
            existing_docs = collection_ref.get()
            
            # Delete each existing document
            for doc in existing_docs:
                doc_ref = collection_ref.document(doc.id)
                doc_ref.delete()
            
            # Add the new document to the collection
            doc_ref = collection_ref.document(self.flashcard_id)
            doc_ref.set({
                "flash_card_location": flash_card_location,
            })
            print("Successfully added processed material to Firestore")
        except Exception as e:
            print(e)
    @classmethod
    def fromJson(cls, data, processed_material):
        # Assuming you also want to pass a Processed_Materials object when creating from JSON
        return cls(
            flashcard_id=data.get("flashcard_id", ""),
         # Pass the Processed_Materials object here
        )

    def toJson(self):
        return {
            "flashcard_id": self.flashcard_id,
            
            
        }
    def is_conceptually_relevant(self,question):
        # Patterns for non-conceptual questions
        non_conceptual_patterns = [
            r"\bwho\b",  # Who authored, who developed
            r"\bwhen\b",  # When was it published/developed
            r"\bwhere\b",  # Where was it published
            r"\bpublication\b",
            r"\bauthor\b",
            r"\bpublished\b",
            r"\bbook\b",
            r"\bISBN\b",
            r"\bedition\b",
            r"\bhistory\b",
            r"\bhistorical\b",
            # Add more patterns as needed
        ]
        return not any(re.search(pattern, question.lower()) for pattern in non_conceptual_patterns)
    def is_conceptually_relevant_Arabic(self, question):
        # Patterns for non-conceptual questions in Arabic
        non_conceptual_patterns = [
            r"\bمن\b",  # Who authored, who developed (من كتب, من طور)
            r"\bمتى\b",  # When was it published/developed
            r"\bأين\b",  # Where was it published
            r"\bنشر\b",
            r"\bمؤلف\b",
            r"\bتاريخ\b",
            r"\bكتاب\b",
            r"\bISBN\b",
            r"\bإصدار\b",
            r"\bتاريخي\b",
            r"\bتاريخية\b",
            # Add more patterns as needed
        ]
        return not any(re.search(pattern, question.lower()) for pattern in non_conceptual_patterns)
    def extract_paragraphs_from_pdf(self,pdf_path):
        paragraphs = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    paragraphs.extend(text.split('\n'))
        return paragraphs

    def extract_and_split_text(self,txt_path, max_length=16000):
        paragraphs = []
        with open(txt_path, 'r',errors='ignore') as file:
            for paragraph in file.read().split('\n\n'):
                trimmed_paragraph = paragraph.strip()
                if len(trimmed_paragraph) > 0:
                    if len(trimmed_paragraph) > max_length:
                        segments = self.split_text_into_segments(trimmed_paragraph, max_length)
                        paragraphs.extend(segments)
                    else:
                        paragraphs.append(trimmed_paragraph)
        return paragraphs

    def split_text_into_segments(self,text, max_length=16000):
        words = text.split(' ')
        segments = []
        current_segment = ''

        for word in words:
            if len(current_segment) + len(word) < max_length:
                current_segment += word + ' '
            else:
                last_period = current_segment.rfind('.')
                if last_period != -1 and (len(current_segment) - last_period) < 200:
                    segment_to_add = current_segment[:last_period + 1]
                    current_segment = current_segment[last_period + 2:] + word + ' '
                else:
                    segment_to_add = current_segment
                    current_segment = word + ' '
                segments.append(segment_to_add.strip())
        
        if current_segment:
            segments.append(current_segment.strip())

        return segments
    def generate_qa_pairs_arabic(self, paragraphs, content_type):
        qa_pairs = []
        batched_paragraphs = []
        current_batch = ""

        for paragraph in paragraphs:

            base_prompt = "قم بتوليد أسئلة وأجوبة تركز على المحتوى التقني والمفاهيمي لهذا النص. "

            transcript_note = "مع ملاحظة أن النص المقدم قد يحتوي على أخطاء نحوية أو منطقية بسبب عدم دقة تحويل الكلام إلى نص، يرجى التركيز على توليد أسئلة وأجوبة ذات صلة ومفهومة، وتجنب المحتوى الغامض. قم فقط بتوليد الأسئلة والأجوبة ذات الصلة بالنص التالي: " 
            pdf_note = "تجنب الأسئلة حول المؤلفين أو تواريخ النشر أو التطور التاريخي. لا تشير إلى المادة المقدمة لك على أنها 'هذا النص' أو 'النص'، بدلاً من ذلك، أشر إليها باسم الموضوع الحالي، ولا تعامل الأسئلة والأجوبة كما لو كانت حصرية لهذا النص، على سبيل المثال، لا تسأل عن ما يتحدث عنه هذا النص بالتحديد. يمكنك طرح أسئلة حول تعريفات الأشياء التي تم شرحها في النص: "

            if content_type.lower() == "pdf":
                note = pdf_note
            elif content_type.lower() == "transcript" or content_type.lower() == "video transcript":
                note = transcript_note
            elif content_type.lower() == "txt" or content_type.lower() == "text":
                note = ""
            else:
                note = ""

            if len(paragraph) > 20 and "http" not in paragraph:
                if len(current_batch) + len(paragraph) < MAX_TOKENS_PER_REQUEST:
                    current_batch += f"{paragraph}\n\n"
                else:
                    batched_paragraphs.append(current_batch)
                    current_batch = f"{paragraph}\n\n"
        
        if current_batch:
            batched_paragraphs.append(current_batch)

        for batch in batched_paragraphs:
            prompt_content = base_prompt + note
            system_prompt = {"role": "system", "content": "أنت مساعد ذكي ومفيد."}
            user_prompt = {"role": "user", "content": prompt_content + ": " + batch}

            print("This is the user prompt that will be sent: Prompt Content:\n" + prompt_content + "\nBatch:\n" + batch)

            prompt = [system_prompt, user_prompt]
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
                response_text = response.choices[0].message['content'].strip()
                potential_qa_pairs = response_text.split('\n\n')
                for pair in potential_qa_pairs:
                    question = pair.split('\n')[0]
                    if self.is_conceptually_relevant_Arabic(question):
                        qa_pairs.append(pair)
            except openai.error.RateLimitError:
                print("Rate limit reached, waiting for 30 seconds...")
                time.sleep(20)
                # Retry the request after waiting
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
                response_text = response.choices[0].message['content'].strip()
                potential_qa_pairs = response_text.split('\n\n')
                for pair in potential_qa_pairs:
                    question = pair.split('\n')[0]
                    if self.is_conceptually_relevant_Arabic(question):
                        qa_pairs.append(pair)

        return qa_pairs
    def generate_qa_pairs(self,paragraphs, content_type):
        qa_pairs = []
        batched_paragraphs = []
        current_batch = ""

        for paragraph in paragraphs:

            base_prompt = "Generate questions and answers focusing on the technical and conceptual content of this text. "

            transcript_note = "Noting that the text that will be given might contain grammatical or logical mistakes due to speech-to-text inaccuracies, please focus on generating conceptually relevant and clear questions and answers, avoiding ambiguous content. Only generate quesitons and answers relevant to the following text: " 
            pdf_note = "Avoiding questions about authors, publication dates, or historical development. Do not refer to the material you have been provided with as 'this text' or 'the text', instead, refer to it with the name of the topic at hand, and do not treat the questions & answers as they are exclusive to this text, for example, do not ask about what this text in particular is talking about. You can ask about definitions of things that were explained in the text: "


            if content_type.lower() == "pdf":
                note = pdf_note
            elif content_type.lower() == "transcript" or content_type.lower() == "video transcript":
                note = transcript_note
            elif content_type.lower() == "txt" or content_type.lower() == "text":
                note = ""
            else:
                note = ""

            if len(paragraph) > 20 and "http" not in paragraph:
                if len(current_batch) + len(paragraph) < MAX_TOKENS_PER_REQUEST:
                    current_batch += f"{paragraph}\n\n"
                else:
                    batched_paragraphs.append(current_batch)
                    current_batch = f"{paragraph}\n\n"
        
        if current_batch:
            batched_paragraphs.append(current_batch)

        for batch in batched_paragraphs:

            prompt_content = base_prompt + note
            system_prompt = {"role": "system", "content": "You are a helpful assistant."}
            user_prompt = {"role": "user", "content": prompt_content + ": " + batch}

            print("This is the user prompt that will be sent: Prompt Content:y\n" + prompt_content + "\nBatch:\n" + batch)

            prompt = [system_prompt, user_prompt]
            try:
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
                response_text = response.choices[0].message['content'].strip()
                potential_qa_pairs = response_text.split('\n\n')
                for pair in potential_qa_pairs:
                    question = pair.split('\n')[0]
                    if self.is_conceptually_relevant(question):
                        qa_pairs.append(pair)
            except openai.error.RateLimitError:
                print("Rate limit reached, waiting for 30 seconds...")
                time.sleep(20)
                # Retry the request after waiting
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
                response_text = response.choices[0].message['content'].strip()
                potential_qa_pairs = response_text.split('\n\n')
                for pair in potential_qa_pairs:
                    question = pair.split('\n')[0]
                    if self.is_conceptually_relevant(question):
                        qa_pairs.append(pair)

        return qa_pairs

    def format_flash_cards(self,qa_pairs):
        formatted_cards = []
        for pair in qa_pairs:
            if pair.count('\n') == 1:  # Expecting each pair to be two lines: question and answer
                question, answer = pair.split('\n')
                question = re.sub(r"^(Q:|A:|\s*\-\s*|\d+\.\s*|\d+\-\s*)", "", question)
                answer = re.sub(r"^(Q:|A:|\s*\-\s*|\d+\.\s*|\d+\-\s*)", "", answer)
                formatted_cards.append({'front': question.strip(), 'back': answer.strip()})
        return formatted_cards

    def filenameFromPath(self,filepath):
        parts = filepath.rsplit('/', 1)

        if len(parts) == 1: # If no '/' was found, return empty string
            return ""

        filename_parts = parts[-1].rsplit('.', 1)

        if len(filename_parts) == 1:
            return parts[-1]

        return filename_parts[0] # Return the filename alone (assuming it was between the last '/' and the last '.')

    # Example usage:
    @staticmethod
    def detect_language(text):
        return detect(text)
    def save_flash_cards_to_file(self,formatted_cards, filepath):
        with open(filepath, 'w') as file:
            json.dump(formatted_cards, file, indent=4)

    def runFlashcards(self,file_path, content_type = ''):
        content = []

        self.filename = self.filenameFromPath(file_path)
        output_path = 'assets/output_files/flashcards/'+self.filename+'.json'
        self.Flashcards = output_path

        if content_type == '':
            if file_path.endswith('.pdf'):
                content = self.extract_paragraphs_from_pdf(file_path)
                content_type = 'pdf'
            elif file_path.endswith('.txt'):
                content = self.extract_and_split_text(file_path)
                
            else:
                raise ValueError("Unsupported file type. Only .pdf or .txt files are currently accepted.")
        
        qa_pairs = self.generate_qa_pairs(content, content_type)
        formatted_cards = self.format_flash_cards(qa_pairs)
        self.save_flash_cards_to_file(formatted_cards, output_path)
        self.Flashcards=output_path
        print(f"Flash cards saved to {output_path}")
