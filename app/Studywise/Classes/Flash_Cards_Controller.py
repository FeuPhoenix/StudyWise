import pdfplumber
import openai
import time
import json
import re
from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
import FirestoreDB 

class FlashcardsController:
    def __init__(self,ProcessedMaterial):
        openai.api_key = OPENAI_API_KEY
        self.ProcessedMaterial=ProcessedMaterial  
        #self.db = FirestoreDB.get_instance()
        self.runFlashcards(self.ProcessedMaterial, content_type = '')
       
