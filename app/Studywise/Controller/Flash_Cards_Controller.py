import pdfplumber
import openai
import time
import json
import re
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 

class FlashcardsController:
    # openai_api_key = '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'
    # openai_api_key = openai_api_key
    # openai.api_key = self.openai_api_key
    # max_tokens_per_request = 1000 
    def __init__(self, openai_api_key):
        self.openai_api_key = openai_api_key
        openai.api_key = self.openai_api_key
        self.max_tokens_per_request = 1000  # Safe limit for tokens per request
    

    def is_conceptually_relevant(self, question):
        non_conceptual_patterns = [
            r"\bwho\b", r"\bwhen\b", r"\bwhere\b", r"\bpublication\b",
            r"\bauthor\b", r"\bpublished\b", r"\bbook\b", r"\bISBN\b",
            r"\bedition\b", r"\bhistory\b", r"\bhistorical\b"
        ]
        return not any(re.search(pattern, question.lower()) for pattern in non_conceptual_patterns)

    def extract_paragraphs_from_pdf(self, pdf_path):
        paragraphs = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    paragraphs.extend(text.split('\n'))
        return paragraphs

    def generate_qa_pairs_with_chatgpt(self, paragraphs):
        qa_pairs = []
        batched_paragraphs = []
        current_batch = ""

        for paragraph in paragraphs:
            if len(paragraph) > 20 and "http" not in paragraph:
                if len(current_batch) + len(paragraph) < self.max_tokens_per_request:
                    current_batch += f"{paragraph}\n\n"
                else:
                    batched_paragraphs.append(current_batch)
                    current_batch = f"{paragraph}\n\n"
        
        if current_batch:
            batched_paragraphs.append(current_batch)

        for batch in batched_paragraphs:
            prompt = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": f"Generate questions and answers focusing on the technical and conceptual content of this text, avoiding questions about authors, publication dates, or historical development: {batch}"}
            ]
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
                time.sleep(30)
                response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=prompt)
                response_text = response.choices[0].message['content'].strip()
                potential_qa_pairs = response_text.split('\n\n')
                for pair in potential_qa_pairs:
                    question = pair.split('\n')[0]
                    if self.is_conceptually_relevant(question):
                        qa_pairs.append(pair)
        
        return qa_pairs

    def format_flash_cards(self, qa_pairs):
        formatted_cards = []
        for pair in qa_pairs:
            if pair.count('\n') == 1:
                question, answer = pair.split('\n')
                formatted_cards.append({'front': question, 'back': answer})
        return formatted_cards

    def save_flash_cards_to_file(self, formatted_cards, filename):
        with open(filename, 'w') as file:
            json.dump(formatted_cards, file, indent=4)

    def process_pdf_to_flashcards(self, pdf_path, output_file):
        paragraphs = self.extract_paragraphs_from_pdf(pdf_path)
        qa_pairs = self.generate_qa_pairs_with_chatgpt(paragraphs)
        formatted_cards = self.format_flash_cards(qa_pairs)
        self.save_flash_cards_to_file(formatted_cards, output_file)
        print(f"Flash cards saved to {output_file}")
    
    async def get_flashcards(self, processed_material_id):
        material_doc = await self.db.collection('UsersFlashCards').document(kUserId).collection(self.processed_material.processed_material_id).document(self.flashcard_id
                                                                                                                                 ).get()
                                             
        if material_doc.exists:
            flashcards = material_doc.to_dict()
            return flashcards.fromJson(flashcards)
        else:
            return None

   
    async def delete_flashcards(self, processed_material_id):
        try:
            await self.db.collection('UsersFlashCards').document(kUserId).collection(self.processed_material.processed_material_id).document(self.flashcard_id
                                                                                                                                 ).delete()
        except Exception as e:
            print(e)
    async def addFlashCardsToFirestore(self):
        
        processed_data = self.processed_material  # Assuming Processed_Materials has a method named 'process'
        #.document(self.processed_material.user_id)
        try:
            await self.db.collection('UsersFlashCards').document(kUserId).collection(self.processed_material.processed_material_id).document(self.flashcard_id
                                                                                                                                 ).set({
                "flashcard_id": self.flashcard_id,
                "front_content": self.front_content,
                "back_content": self.back_content,
                "creation_date": self.creation_date,
            })
        except Exception as e:
            print(e)


openai_api_key = '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'
flashcards_controller = FlashcardsController(openai_api_key)
pdf_path = 'StudyWise/flashcards_from_pdf/test.pdf'
output_file = 'StudyWise/flashcards_from_pdf/JS/flash_cards.json'
flashcards_controller.process_pdf_to_flashcards(pdf_path, output_file)
