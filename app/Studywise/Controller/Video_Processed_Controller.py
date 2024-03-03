from datetime import datetime
import json
import time
from firebase_admin import firestore
from openai import OpenAI
import openai
from Constants.Constants import OPENAI_API_KEY, MAX_TOKENS_PER_REQUEST,kUserId,kUserEmail ,kDatejoined ,kFullName
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
from app.Studywise.Model import FirestoreDB, VideoProcessed_Repo
from app.Studywise.Model.VideoProcessed_Repo import MaterialProcessed, VideoProcessed
from app.Studywise.Model import Material_Repo
import firebase_admin
from firebase_admin import credentials, storage
from flask import request,jsonify,render_template
import uuid

from audiocutter import runaudiocutter

class Video_Processed_Controller:
    
    def __init__(self,material):
        self.material=material
        self.db = FirestoreDB.get_instance()
    def Save_ProcessedVideo_to_database(self,generated_summary_file_path,generated_audio_file_path,generated_chapters_file_path,generated_text_file_path,generated_images_file_path,generated_video_file_path):
        processed_material_id = uuid.uuid4().hex
        Video_Token=VideoProcessed.upload_to_firebase(generated_video_file_path,f'{kUserId}/{Video_Processed_Controller.getFileNameFromPathWithOutExtension(generated_video_file_path)}.mp4')
        Audio_Token=VideoProcessed.upload_to_firebase(generated_audio_file_path,f'{kUserId}/{Video_Processed_Controller.getFileNameFromPathWithOutExtension(generated_audio_file_path)}.wav')
        videoprocessed = VideoProcessed(processed_material_id,self.material, generated_summary_file_path, Audio_Token, generated_chapters_file_path,generated_text_file_path,generated_images_file_path,Video_Token)
        
        
        try:
            videoprocessed.addProcessedMaterialToFirestore()

            return jsonify({"success": True, "message": "processed_material created successfully"}), 200
        except Exception as e:
               return jsonify({"success": False, "message": str(e)}), 500

    
    # The metadata might include a token which you can access like this
    # Note: The structure of metadata might vary, ensure to check the keys
       
    

    async def get_processed_material(self, processed_material_id):
        material_doc = await self.db.collection('MaterialsProcessed')\
                                             .document(kUserId)\
                                             .collection('MaterialsProcessed')\
                                             .document(processed_material_id)\
                                             .get()
        if material_doc.exists:
            material_data = material_doc.to_dict()
            return VideoProcessed.fromJson(material_data)
        else:
            return None

   
    async def delete_processed_material(self, processed_material_id):
        try:
            await self.db.collection('MaterialsProcessed').document(processed_material_id).delete()
        except Exception as e:
            print(e)
    
    # async def update_processed_material(self, processed_material_id, data):
    #     try:
    #         await self.db.collection('MaterialsProcessed').document(processed_material_id).update(data)
    #     except Exception as e:
    #         print(e)
    @staticmethod       
    def split_text(self,text, max_chunk_size=3800):  # Reduced max_chunk_size for safety
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
    def is_mp4_file(self,file_path):
        extension = os.path.splitext(file_path)[1]
        if extension == ".mp4":
            print("True")
            return True
        else:
            print("Flase")
            return False
    @staticmethod
    def getFileNameFromPathWithOutExtension(self,input_string):
    # Find the last occurrence of '/'
        last_slash_index = input_string.rfind('/')
        
        # Slice the string from the character after the last '/'
        # If '/' is not found, rfind returns -1, and slicing starts from index 0
        result_string = input_string[last_slash_index + 1:]
        result_string=result_string.replace('.mp4','')
        return result_string
    @staticmethod
    def milliseconds_to_hms(self,ms):
        ms=int(ms)
        seconds = int(ms / 1000)
        return str(timedelta(seconds=seconds))
    @staticmethod
    def generate_concise_title(self,headline, api_key):
        while True:
            try:
                headers = {"Authorization": f"Bearer {api_key}"}
                OpenAI.api_key = api_key
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
    def Readjsonfile(self,filename):
        with open(filename, 'r') as file:
            chapters = json.load(file)
        return chapters


    @staticmethod
    def download_video_from_youtube(self,video_url, output_path):
   

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
    def read_text_file(self,file_path):
        with open(file_path, 'r') as file:
            return file.read()
    
    @staticmethod
    def get_Long_summary(self,text, api_key):
        openai.api_key = api_key
        summaries = []

        for chunk in Video_Processed_Controller.split_text(text):
            while True:  # Keep trying until successful
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a helpful assistant."},
                            {"role": "user", "content": f"Summarize the following text into concise bullet points, focusing only on essential information: \n{chunk}"}
                        ]
                    )
                    summaries.append(response['choices'][0]['message']['content'].strip())
                    break  # Exit the loop if successful
                except openai.error.RateLimitError as e:
                    print("Rate limit exceeded, waiting to retry...")
                    time.sleep(20)  # Wait for 20 seconds before retrying

        full_summary = ' '.join(summaries)
        return full_summary
    
    def Video_Processing(self,file_path_or_url):

    # Check if the input is a local file with the extension .mp4
        
        if  Video_Processed_Controller.is_mp4_file(file_path_or_url):
            output_path = 'assets/input_files/videos'
            video_file_path = os.path.join(output_path, file_path_or_url)
            new_video_file_path = video_file_path.replace(" ", "_")
            new_video_file_path = new_video_file_path.replace("\\", "/")
            print(new_video_file_path)
            os.rename(video_file_path, new_video_file_path)
            
            videocutted = runaudiocutter(file_path_or_url)
            print("Audiocutter output file: "+file_path_or_url)

            Video_name = Video_Processed_Controller.getFileNameFromPathWithOutExtension(new_video_file_path
                                                            )
            print("Video_name: "+video_file_path)
            video = mp.VideoFileClip(videocutted)
            print('video is initialized')
            audio = video.audio
            print('video.audio is extracted')
            audio.write_audiofile(f"assets/output_files/extracted_audio_from_{Video_name}.wav")
            audio_file_path = f"assets/output_files/extracted_audio_from_{Video_name}.wav"
            print(f"Audio file downloaded at: {audio_file_path}") 
            config = aai.TranscriptionConfig(auto_chapters=True)

            # Transcribe the audio and get the result as a JSON object
            transcript = aai.Transcriber().transcribe(audio_file_path, config)
            
            transcript_filename = f"assets/output_files/extracted_transcripts/{Video_name}.txt"
            with open(transcript_filename, 'w', encoding='utf-8') as transcript_file:
                    transcript_file.write(transcript.text)
                    print(f"Full transcript has been successfully saved to {transcript_filename}.")
            #runFlashcards(transcript_filename, 'TRANSCRIPT')
            chapters_data = []

            # Iterate over chapters and add their data to the list
            for chapter in transcript.chapters:
                chapters_data.append({
                    "start": chapter.start,
                    "end": chapter.end,
                    "headline": chapter.headline
                }) 
                    
            json_chapters = f'assets/output_files/Chapters/chapters_results_{Video_name}.json'

    # Write the chapters data to a JSON file
            with open(json_chapters, 'w') as json_file:
                json.dump(chapters_data, json_file, indent=4)
            
            print(f"Chapters have been successfully saved to {json_chapters}.")
            
            text_file_path = f'assets/output_files/extracted_transcripts/{Video_name}.txt'
            json_file_path = f'assets/output_files/Summaries/{Video_name}.json'
            



            text = Video_Processed_Controller.read_text_file(text_file_path)
            long_summary = Video_Processed_Controller.get_Long_summary(text, OPENAI_API_KEY)
            summary_data = {
                    'long_summary': long_summary
                }
                # Write the summary data to a JSON file
            with open(json_file_path, 'w') as json_file:
                    json.dump(summary_data, json_file, indent=4)
                    print(f"Long summary has been successfully saved to {json_file_path}.") 
            text=Video_Processed_Controller.Readjsonfile(json_chapters)
            

            processed_chapters = []
            for chapter in text:
                start_hms = Video_Processed_Controller.milliseconds_to_hms(chapter['start'])
                end_hms = Video_Processed_Controller.milliseconds_to_hms(chapter['end'])
                concise_title = Video_Processed_Controller.generate_concise_title(chapter['headline'], OPENAI_API_KEY)
                
                processed_chapters.append({
                    'start': start_hms,
                    'end': end_hms,
                    'concise_title': concise_title
                })

            with open(f'assets/output_files/Chapters/processed_chapters_{Video_name}.json', 'w') as outfile:
                json.dump(processed_chapters, outfile, indent=4)
            v=VideoProcessed(json_file_path,audio_file_path,f'assets/output_files/Chapters/processed_chapters_{Video_name}.json',text_file_path,None,videocutted)
            self.Save_ProcessedVideo_to_database(v)
        # Check if the input is a YouTube video link
        # youtube_regex = (
        #     r'(https?://)?(www\.)?'
        #     r'(youtube|youtu|youtube-nocookie)\.(com|be)/'
        #     r'(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
        # match = re.match(youtube_regex, file_path_or_url)
        else:
            print("skipped if")
            video_url = file_path_or_url  
            output_path = 'assets/input_files/videos'  
            video_file_path,title = Video_Processed_Controller.download_video_from_youtube(video_url, output_path)
            print("the video has been downloaded successfully")
            #videocutted=runaudiocutter(video_file_path)
            print(video_file_path)
            video = mp.VideoFileClip(video_file_path)

            audio = video.audio
            audio.write_audiofile(f"assets/output_files/audio/extracted_audio_from_{title}.wav")
            audio_file_path = f"assets/output_files/extracted_audio_from_{title}.wav"
            print(f"Audio file downloaded at: {audio_file_path}") 
            config = aai.TranscriptionConfig(auto_chapters=True,)

            # Transcribe the audio and get the result as a JSON object
            transcript = aai.Transcriber().transcribe(video_file_path, config)
            transcript_filename = f"assets/output_files/extracted_transcripts/{title}.txt"
            with open(transcript_filename, 'w', encoding='utf-8') as transcript_file:
                    transcript_file.write(transcript.text)
                    print(f"Full transcript has been successfully saved to {transcript_filename}.")
            #runFlashcards(transcript_filename, 'TRANSCRIPT')
            chapters_data = []

            # Iterate over chapters and add their data to the list
            for chapter in transcript.chapters:
                chapters_data.append({
                    "start": chapter.start,
                    "end": chapter.end,
                    "headline": chapter.headline
                }) 
                    
            json_chapters = f'assets/output_files/Chapters/chapters_results_{title}.json'

    # Write the chapters data to a JSON file
            with open(json_chapters, 'w') as json_file:
                json.dump(chapters_data, json_file, indent=4)
            
            print(f"Chapters have been successfully saved to {json_chapters}.")
            
            text_file_path = f'assets/output_files/extracted_transcripts/{title}.txt'
            json_file_path = f'assets/output_files/Summaries/{title}.json'
            



            text = Video_Processed_Controller.read_text_file(text_file_path)
            long_summary = self.get_Long_summary(text, OPENAI_API_KEY)
            summary_data = {
                    'long_summary': long_summary
                }
                # Write the summary data to a JSON file
            with open(json_file_path, 'w') as json_file:
                    json.dump(summary_data, json_file, indent=4)
                    print(f"Long summary has been successfully saved to {json_file_path}.") 
            text=Video_Processed_Controller.Readjsonfile(json_chapters)
            

            processed_chapters = []
            for chapter in text:
                start_hms = Video_Processed_Controller.milliseconds_to_hms(chapter['start'])
                end_hms = Video_Processed_Controller.milliseconds_to_hms(chapter['end'])
                concise_title = Video_Processed_Controller.generate_concise_title(chapter['headline'], aai.settings.api_key)
                
                processed_chapters.append({
                    'start': start_hms,
                    'end': end_hms,
                    'concise_title': concise_title
                })

            with open(f'assets/output_files/Chapters/processed_chapters_{title}.json', 'w') as outfile:
                json.dump(processed_chapters, outfile, indent=4)
            self.Save_ProcessedVideo_to_database(json_file_path,audio_file_path,f'assets/output_files/Chapters/processed_chapters_{Video_name}.json',text_file_path,None,videocutted)
