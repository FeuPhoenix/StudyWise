import re
import subprocess
import uuid
from datetime import datetime
from pptx import Presentation
from docx import Document
import requests
from backend.Classes.DocumentProcessed_Repo import DocumentProcessed
from backend.Classes.FirestoreDB import FirestoreDB
import json
class DocumentProcessedController:
    @staticmethod
    def fetch_all_filenames_and_filetypes_in_Video_and_Document_material(userid):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            all_filenames_and_filetypes = []

            # Reference to the "DocumentMaterial" collection
            doc_material_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial")
            doc_material_docs = doc_material_ref.stream()

            # Iterate over each document in "DocumentMaterial" collection
            for doc_material_doc in doc_material_docs:
                doc_material_data = doc_material_doc.to_dict()

                # Check if the document has the "file_name" and "file_type" fields and they are strings
                if 'file_name' in doc_material_data and 'file_type' in doc_material_data \
                        and isinstance(doc_material_data['file_name'], str) and isinstance(doc_material_data['file_type'], str):
                    filename = doc_material_data['file_name']
                    filetype = doc_material_data['file_type']
                    all_filenames_and_filetypes.append({"filename": filename, "filetype": filetype})

            # Reference to the "VideoMaterial" collection
            video_material_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial")
            video_material_docs = video_material_ref.stream()

            # Iterate over each document in "VideoMaterial" collection
            for video_material_doc in video_material_docs:
                video_material_data = video_material_doc.to_dict()

                # Check if the document has the "file_name" and "file_type" fields and they are strings
                if 'file_name' in video_material_data and 'file_type' in video_material_data \
                        and isinstance(video_material_data['file_name'], str) and isinstance(video_material_data['file_type'], str):
                    filename = video_material_data['file_name']
                    filetype = video_material_data['file_type']
                    all_filenames_and_filetypes.append({"filename": filename, "filetype": filetype})

            # Dump the result to JSON
            result_json = json.dumps(all_filenames_and_filetypes, indent=4)
            return result_json
        except Exception as e:
            print("Error:", e)
            return None
        
    @staticmethod
    async def upload_document(file, userID) : 
        document = DocumentProcessed(file, userID)
        await document.Document_Processing()
        print('Doc ID and Name', document.file_name, document.material_id)
        return document.file_name, document.material_id

    @staticmethod
    def fetch_all_filenames_with_filetype_in_Document_material(userid):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the "DocumentMaterial" collection
            doc_material_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial")

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
    def retrieveDocumentMaterialFromFirestore(user_id, material_id):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        try:
            doc_ref = firestore_instance.collection('Users').document(user_id).collection('DocumentMaterial').document(material_id)
            doc = doc_ref.get()
            if doc.exists:
                Document_material_data = doc.to_dict()

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
                Document_material_data['FlashCards'] = flashcards_data
                Document_material_data['Questions'] = questions_data
                flash_card_data = Document_material_data['FlashCards']
                for question in questions_data:
                    medium_location = question['Questions_medium_location']
                    hard_location = question['Questions_hard_location']
                    easy_location = question['Questions_easy_location']
                
                # text=DocumentProcessedController.fetch_text_and_convert_to_json(Document_material_data['generated_text_file_path'])

                Summary= DocumentProcessedController.fetch_json_from_url(Document_material_data['generated_summary_file_path'])
                
                flashcards= DocumentProcessedController.fetch_json_from_url( flash_card_data[0]['flash_card_location'])
                
                MCQ_E= DocumentProcessedController.fetch_json_from_url(easy_location)
                
                MCQ_M= DocumentProcessedController.fetch_json_from_url(medium_location)
                
                MCQ_H= DocumentProcessedController.fetch_json_from_url(hard_location)
                
                return Document_material_data['_file_path'],Summary,flashcards,MCQ_E,MCQ_M,MCQ_H
            
            else:
                print(f"No such document with user_id: {user_id} and material_id: {material_id}")
                return None
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None
    @staticmethod
    def clean_text(text):
        allowed_pattern = r"[^a-zA-Z\s,.;:'\"!?()-]"
        cleaned_text = re.sub(allowed_pattern, '', text)    
        return cleaned_text
    
    @staticmethod
    def fetch_text_and_convert_to_json(url):
            try:
                # Make a GET request to download the text file
                response = requests.get(url)
                response.raise_for_status()  # Raise an exception for any HTTP error status codes

                # Read the text data
                text_data = response.text

                text_data = DocumentProcessedController.clean_text(text_data)
                
                # Create a JSON object with the attribute "Transcript"
                data = {"text": text_data}
                return data
            except requests.exceptions.RequestException as e:
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
        
    @staticmethod
    def fetch_document_content(userid, filename):
            db_instance = FirestoreDB.get_instance()
            firestore_instance = db_instance.get_firestore_instance()
            try:
                # Reference to the "DocumentMaterial" collection
                video_material_ref = firestore_instance.collection("Users").document(userid).collection("DocumentMaterial")

                # Get all documents in the "DocumentMaterial" collection
                video_material_docs = video_material_ref.stream()

                # Iterate over each document in "DocumentMaterial" collection
                for doc_material_doc in video_material_docs:
                    doc_material_data = doc_material_doc.to_dict()

                    # Check if the document has the "file_name" field and it's a string
                    if 'file_name' in doc_material_data and isinstance(doc_material_data['file_name'], str):
                        # Check if the filename matches the desired filename
                        if doc_material_data['file_name'] == filename:
                            # Return the document ID
                          return  DocumentProcessedController.retrieveDocumentMaterialFromFirestore(userid,doc_material_doc.id)

                # If filename is not found, return None
                return None

            except Exception as e:
                print("Error:", e)
                return None
            
# def main():
#     file,Summary,flashcards,MCQ_E,MCQ_M,MCQ_H = DocumentProcessedController.fetch_document_content("0GKTloo0geWML96tvd9g27C99543","test")
#     returns = [file,Summary,flashcards,MCQ_E,MCQ_M,MCQ_H]
#     for i in returns :
#        print(i, '============================================================\n\n\n\n\n\n')
# if __name__ == "__main__":
#     main()