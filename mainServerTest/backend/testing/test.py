from moviepy.editor import VideoFileClip
import os

class VideoProcessor:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = self.getFileNameFromPathWithoutExtension(self.file_path)
        self.generated_audio_file_path = None

    @staticmethod
    def getFileNameFromPathWithoutExtension(input_string):
        """Extract file name without extension from a file path."""
        last_slash_index = input_string.rfind('/')
        result_string = input_string[last_slash_index + 1:].replace('.mp4', '')
        return result_string

    def extract_audio(self):
        video = VideoFileClip(self.file_path)
        print("Video name: " + self.file_name)
        print('Video is initialized')

        # Extract audio from video
        audio = video.audio
        print('Video audio is extracted')

        # Ensure the output directory exists
        output_dir = "mainServerTest/assets/output_files/audio"
        os.makedirs(output_dir, exist_ok=True)

        # Use a shorter and simpler file name
        output_file = f"{output_dir}/{self.file_name}.mp3".replace('\\', '/')
        print(f"Saving audio to: {output_file}")

        audio.write_audiofile(output_file, codec='mp3')
        self.generated_audio_file_path = output_file
        print(f"Audio file downloaded at: {self.generated_audio_file_path}")

# Example usage
file_path = "D:/COLLEGE/StudyWise/mainServerTest/assets/input_files/video-based/What is Artificial Intelligence _ Artificial Intelligence Tutorial For Beginners _ Edureka.mp4"
processor = VideoProcessor(file_path)
processor.extract_audio()