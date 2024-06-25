from datetime import datetime, timedelta
import uuid
from FirestoreDB import FirestoreDB
import os
import easyocr



class OCR_Repo:
    
        def __init__(self,image_File):
            self.image_File=image_File
            self.image_id=uuid.uuid4().hex
        @staticmethod
        def get_filename(file_path):
            return os.path.basename(file_path)
        def run_ocr(self):
            reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
            result = reader.readtext(self.image_File,detail = 0)
            result_string =', '.join(result)
            return result_string
            
        @staticmethod
        def upload_material_to_storage(user_id, material_name, image_file_path):
            db_instance = FirestoreDB.get_instance()
            storage_instance = db_instance.get_storage_instance()
            filename = OCR_Repo.get_filename(image_file_path)
            # Constructing the full path for the folder using the material name
            folder_path = f"user/{user_id}/Uploaded Materials/{material_name}/images/"

            # Creating a folder with the material name as the folder name
            folder_blob = storage_instance.blob(folder_path)
            folder_blob.upload_from_string('')  # Upload an empty string to create the folder

            # Upload the material file inside the folder
            flashcard_blob_path = folder_path + filename
            flashcard_blob = storage_instance.blob(flashcard_blob_path)
            flashcard_blob.upload_from_filename(image_file_path,timeout=600)
        
            expiration = datetime.now() + timedelta(days=36500)


            print("Successfully uploaded material to Storage")
            return flashcard_blob.generate_signed_url(expiration=expiration),filename
        
        def add_image_to_firestore(self, user_id, material_name, Material_Type, materialid):
        
            db_instance = FirestoreDB.get_instance()
            firestore_instance = db_instance.get_firestore_instance()
            image_file_link, image_name = OCR_Repo.upload_material_to_storage(user_id, material_name, self.image_File)

            # Search for an image with the same name before adding
            images_ref = firestore_instance.collection('Users').document(user_id).collection(Material_Type).document(materialid).collection('Images')
            docs = images_ref.where("image_name", "==", image_name).stream()
            
            if any(doc.exists for doc in docs):
                print("Image already exists")
                return None
            
            try:
                doc_ref = images_ref.document(self.image_id).set({
                    "image": image_file_link,
                    "image_name": image_name,
                })
                print("Successfully added processed material to firestore")
            except Exception as e:
                print(e)
        def fetch_all_images(self, user_id, Material_Type, materialid):
             
            db_instance = FirestoreDB.get_instance()
            firestore_instance = db_instance.get_firestore_instance()
            try:
                # Get reference to the Images collection
                images_ref = firestore_instance.collection('Users').document(user_id).collection(Material_Type).document(materialid).collection('Images')
                
                # Fetch all documents in the Images collection
                docs = images_ref.stream()

                # Iterate through the documents and print out the data
                images = []
                for doc in docs:
                    image_data = doc.to_dict()
                    images.append(image_data)
                    # print(f"Image ID: {doc.id}, Image Data: {image_data}")
                
                return images

            except Exception as e:
                print(f"Error fetching images: {e}")
                return []
        def get_image_from_firestore(self, user_id, Material_Type, materialid, image_name):
            try:
                db_instance = FirestoreDB.get_instance()
                firestore_instance = db_instance.get_firestore_instance()
                images_ref = firestore_instance.collection('Users').document(user_id).collection(Material_Type).document(materialid).collection('Images')
                docs = images_ref.where("image_name", "==", image_name).stream()
                for doc in docs:
                    if doc.exists:
                        return doc.to_dict()
                return None
            except Exception as e:
                print(f"Error searching for image: {e}")
                return None
def main():
  
    x= OCR_Repo("../../assets/output_files/Images/test/test_page_1_img_1.png")
    x.add_image_to_firestore("0GKTloo0geWML96tvd9g27C99543","mohamed_test","DocumentMaterial","cc20ce5446be455db89d88698929423a")
    x.run_ocr()
if __name__ == "__main__":
    main()
               
