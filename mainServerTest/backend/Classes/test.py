#-------------------getting json from url----------------------------
# import requests
# from FirestoreDB import FirestoreDB


# def fetch_json_from_url(url):
#     try:
#         # Make a GET request to download the JSON file
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for any HTTP error status codes
        
#         # Load the JSON data
#         data = response.json()
#         return data
#     except requests.exceptions.RequestException as e:
#         print("Error:", e)
#         return None

# # URL of the JSON file
# url = "https://storage.googleapis.com/studywise-dba07.appspot.com/user/3f803d991c5b490887e6992fa5e58f71/Uploaded%20Materials/test/flashcards?Expires=4868648410&GoogleAccessId=firebase-adminsdk-56dni%40studywise-dba07.iam.gserviceaccount.com&Signature=iHCACA9pfomRl9vu%2FlUdOOpVvtU4Bkv2GhhuDxgQGjxw6EtTkk6y6d39OH5SSOpllvzDr6bbbjTNei6QPj4CI7zuBV3OeDLqn6BXaDkZfjsbIV17KMaU1D50L64zYbrsM7k9wZiUCtyTV4CyxzKFS46DuGbjEilsVjqo8leE8IIP2iHycnhsgpPLC0eGQpQimZu9onmp%2FATqnNkmCCoRfnc58mVWSpHwE8mCEuNW5ZQdD%2FD5XY97kZCxt1NuLhE1QTDxKgaHgDgdhjUOJeGi%2F1wVk1DHGPHOAK%2BDmfRdhTWezI29GOtAg3PJqmNkFLqHRdzU8yx6fVeb7JXrEw3aFQ%3D%3D"

# # Fetch JSON data from the URL
# json_data = fetch_json_from_url(url)

# if json_data:
#     print("JSON data:")
#     print(json_data)
# else:
#     print("Failed to fetch JSON data from the URL.")
#-------------------VideoMetaData-------------------------

# from moviepy.editor import VideoFileClip
# def get_video_metadata(file_path):
#     clip = VideoFileClip(file_path)
#     metadata = {
#         "duration": clip.duration,
#         "resolution": clip.size,
#         "fps": clip.fps,
#         "filename": clip.reader.filename,
#         "audio": {
#             "channels": clip.audio.nchannels if clip.audio else None,
#             "sample_rate": clip.audio.fps if clip.audio else None,
#         }
#     }
#     metadata_str = "Video Metadata:\n"
#     metadata_str += f"Duration: {metadata['duration']} seconds\n"
#     metadata_str += f"Resolution: {metadata['resolution'][0]}x{metadata['resolution'][1]}\n"
#     metadata_str += f"FPS: {metadata['fps']}\n"
#     metadata_str += f"Filename: {metadata['filename']}\n"
#     if metadata['audio']:
#         metadata_str += f"Audio Channels: {metadata['audio']['channels']}\n"
#         metadata_str += f"Audio Sample Rate: {metadata['audio']['sample_rate']} Hz\n"
#     return metadata_str



# file_path = "mainServerTest/assets/input_files/video-based/Inflation Explained in One Minute.mp4"
# metadata_string = get_video_metadata(file_path)
# print(metadata_string)
#---------------------------------------download a video---------------------------
# import os
# from pytube import YouTube
# def download_video_from_youtube(video_url, output_path):
   

#         # Create a YouTube object with the URL
#         yt = YouTube(video_url)
        
#         # Get the highest quality video stream
#         video_stream = yt.streams.get_highest_resolution()
        
#         # Define the filename for the video file
#         filename = yt.title + '.mp4'
#         # filename=filename.replace(" ","_")
#         # Download the video stream
#         video_stream.download(output_path=output_path, filename=filename)
        
#         # Construct the full path to the downloaded video file
#         video_file_path = ocs.path.join(output_path, filename)
#         video_file_path=video_file_path.replace("\\", "/")
#         video_file_path=video_file_path.replace(" ", "_")
        
#         yt.title=yt.title.replace(" ","_")
#         print(video_file_path)

#         # Return a tuple containing the path of the downloaded video file and the name of the video
#         return video_file_path, yt.title
# x,y=download_video_from_youtube("https://www.youtube.com/watch?v=zhWDdy_5v2w","mainServerTest/assets/input_files/video-based")
#--------------------------------------test mlo4 lazma----------------------------
# Assuming the list is stored in the variable `questions_data`
questions_data = [
    {
        'Questions_medium_location': 'https://storage.googleapis.com/studywise-dba07.appspot.com/user/62a9c20699654da5b14cca9d21cd8ef6/Uploaded%20Materials/Inflation%20Explained%20in%20One%20Minute/output_mcqs_medium.json?Expires=4868648802&GoogleAccessId=firebase-adminsdk-56dni%40studywise-dba07.iam.gserviceaccount.com&Signature=ZAbtUfgZDgDRRhfAi8YmECnNNUHEOuHfTcg%2F9sy4aiSqk8wTgvYb9%2F6nLf2n%2BeS2T2GJPMP3hmUdpxQPvz%2FzCtRKHQVeQ0H5ExckFbX19f%2BDRIXfTDY3QP5z25URmvsKsTV1lC0eujlwEsEBTKRFbTpJvuJ3rdLFWoHLF80M40DgtIXli7E%2FmEot3LsbnuzqW34L%2FVxTfh%2BNZ2wPhXvGgYh58aeijoPJb%2B54sKX1%2Bcy%2FCK7VmVRfNmX%2BF0X9vX08xM4o1dd%2BLAdgukBtY%2FNUDLDEBIKKjxfmm2XSW%2FQmbjAHMjil%2BpXOpkgtAwk1LfkmdpY7fGB4n1nITXVCbIdiaA%3D%3D',
        'Questions_hard_location': 'https://storage.googleapis.com/studywise-dba07.appspot.com/user/62a9c20699654da5b14cca9d21cd8ef6/Uploaded%20Materials/Inflation%20Explained%20in%20One%20Minute/output_mcqs_hard.json?Expires=4868648802&GoogleAccessId=firebase-adminsdk-56dni%40studywise-dba07.iam.gserviceaccount.com&Signature=jQt4PGNDRojU7mYUkL3U3g4XlZUdeQzcahyrQAJqzgyZFqVCZmUWs6X2TlXAWydYQN6u62UB99DqNLAWVHjytvSjCyDwCJjn2Aw8SJo4tJUwfpIjmRRn3GfmxT%2Be1mO2NEvuGUYGIpYIPgp4sXWWx%2BJM%2Bmk5vXThuSVvdpK9sgtz6bpB07mOisuOPt1FKfeEpxoW8q3tnvRgs5jqxk%2FI5%2FA8fF4l%2BYuBCet1xibBq%2BSAbzgkE4YchG9UzjAWybjlKwMRa2XJqmQGHbDnQtQLVM6t1sjzmKk4GAspPVYUprTB19nkJp9WbK4pD8tyqJnahOqrEwM34fdFe%2FWEFUnV2A%3D%3D',
        'Questions_easy_location': None
    }
]

# Access and print each link individually
for question in questions_data:
    medium_location = question['Questions_medium_location']
    hard_location = question['Questions_hard_location']
    easy_location = question['Questions_easy_location']
    print("Medium Location:", medium_location)
    print("Hard Location:", hard_location)
    print("Easy Location:", easy_location)
