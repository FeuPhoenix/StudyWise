from datetime import datetime
import json
import time
from firebase_admin import firestore

import openai
from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
import os
import re
import moviepy.editor as mp # Install moviepy: pip install moviepy
from datetime import timedelta
from pytube import YouTube
import assemblyai as aai
import time
import json
import openai
from pytube import YouTube
#from Model.Material_Repo import Material
import firebase_admin
from firebase_admin import credentials, storage
from flask import request,jsonify,render_template
import uuid
from VideoProcessed_Repo import VideoProcessed_Repo

from audiocutter import runaudiocutter
from flashcard_creator import runFlashcards
aai.settings.api_key = "8d8390aa4ac24f7aa92d724e44370d73"

class Video_Processed_Controller:
    
    def __init__(self,material,Video_cutted=True):
        self.material=material
        self.Video_Processing(material,Video_cutted)
        #self.db = FirestoreDB.get_instance()
        