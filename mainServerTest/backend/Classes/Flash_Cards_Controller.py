import pdfplumber
import openai
import time
import json
import re
from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
import FirestoreDB 

class FlashcardsController:
    @staticmethod
    def get_Flashcards_Video_from_firestore(userid,materialid):
                
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial").document(materialid).collection("FlashCards")
            
            # Get all documents in the collection
            documents = collection_ref.get()
            
            # Initialize an empty list to store all data
            all_data = []
            
            # Iterate over each document
            for doc in documents:
                # Get the data from the document
                data = doc.to_dict()
                # Append the data to the list
                all_data.append(data)
            
            return all_data
        except Exception as e:
            print("Error:", e)
            return None
    @staticmethod
    def get_Flashcards_Document_from_firestore(userid,materialid):
                
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial").document(materialid).collection("FlashCards")
            
            # Get all documents in the collection
            documents = collection_ref.get()
            
            # Initialize an empty list to store all data
            all_data = []
            
            # Iterate over each document
            for doc in documents:
                # Get the data from the document
                data = doc.to_dict()
                # Append the data to the list
                all_data.append(data)
            
            return all_data
        except Exception as e:
            print("Error:", e)
            return None
       
