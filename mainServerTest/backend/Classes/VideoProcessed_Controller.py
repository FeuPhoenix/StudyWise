from datetime import datetime
import json
import time
from firebase_admin import firestore
import openai
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
import uuid
import json
import requests

from backend.Classes.FirestoreDB import FirestoreDB
aai.settings.api_key = "8d8390aa4ac24f7aa92d724e44370d73"

class Video_Processed_Controller:
    @staticmethod
    def fetch_all_filenames_and_filetypes_in_Video_material(userid):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the "DocumentMaterial" collection
            doc_material_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial")

            # Get all documents in the "DocumentMaterial" collection
            doc_material_docs = doc_material_ref.stream()

            # Initialize an empty list to store all filenames and filetypes
            all_filenames_and_filetypes = []

            # Iterate over each document in "DocumentMaterial" collection
            for doc_material_doc in doc_material_docs:
                doc_material_data = doc_material_doc.to_dict()

                # Check if the document has the "file_name" and "file_type" fields and they are strings
                if 'file_name' in doc_material_data and 'file_type' in doc_material_data \
                        and isinstance(doc_material_data['file_name'], str) and isinstance(doc_material_data['file_type'], str):
                    filename = doc_material_data['file_name']
                    filetype = doc_material_data['file_type']
                    # Append the filename and filetype as a dictionary to the list
                    all_filenames_and_filetypes.append({"filename": filename, "filetype": filetype})

            # Dump the result to JSON
            result_json = json.dumps(all_filenames_and_filetypes, indent=4)

            return result_json
        except Exception as e:
            print("Error:", e)
            return None

    @staticmethod 
    def fetch_json_from_url(url):
            try:
                # Make a GET request to download the JSON file
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for any HTTP error status codes
                
                # Load the JSON data
                data = response.json()
                return data
            except requests.exceptions.RequestException as e:
                print("Error:  2", e)
                return None
    @staticmethod
    def fetch_video_content(userid, filename):
            db_instance = FirestoreDB.get_instance()
            firestore_instance = db_instance.get_firestore_instance()
            try:
                # Reference to the "VideoMaterial" collection
                video_material_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial")

                # Get all documents in the "VideoMaterial" collection
                video_material_docs = video_material_ref.stream()

                # Iterate over each document in "VideoMaterial" collection
                for doc_material_doc in video_material_docs:
                    doc_material_data = doc_material_doc.to_dict()

                    # Check if the document has the "file_name" field and it's a string
                    if 'file_name' in doc_material_data and isinstance(doc_material_data['file_name'], str):
                        # Check if the filename matches the desired filename
                        if doc_material_data['file_name'] == filename:
                            # Return the document ID
                          return  Video_Processed_Controller.retrieveVideoMaterialFromFirestore(userid,doc_material_doc.id)

                # If filename is not found, return None
                return None

            except Exception as e:
                print("Error:", e)
                return None
    @staticmethod
    def fetch_all_filenames_in_Video_material_with_id(userid):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the "VideoMaterial" collection
            video_material_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial")

            # Get all documents in the "VideoMaterial" collection
            video_material_docs = video_material_ref.stream()

            # Initialize an empty dictionary to store filenames with corresponding Document IDs
            filenames_with_ids = {}

            # Iterate over each document in "VideoMaterial" collection
            for doc_material_doc in video_material_docs:
                doc_material_data = doc_material_doc.to_dict()

                # Check if the document has the "file_name" field and it's a string
                if 'file_name' in doc_material_data and isinstance(doc_material_data['file_name'], str):
                    filename = doc_material_data['file_name']
                    document_id = doc_material_doc.id
                    # Store the filename with its corresponding Document ID in the dictionary
                    filenames_with_ids[document_id] = filename

            return filenames_with_ids
        except Exception as e:
            print("Error:", e)
            return None

    @staticmethod
    def retrieveVideoMaterialFromFirestore(user_id, material_id):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        try:
            doc_ref = firestore_instance.collection('Users').document(user_id).collection('VideoMaterial').document(material_id)
            doc = doc_ref.get()
            if doc.exists:
                video_material_data = doc.to_dict()

                # Fetch data from FlashCards collection if it exists
                flashcards_ref = doc_ref.collection('FlashCards')
                flashcards_data = []
                for flashcard_doc in flashcards_ref.stream():
                    flashcards_data.append(flashcard_doc.to_dict())

                # Fetch data from Questions collection if it exists
                questions_ref = doc_ref.collection('Questions')
                questions_data = []
                for question_doc in questions_ref.stream():
                    questions_data.append(question_doc.to_dict())

                # Add FlashCards and Questions data to the video_material_data
                video_material_data['FlashCards'] = flashcards_data
                video_material_data['Questions'] = questions_data
                flash_card_data = video_material_data['FlashCards']
                Questions_data = video_material_data['Questions']
                for question in questions_data:
                    medium_location = question['Questions_medium_location']
                    hard_location = question['Questions_hard_location']
                    easy_location = question['Questions_easy_location']
                

                Summary= Video_Processed_Controller.fetch_json_from_url(video_material_data['generated_summary_file_path'])

                Chapters= Video_Processed_Controller.fetch_json_from_url(video_material_data['generated_chapters_file_path'])

                flashcards= Video_Processed_Controller.fetch_json_from_url( flash_card_data[0]['flash_card_location'])

                MCQ_E= Video_Processed_Controller.fetch_json_from_url(easy_location)

                MCQ_M= Video_Processed_Controller.fetch_json_from_url(medium_location)

                MCQ_H= Video_Processed_Controller.fetch_json_from_url(hard_location)
            
                return video_material_data['Material'],video_material_data['generated_audio_file_path'],Summary,Chapters,flashcards,MCQ_E,MCQ_M,MCQ_H
            
            else:
                print(f"No such document with user_id: {user_id} and material_id: {material_id}")
                return None
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None