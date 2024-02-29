import pdfplumber
import openai
import time
import json
import re
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 

class FlashcardsController:
    def __init__(self,material_id):
        openai.api_key = OPENAI_API_KEY
        MAX_TOKENS_PER_REQUEST = 4096
        self.material_id=material_id  # Safe limit for tokens per request


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
        with open(txt_path, 'r') as file:
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

    def generate_qa_pairs_with_chatgpt(self,paragraphs, content_type):
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
                time.sleep(30)
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
                formatted_cards.append({'front': question, 'back': answer})
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

    def save_flash_cards_to_file(self,formatted_cards, filepath):
        with open(filepath, 'w') as file:
            json.dump(formatted_cards, file, indent=4)

    def runFlashcards(self,file_path, content_type = ''):
        content = []

        filename = self.filenameFromPath(file_path)
        output_path='assets/output_files/flashcards/'+filename+'_flashcards.json' 

        if content_type == '':
            if file_path.endswith('.pdf'):
                content =self. extract_paragraphs_from_pdf(file_path)
                content_type = 'pdf'
            elif file_path.endswith('.txt'):
                content = self.extract_and_split_text(file_path) 
            else:
                raise ValueError("Unsupported file type. Only .pdf or .txt files are currently accepted.")
        
        
    
    async def get_flashcards(self, processed_material_id):
        material_doc = await self.db.collection('UsersFlashCards').document(kUserId).collection(self.material_id).document(self.flashcard_id
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


# openai_api_key = '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'
# flashcards_controller = FlashcardsController(openai_api_key)
# pdf_path = 'StudyWise/flashcards_from_pdf/test.pdf'
# output_file = 'StudyWise/flashcards_from_pdf/JS/flash_cards.json'
# flashcards_controller.process_pdf_to_flashcards(pdf_path, output_file)
#------------------
# qa_pairs = generate_qa_pairs_with_chatgpt(content, content_type)
#         formatted_cards = format_flash_cards(qa_pairs)
#         save_flash_cards_to_file(formatted_cards, output_path)
#         print(f"Flash cards saved to {output_path}")
