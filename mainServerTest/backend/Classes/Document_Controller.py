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
from FirestoreDB import FirestoreDB


class DocumentProcessedController:
    @staticmethod
    def fetch_all_filenames_in_document_material(userid):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the "DocumentMaterial" collection
            doc_material_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial")

            # Get all documents in the "DocumentMaterial" collection
            doc_material_docs = doc_material_ref.stream()

            # Initialize an empty list to store all filenames
            all_filenames = []

            # Iterate over each document in "DocumentMaterial" collection
            for doc_material_doc in doc_material_docs:
                doc_material_data = doc_material_doc.to_dict()

                # Check if the document has the "file_name" field and it's a string
                if 'file_name' in doc_material_data and isinstance(doc_material_data['file_name'], str):
                    filename = doc_material_data['file_name']
                    # Append the filename to the list
                    all_filenames.append(filename)

            return all_filenames
        except Exception as e:
            print("Error:", e)
            return None
    @staticmethod
    def fetch_all_data_in_document(userid, document_id):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the document in the "DocumentMaterial" collection
            doc_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial").document(document_id)

            # Get the document data
            doc_data = doc_ref.get().to_dict()

            return doc_data
        except Exception as e:
            print("Error:", e)
            return None
    @staticmethod
    def fetch_data_by_file_name(userid, attribute_value):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            doc_material_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial")

            # Query documents where the attribute "name" has the value "test"
            query = doc_material_ref.where("file_name", "==", attribute_value).stream()

            # Initialize an empty list to store the matching documents
            matching_documents = []

            # Iterate over each document in the query result
            for doc in query:
                # Convert the document to a dictionary and append it to the list
                matching_documents.append(doc.to_dict())

            return matching_documents
        except Exception as e:
            print("Error:", e)
            return None
def main():
    print(DocumentProcessedController.fetch_data_by_attribute_value("13ffe4704e2d423ea7751cb88d599db7","test"))
if __name__ == "__main__":
    main()
       
    