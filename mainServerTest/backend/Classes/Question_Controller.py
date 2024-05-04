import os
import sys
import time
import pdfplumber
import openai
import re
import random
import json
import textstat

from FirestoreDB import FirestoreDB

user_points = 0  # Initialize user points
class QuestionController:
    @staticmethod
    def get_Questions_Video_from_firestore(userid,materialid):
                
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial").document(materialid).collection("Questions")
            
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
    def get_Questions_Document_from_firestore(userid,materialid):
                
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial").document(materialid).collection("Questions")
            
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
    def get_easy_Questions_from_firestore(userid,materialid):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial").document(materialid).collection("Questions")
            
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
            
            return all_data['Questions_easy_location']
        except Exception as e:
            print("Error:", e)
            return None
    @staticmethod
    def get_medium_Questions_from_firestore(userid,materialid):
       
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial").document(materialid).collection("Questions")
            
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
            
            return all_data['Questions_medium_location']
        except Exception as e:
            print("Error:", e)
            return None
    @staticmethod
    def get_hard_Questions_from_firestore(userid,materialid):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial").document(materialid).collection("Questions")
            
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
            
            return all_data['Questions_hard_location']
        except Exception as e:
            print("Error:", e)
            return None
