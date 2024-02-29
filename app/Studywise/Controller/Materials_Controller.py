from datetime import datetime
from firebase_admin import firestore
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 
import os
import re
import moviepy.editor as mp # Install moviepy: pip install moviepy
from datetime import timedelta
from pytube import YouTube
import requests
import assemblyai as aai

import time
import json
import openai

from pytube import YouTube
from app.Studywise.Model import FirestoreDB
from app.Studywise.Model.Material_Repo import Material

class MaterialController:
    def __init__(self):
     self.db = FirestoreDB.get_instance()
    
    