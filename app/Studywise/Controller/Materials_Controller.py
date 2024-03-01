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
    def __init__(self,Material:Material):
     self.db = FirestoreDB.get_instance()
     self.Material=Material
    
    async def add_material(self):
        try:
            upload_date = datetime.now().strftime("%d-%B-%Y")
            await self.db.collection('Materials').document(kUserId).collection('UserMaterials').document(self.Material.material_id).set({
                "material_id": self.Material,
                "user_ID": self.Material,
                "file_name": self.Material,
                "_file_path": self.Material,
                "upload_date": self.Material,
                "file_type": self.Material
            })
        except Exception as e:
            print(e)
    
    async def get_material(self):
        material_doc = await self.db.collection('Materials').document(kUserId).collection('UserMaterials').document(self.Material.material_id).get()
        if material_doc.exists:
            material_data = material_doc.to_dict()
            return Material.fromJson(material_data)
        else:
            return None

    # async def update_material(self, material_id, data):
    #     try:
    #         await self.db.collection('Materials').document(material_id).update(data)
    #     except Exception as e:
    #         print(e)

    async def delete_material(self):
        try:
            await self.db.collection('Materials').document(kUserId).collection('UserMaterials').document(self.Material.material_id).delete()
        except Exception as e:
            print(e)
     
    