from datetime import datetime, timedelta
import time

from FirestoreDB import FirestoreDB
import moviepy.editor as mp # Install moviepy: pip install moviepy


def addProcessedMaterialToFirestore(ID,file_name,file_path,audio_file_path):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        
       
        file_path_location,audio_file_path_Location=upload_material_to_storage(ID,file_name , file_path,audio_file_path)

        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id

        try:
            doc_ref=firestore_instance.collection('Users').document('13ffe4704e2d423ea7751cb88d599db7').collection('VideoMaterial').document("rmk3SGTciwNRdo9pT4ic").set({
                "file_name": file_name,
                "Material":file_path_location,
                "Audio":audio_file_path_Location


            })
            print("Successfully added Video to firestore")
        except Exception as e:
            print(e)
def upload_Video_file_to_storage(blob, file_path):
        """Uploads a large file to Google Cloud Storage using resumable upload."""
        print(f"Uploading {file_path}...")
        timeout_seconds = 600  # Example: 10 minutes
        with open(file_path, 'rb') as f:
            blob.upload_from_file(f, rewind=True, content_type='video/mp4',timeout=timeout_seconds)
def upload_audio_file_to_storage(blob, file_path):
        """Uploads a large file to Google Cloud Storage using resumable upload."""
        

        with open(file_path, 'rb') as f:
            blob.upload_from_file(f, rewind=True, content_type='audio/wav',timeout=600)

def upload_material_to_storage(user_id, material_name, material_file_path,audio_file_path):
        db_instance = FirestoreDB.get_instance()
        storage_instance = db_instance.get_storage_instance()

        # Constructing the full path for the folder using the material name
        folder_path = f"user/{user_id}/Uploaded Materials/{material_name}/"

        # Creating a folder with the material name as the folder name
        folder_blob = storage_instance.blob(folder_path)
        folder_blob.upload_from_string('')  # Upload an empty string to create the folder
        print("file path material_file_path",material_file_path)



        # Upload the material file inside the folder
        material_blob_path = folder_path + f"{material_name}.mp4"
        material_blob = storage_instance.blob(material_blob_path)
        upload_Video_file_to_storage(material_blob, material_file_path)
        time.sleep(10)
        audio_blob_path = folder_path + "audio.mp3"
        audio_blob = storage_instance.blob(audio_blob_path)
        upload_audio_file_to_storage(audio_blob, audio_file_path)
        expiration = datetime.now() + timedelta(days=36500)
        print("Successfully uploaded material to Storage")
    # Returning the signed URLs for the uploaded files
        return (
            material_blob.generate_signed_url(expiration=expiration),
            audio_blob.generate_signed_url(expiration=expiration)

        )
def upload_audio_file_to_storage(blob, file_path):
        """Uploads a large file to Google Cloud Storage using resumable upload."""
        

        with open(file_path, 'rb') as f:
            blob.upload_from_file(f, rewind=True, content_type='audio/wav',timeout=600)
if __name__ == '__main__':
      
      addProcessedMaterialToFirestore("13ffe4704e2d423ea7751cb88d599db7", "Physics_-_Basic_Introduction", "D:/COLLEGE/StudyWise/assets/input_files/videos/Physics_-_Basic_Introduction.mp4","D:/COLLEGE/StudyWise/assets/output_files/audio/Physics_-_Basic_Introduction.wav")