
import openai
from Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
import os
import re
import moviepy.editor as mp # Install moviepy: pip install moviepy
from datetime import datetime, timedelta
from pytube import YouTube
import assemblyai as aai
import time
import json
import openai
from pytube import YouTube
#from Model.Material_Repo import Material
import firebase_admin
from firebase_admin import credentials, storage
from flask import request,jsonify,render_template
import uuid
from Flash_Cards_Repo import Flash_Cards
from Questions_Repo import Questions_Repo

from FirestoreDB import FirestoreDB
from audiocutter import runaudiocutter
aai.settings.api_key = "8d8390aa4ac24f7aa92d724e44370d73"
class VideoProcessed_Repo:
    def __init__(self,material,userid,Video_cut=True):
        self.material_id=uuid.uuid4().hex#done

        self.material=material
        self.user_ID=userid
        self.Video_Processing(material,Video_cut)
        
        #self.db = FirestoreDB.get_instance()
    @staticmethod
    def check_value_exists_in_VideoMaterial(userid, attribute_value):
        db_instance = FirestoreDB.get_instance()  # Assuming FirestoreDB is a class or method to access Firestore
        firestore_instance = db_instance.get_firestore_instance()
        try:
            # Reference to the collection
            doc_material_ref = firestore_instance.collection("Users").document(userid).collection("VideoMaterial")

            # Query documents where the attribute name matches the value
            query = doc_material_ref.where("file_name", "==", attribute_value).stream()

            # Iterate over the query results
            for doc in query:
                # If any document matches the query, return False
                print("The Video already exists")
                return False

            # If no matching document is found, return True
            return True
        except Exception as e:
            print("Error:", e)
            return None
    def addProcessedMaterialToFirestore(self):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()
        
       
        file_path_location,generated_text_file_path_Location\
            ,generated_summary_file_path_Location\
            ,generated_chapters_file_path_Location,generated_audio_file_path_Location=VideoProcessed_Repo.upload_material_to_storage(self.user_ID,self.file_name , self.file_path,self.generated_text_file_path,self.generated_summary_file_path,self.generated_chapters_file_path,self.generated_audio_file_path)

        #document('13ffe4704e2d423ea7751cb88d599db7') the number will be replaced with the user id
        #document(rmk3SGTciwNRdo9pT4CO) this will be replaced with the material id

        try:
            doc_ref=firestore_instance.collection('Users').document(self.user_ID).collection('VideoMaterial').document(self.material_id).set({
                "file_name": self.file_name,
                "_file_path": file_path_location,
                "file_type": self.file_type,
                "material_id": self.material_id,
                "Material":file_path_location,
                "generated_summary_file_path": generated_summary_file_path_Location,
                "generated_text_file_path":generated_text_file_path_Location ,
                "generated_chapters_file_path":generated_chapters_file_path_Location,
                "generated_audio_file_path":generated_audio_file_path_Location

            })
            print("Successfully added Video to firestore")
        except Exception as e:
            print(e)
    @staticmethod
    def retrieveVideoMaterialFromFirestore(user_id, material_id):
        db_instance = FirestoreDB.get_instance()
        firestore_instance = db_instance.get_firestore_instance()

        try:
            doc_ref = firestore_instance.collection('Users').document(user_id).collection('VideoMaterial').document(material_id)
            doc = doc_ref.get()
            if doc.exists:
                return doc.to_dict()
            else:
                print(f"No such document with user_id: {user_id} and material_id: {material_id}")
                return None
        except Exception as e:
            print(f"Error retrieving document: {e}")
            return None
    @staticmethod        
    def upload_Video_file_to_storage(blob, file_path):
        """Uploads a large file to Google Cloud Storage using resumable upload."""
        print(f"Uploading {file_path}...")
        with open(file_path, 'rb') as f:
            blob.upload_from_file(f, rewind=True, content_type='video/mp4',timeout=600)
    def upload_audio_file_to_storage(blob, file_path):
        """Uploads a large file to Google Cloud Storage using resumable upload."""
        

        with open(file_path, 'rb') as f:
            blob.upload_from_file(f, rewind=True, content_type='audio/wav',timeout=600)

    def upload_material_to_storage(user_id, material_name, material_file_path, text_file_path, summary_file_path, chapters_file_path, audio_file_path):
        db_instance = FirestoreDB.get_instance()
        storage_instance = db_instance.get_storage_instance()

        # Constructing the full path for the folder using the material name
        folder_path = f"user/{user_id}/Uploaded Materials/{material_name}/"

        # Creating a folder with the material name as the folder name
        folder_blob = storage_instance.blob(folder_path)
        folder_blob.upload_from_string('')  # Upload an empty string to create the folder
        print("file path material_file_path",material_file_path)
        print("file path text_file_path ",text_file_path)
        print("file path summary_file_path ",summary_file_path)
        print("file path chapters_file_path ",chapters_file_path)
        print("file path audio_file_path ",audio_file_path)


        # Upload the material file inside the folder
        material_blob_path = folder_path + f"{material_name}.mp4"
        material_blob = storage_instance.blob(material_blob_path)
        VideoProcessed_Repo.upload_Video_file_to_storage(material_blob, material_file_path)

        # Upload the text file inside the folder
        text_blob_path = folder_path + "text.txt"
        text_blob = storage_instance.blob(text_blob_path)
        text_blob.upload_from_filename(text_file_path,timeout=600)

        # Upload the summary file inside the folder
        summary_blob_path = folder_path + "summary.json"
        summary_blob = storage_instance.blob(summary_blob_path)
        summary_blob.upload_from_filename(summary_file_path,timeout=600)

        # If chapters_file_path is provided, upload the chapters file inside the folder
        
        chapters_blob_path = folder_path + "chapters.json"
        chapters_blob = storage_instance.blob(chapters_blob_path)
        chapters_blob.upload_from_filename(chapters_file_path,timeout=600)

        # If audio_file_path is provided, upload the audio file inside the folder
        time.sleep(10)
        audio_blob_path = folder_path + "audio.mp3"
        audio_blob = storage_instance.blob(audio_blob_path)
        VideoProcessed_Repo.upload_audio_file_to_storage(audio_blob, audio_file_path)
        
        expiration = datetime.now() + timedelta(days=36500)
        print("Successfully uploaded material to Storage")
    # Returning the signed URLs for the uploaded files
        return (
            material_blob.generate_signed_url(expiration=expiration),
            text_blob.generate_signed_url(expiration=expiration),
            summary_blob.generate_signed_url(expiration=expiration),
            chapters_blob.generate_signed_url(expiration=expiration) ,
            audio_blob.generate_signed_url(expiration=expiration) 
        )

        
     
    

    
   
    
  
    @staticmethod       
    def split_text(text, max_chunk_size=3800):  # Reduced max_chunk_size for safety
        """
        Dynamically splits the text into chunks that are less than max_chunk_size,
        trying to avoid cutting off in the middle of a sentence.
        """
        sentences = re.split(r'(?<=[.!?]) +', text)
        current_chunk = ""
        for sentence in sentences:
            # Check if adding the next sentence would exceed the max chunk size
            if len(current_chunk) + len(sentence) > max_chunk_size:
                yield current_chunk
                current_chunk = sentence  # Start a new chunk
            else:
                current_chunk += " " + sentence
        yield current_chunk  # Yield the last chunk
    
    @staticmethod
    def is_mp4_file(file_path):
        extension = os.path.splitext(file_path)[1]
        if extension == ".mp4":
            print("True")
            return True
        else:
            print("Flase")
            return False
    @staticmethod
    def getFileNameFromPathWithOutExtension(input_string):
    # Find the last occurrence of '/'
        last_slash_index = input_string.rfind('/')
        
        # Slice the string from the character after the last '/'
        # If '/' is not found, rfind returns -1, and slicing starts from index 0
        result_string = input_string[last_slash_index + 1:]
        result_string=result_string.replace('.mp4','')
        return result_string
    @staticmethod
    def milliseconds_to_hms(ms):
        ms=int(ms)
        seconds = int(ms / 1000)
        return str(timedelta(seconds=seconds))
    @staticmethod
    def generate_concise_title(headline, OPENAI_API_KEY):
        while True:
            try:
                        openai.api_key = OPENAI_API_KEY
                        response = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo",
                            messages=[
                                {"role": "system", "content": "You are a helpful assistant."},
                                {"role": "user", "content": f"Convert this headline into a concise title: \"{headline}\""}
                            ]
                        )

                        return response['choices'][0]['message']['content'].strip()

            except openai.error.RateLimitError as e:
                print("Rate limit exceeded, waiting to retry...")
                time.sleep(20)
    @staticmethod
    def Readjsonfile(filename):
        with open(filename, 'r') as file:
            chapters = json.load(file)
        return chapters


    @staticmethod
    def download_video_from_youtube(video_url, output_path):
   

        # Create a YouTube object with the URL
        yt = YouTube(video_url)
        
        # Get the highest quality video stream
        video_stream = yt.streams.get_highest_resolution()
        
        # Define the filename for the video file
        filename = yt.title + '.mp4'
        filename=filename.replace(" ","_")
        # Download the video stream
        video_stream.download(output_path=output_path, filename=filename)
        
        # Construct the full path to the downloaded video file
        video_file_path = os.path.join(output_path, filename)
        video_file_path=video_file_path.replace("\\", "/")
        video_file_path=video_file_path.replace(" ", "_")
        
        yt.title=yt.title.replace(" ","_")
        print(video_file_path)

        # Return a tuple containing the path of the downloaded video file and the name of the video
        return video_file_path, yt.title

    @staticmethod
    def read_text_file(file_path):
        with open(file_path, 'r') as file:
            return file.read()
    

    @staticmethod
    def get_file_extension(file_name):
        # Split the file name by the dot (.)
        parts = file_name.split(".")

        # Check if there is an extension available
        if len(parts) > 1:
            # Return the last part as the extension
            return parts[-1]
        else:
            # No extension found
            return ""

    def Video_Processing(self,file_path_or_url,Video_cut):
        self.file_name = VideoProcessed_Repo.getFileNameFromPathWithOutExtension(self.file_path)
        if VideoProcessed_Repo.check_value_exists_in_VideoMaterial(self.user_ID,self.file_name):
        # Check if the input is a local file with the extension .mp4
            try:
                if  self.is_mp4_file(file_path_or_url):
                    self.file_path=file_path_or_url


                    # self.file_path = file_path_or_url.replace(" ", "_")
                    # print(self.file_path)
                    # os.rename(file_path_or_url, self.file_path)
                    
                    if Video_cut:
                        
                        # self.file_path = file_path_or_url.replace(" ", "_")
                        # print(self.file_path)
                        # os.rename(file_path_or_url, self.file_path)
                        self.generated_video_file_path = runaudiocutter(self.file_path)
                        print("Audiocutter output file: "+file_path_or_url)
                        video = mp.VideoFileClip(file_path_or_url)

                    else:
                        video = mp.VideoFileClip(self.file_path)
                        self.generated_video_file_path=video
                    self.file_name = VideoProcessed_Repo.getFileNameFromPathWithOutExtension(self.file_path)
                    self.file_type=VideoProcessed_Repo.get_file_extension(self.file_name)
                    print("Video_name: "+self.file_name)
                    
                    print('video is initialized')
                    audio = video.audio
                    print('video.audio is extracted')
                    audio.write_audiofile(f"mainServerTest/assets/output_files/audio/{self.file_name}.wav")
                    self.generated_audio_file_path = f"mainServerTest/assets/output_files/audio/{self.file_name}.wav"
                    print(f"Audio file downloaded at: {self.generated_audio_file_path}") 
                    config = aai.TranscriptionConfig(auto_chapters=True)

                    # Transcribe the audio and get the result as a JSON object
                    transcript = aai.Transcriber().transcribe(self.generated_audio_file_path, config)
                    if transcript.status == aai.TranscriptStatus.error:
                        print(transcript.error)
                    else:
                        print(transcript.text)
                    
                    self.generated_text_file_path = f"mainServerTest/assets/output_files/text_files/{self.file_name}.txt"
                    with open(self.generated_text_file_path, 'w', encoding='utf-8',errors='ignore') as transcript_file:
                            transcript_file.write(transcript.text)
                            print(f"Full transcript has been successfully saved to {self.generated_text_file_path}.")
                    
                    chapters_data = []

                    # Iterate over chapters and add their data to the list
                    for chapter in transcript.chapters:
                        chapters_data.append({
                            "start": chapter.start,
                            "end": chapter.end,
                            "headline": chapter.headline
                        }) 
                            
                    json_chapters = f'mainServerTest/assets/output_files/Chapters/{self.file_name}.json'

            # Write the chapters data to a JSON file
                    with open(json_chapters, 'w') as json_file:
                        json.dump(chapters_data, json_file, indent=4)
                    
                    print(f"Chapters have been successfully saved to {json_chapters}.")
                    
                    self.generated_summary_file_path = f'mainServerTest/assets/output_files/summaries/{self.file_name}.json'
                    text = VideoProcessed_Repo.read_text_file(self.generated_text_file_path)
                    prompt = "Provide a long summary of the transcript."

                    result = transcript.lemur.task(prompt)   
                    summary_data = {
                            'long_summary': result.response
                        }
                        # Write the summary data to a JSON file
                    with open(self.generated_summary_file_path, 'w') as json_file:
                            json.dump(summary_data, json_file, indent=4)
                            print(f"Long summary has been successfully saved to {self.generated_summary_file_path}.") 
                    text=VideoProcessed_Repo.Readjsonfile(json_chapters)
                    processed_chapters = []
                    for chapter in text:
                        start_hms = VideoProcessed_Repo.milliseconds_to_hms(chapter['start'])
                        end_hms = VideoProcessed_Repo.milliseconds_to_hms(chapter['end'])
                        concise_title = VideoProcessed_Repo.generate_concise_title(chapter['headline'], OPENAI_API_KEY)
                        print("the processed chapter success")
                        processed_chapters.append({
                            'start': start_hms,
                            'end': end_hms,
                            'concise_title': concise_title
                        })
                    self.generated_chapters_file_path=f'mainServerTest/assets/output_files/Processed_Chapters/{self.file_name}.json'
                    with open(f'mainServerTest/assets/output_files/Processed_Chapters/{self.file_name}.json', 'w') as outfile:
                        json.dump(processed_chapters, outfile, indent=4)
                    self.addProcessedMaterialToFirestore()

                    f=Flash_Cards(self.generated_text_file_path,self.user_ID,self.material_id,"TRANSCRIPT")
                    m=Questions_Repo(self.generated_text_file_path,self.user_ID,self.material_id,"TRANSCRIPT")
                    return self.file_name,self.material_id

            except Exception as e:
                print(e)
                # os.remove(self.generated_audio_file_path)
                # os.remove(self.generated_text_file_path)
                # os.remove(json_chapters)
                # os.remove(self.generated_chapters_file_path)
                
                # os.remove(self.generated_summary_file_path)
                # if self.generated_video_file_path is not None:
                #  os.remove(self.generated_video_file_path)
                # os.remove(self.file_path)

            # Check if the input is a YouTube video link
            # youtube_regex = (
            #     r'(https?://)?(www\.)?'
            #     r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
            #     r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
            # match = re.match(youtube_regex, file_path_or_url)
            else:
                try:
                    print("skipped if")
                    video_url = file_path_or_url  
                    output_path = 'mainServerTest/assets/input_files/videos'  
                    self.file_path,self.file_name = VideoProcessed_Repo.download_video_from_youtube(video_url, output_path)
                    print("the video has been downloaded successfully")
                    #videocutted=runaudiocutter(video_file_path)
                    print(self.file_path)
                    if Video_cut:
                        self.file_path = runaudiocutter(self.file_path)
                        print("Audiocutter output file: "+self.file_path)
                        video = mp.VideoFileClip(self.file_path)

                    else:
                        video = mp.VideoFileClip(self.file_path)

                    audio = video.audio
                    audio.write_audiofile(f"mainServerTest/assets/output_files/audio/extracted_audio_from_{self.file_name}.wav")
                    self.generated_audio_file_path = f"mainServerTest/assets/output_files/extracted_audio_from_{self.file_name}.wav"
                    print(f"Audio file downloaded at: {self.generated_audio_file_path}") 
                    config = aai.TranscriptionConfig(auto_chapters=True,)

                    # Transcribe the audio and get the result as a JSON object
                    transcript = aai.Transcriber().transcribe(self.generated_audio_file_path, config)
                    self.generated_text_file_path = f"mainServerTest/assets/output_files/extracted_transcripts/{self.file_name}.txt"
                    with open( self.generated_text_file_path, 'w', encoding='utf-8') as transcript_file:
                            transcript_file.write(transcript.text)
                            print(f"Full transcript has been successfully saved to { self.generated_text_file_path}.")
                    #runFlashcards(transcript_filename, 'TRANSCRIPT')
                    chapters_data = []

                    # Iterate over chapters and add their data to the list
                    for chapter in transcript.chapters:
                        chapters_data.append({
                            "start": chapter.start,
                            "end": chapter.end,
                            "headline": chapter.headline
                        }) 
                            
                    json_chapters = f'mainServerTest/assets/output_files/Chapters/chapters_results_{self.file_name}.json'

            # Write the chapters data to a JSON file
                    with open(json_chapters, 'w') as json_file:
                        json.dump(chapters_data, json_file, indent=4)
                    
                    print(f"Chapters have been successfully saved to {json_chapters}.")
                    
                
                    self.generated_summary_file_path = f'mainServerTest/assets/output_files/summaries/{self.file_name}.json'
                    



                    text = VideoProcessed_Repo.read_text_file(self.generated_text_file_path)
                    prompt = "Provide a summary of the transcript."

                    result = transcript.lemur.task(prompt)   
                    summary_data = {
                            'long_summary': result.response
                        }
                        # Write the summary data to a JSON file
                    with open( self.generated_summary_file_path, 'w') as json_file:
                            json.dump(summary_data, json_file, indent=4)
                            print(f"Long summary has been successfully saved to {self.generated_summary_file_path}.") 
                    text=VideoProcessed_Repo.Readjsonfile(json_chapters)
                    

                    processed_chapters = []
                    for chapter in text:
                        start_hms = VideoProcessed_Repo.milliseconds_to_hms(chapter['start'])
                        end_hms = VideoProcessed_Repo.milliseconds_to_hms(chapter['end'])
                        concise_title = VideoProcessed_Repo.generate_concise_title(chapter['headline'], OPENAI_API_KEY)
                        
                        processed_chapters.append({
                            'start': start_hms,
                            'end': end_hms,
                            'concise_title': concise_title
                        })
                    self.generated_chapters_file_path=f'mainServerTest/assets/output_files/Processed_Chapters/{self.file_name}.json'
                    with open(f'mainServerTest/assets/output_files/Chapters/processed_chapters_{self.file_name}.json', 'w') as outfile:
                        json.dump(processed_chapters, outfile, indent=4)
                    self.addProcessedMaterialToFirestore()

                    f=Flash_Cards(self.generated_text_file_path,self.user_ID,self.material_id,"TRANSCRIPT")
                    m=Questions_Repo(self.generated_text_file_path,self.user_ID,self.material_id,"TRANSCRIPT")
                    # os.remove(self.generated_audio_file_path)
                    # os.remove(self.generated_text_file_path)
                    # os.remove(json_chapters)
                    # os.remove(self.generated_chapters_file_path)
                    # os.remove(self.file_path)
                    # os.remove(self.generated_summary_file_path)
                    # if self.generated_video_file_path is not None:
                    # os.remove(self.generated_video_file_path)
                    return self.file_name,self.material_id
                except Exception as e:
                    print(e)
        else:
            print("the video already exists")
def main():
 print(VideoProcessed_Repo("mainServerTest/assets/input_files/video-based/Inflation Explained in One Minute.mp4","62a9c20699654da5b14cca9d21cd8ef6",False))
if __name__ == '__main__':
     main()
     