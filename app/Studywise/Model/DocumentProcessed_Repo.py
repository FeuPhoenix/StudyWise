from datetime import datetime
from firebase_admin import firestore,storage
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName 
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

from app.Studywise.Model import FirestoreDB
class DocumentProcessed:
    processed_material_id=""
    material_id=""
    generated_summary_file_path=""
    generated_text_file_path=""
    generated_images_folder_path=""
    def __init__(self, processed_material_id, material_id, 
                 generated_summary_file_path=None, 
                 generated_text_file_path=None,
                 generated_images_folder_path=None):
        self.processed_material_id = processed_material_id
        self.material_id = material_id
        self.generated_summary_file_path = generated_summary_file_path 
        self.generated_text_file_path = generated_text_file_path
        self.generated_images_folder_path = generated_images_folder_path
        self.db = FirestoreDB.get_instance()
    async def addProcessedMaterialToFirestore(self):
        try:
            await self.db.collection('MaterialsProcessed').document(kUserId).set({
                "processed_material_id": self.processed_material_id,
                "material_id": self.material_id,
                "generated_summary_file_path": self.generated_summary_file_path,
                "generated_text_file_path": self.generated_text_file_path,
                "generated_images_folder_path": self.generated_images_folder_path,
            })
        except Exception as e:
            print(e)

    @classmethod
    def fromJson(cls, data):
        return cls(
            processed_material_id=data["processed_material_id"],
            material_id=data["material_id"],
            generated_summary_file_path=data["generated_summary_file_path"],
            generated_text_file_path=data["generated_text_file_path"],
            generated_images_folder_path=data["generated_images_folder_path"],
        )

    def toJson(self):
        data = {
            "processed_material_id": self.processed_material_id,
            "material_id": self.material_id,
            "generated_summary_file_path": self.generated_summary_file_path,
            "generated_text_file_path": self.generated_text_file_path,
            "generated_images_folder_path": self.generated_images_folder_path,
        }
        return data
    async def upload_to_firebase(local_file, cloud_file):
    # Reference to the storage bucket
        bucket = storage.bucket()

    # Name of the file in the storage bucket
        blob = bucket.blob(cloud_file)

    # Upload the file
        blob.upload_from_filename(local_file)
        
        print(f'{local_file} has been uploaded to {cloud_file}.')
        metadata = blob.metadata
        print(metadata)
        return metadata
# #Testing
# def main():
#     file = "assets/input_files/text-based/test.pdf"  
#     is_Document(file)
# if __name__ == "__main__":
#     main()