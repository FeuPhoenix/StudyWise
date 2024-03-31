import subprocess
import uuid
from datetime import datetime
from firebase_admin import firestore, credentials, initialize_app
import json
import time
import openai
import re
import pdfplumber
import os
from pptx import Presentation
from io import BytesIO
from PIL import Image
from docx import Document
from PIL import Image
from io import BytesIO
from summarizer import Summarizer
from firebase_admin import credentials, storage
from Flash_Cards_Controller import FlashcardsController
from DocumentProcessed_Repo import DocumentProcessed
from Question_Controller import QuestionController
import fitz  # PyMuPDF
import os
import comtypes.client



class DocumentProcessedController:
    def __init__(self,file) :
        self.file=file
        self.Document_Processing(file)
       
    