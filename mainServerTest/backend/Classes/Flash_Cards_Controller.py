from datetime import datetime, timedelta
import os
import pdfplumber
import openai
import time
import json
import re
from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
import FirestoreDB as FirestoreDB
from Flash_Cards_Repo import Flash_Cards

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
    @staticmethod
    def upload_material_to_storage(user_id, material_name, flashcard_file_path):
        db_instance = FirestoreDB.get_instance()
        storage_instance = db_instance.get_storage_instance()

        # Constructing the full path for the folder using the material name
        folder_path = f"user/{user_id}/Uploaded Materials/{material_name}/"

        # Creating a folder with the material name as the folder name
        folder_blob = storage_instance.blob(folder_path)
        folder_blob.upload_from_string('')  # Upload an empty string to create the folder

        # Upload the material file inside the folder
        flashcard_blob_path = folder_path + "flashcards"
        flashcard_blob = storage_instance.blob(flashcard_blob_path)
        flashcard_blob.upload_from_filename(flashcard_file_path,timeout=600)
    
        expiration = datetime.now() + timedelta(days=36500)


        print("Successfully uploaded material to Storage")
        return flashcard_blob.generate_signed_url(expiration=expiration)
    @staticmethod
    def save_json_to_file(json_data,filename ):
        file_path=f"D:/COLLEGE/StudyWise/mainServerTest/assets/output_files/flashcards/{filename}.json"
        try:
            # Ensure the directory exists
            dir_path = os.path.dirname(file_path)
            os.makedirs(dir_path, exist_ok=True)
            
            # Check if a directory with the same name as the file already exists
            if os.path.isdir(file_path):
                raise IsADirectoryError(f"A directory with the same name as the file '{file_path}' already exists.")

            # Write the JSON data to the file
            with open(file_path, 'w') as json_file:
                json.dump(json_data, json_file, indent=4)
            
            print(f"Successfully saved JSON data to {file_path}")

        except PermissionError as e:
            print(f"PermissionError: {e}. Please check your permissions for the directory.")
        except IsADirectoryError as e:
            print(f"IsADirectoryError: {e}. Please ensure the file path does not conflict with an existing directory.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return file_path
    @staticmethod
    def update_flashcards_in_firestore(userid,material_name,Type,materialid, new_data):
        filepath=FlashcardsController.save_json_to_file(new_data,material_name)
        print("filepath",filepath,"======================")
        file_location=FlashcardsController.upload_material_to_storage(userid,material_name, filepath)
        time.sleep(1)
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        
        try:
            # Reference to the collection
            collection_ref = firestore_instance.collection("Users").document(userid).collection(Type).document(materialid).collection("FlashCards")
            
            # Get all documents in the collection
            documents = collection_ref.get()
            
            # Initialize an empty list to store all data
            all_data = []
            
            # Iterate over each document
            for doc in documents:
                # Get the document reference
                doc_ref = collection_ref.document(doc.id)
                
                # Update the document with new data
                doc_ref.update(file_location)
                
                # Get the updated data from the document
                updated_doc = doc_ref.get()
                updated_data = updated_doc.to_dict()
                
                # Append the updated data to the list
                all_data.append(updated_data)
            
            print("Successfully updated flashcards in Firestore")
        except Exception as e:
            print("Error:", e)
            print("Failed to update flashcards in Firestore")
    @staticmethod
    def Generate_And_Replace_FlasCards(ProcessedMaterial,userid,materialid,content_type=''):
        F= Flash_Cards(ProcessedMaterial,userid,materialid,content_type)
        time.sleep(1)

def main():
    FlashcardsController.Generate_And_Replace_FlasCards("D:/COLLEGE/StudyWise/mainServerTest/assets/input_files/text-based/mohamed_test.pdf","0GKTloo0geWML96tvd9g27C99543","cc20ce5446be455db89d88698929423a","pdf")
if __name__ == "__main__":
    main()
             
