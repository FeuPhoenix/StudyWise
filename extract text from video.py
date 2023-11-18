import requests
import moviepy.editor as mp
import speech_recognition as sr
import requests
import time
API_KEY_ASSEMBLYAI = '387c065c75c04214a0dd420085296a70'

upload_endpoint = 'https://api.assemblyai.com/v2/upload'
transcript_endpoint = 'https://api.assemblyai.com/v2/transcript'

headers_auth_only = {'authorization': API_KEY_ASSEMBLYAI}

headers = {
    "authorization": API_KEY_ASSEMBLYAI,
    "content-type": "application/json"
}

  #


def upload(filename):
    def read_file(filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read()
                if not data:
                    break
                yield data

    upload_response = requests.post(upload_endpoint, headers=headers_auth_only, data=read_file(filename))
    return upload_response.json()['upload_url']


def transcribe(audio_url):
    transcript_request = {
        'audio_url': audio_url
    }

    transcript_response = requests.post(transcript_endpoint, json=transcript_request, headers=headers)
    return transcript_response.json()['id']


def poll(transcript_id):
    polling_endpoint = transcript_endpoint + '/' + transcript_id
    polling_response = requests.get(polling_endpoint, headers=headers)
    return polling_response.json()


def get_transcription_result_url(url):
    transcribe_id = transcribe(url)
    while True:
        data = poll(transcribe_id)
        if data['status'] == 'completed':
            return data, None
        elif data['status'] == 'error':
            return data, data['error']

        print("waiting for 30 seconds")
        time.sleep(30)


def save_transcript(url, title):
    data, error = get_transcription_result_url(url)

    if data:
        filename = title + '.txt'
        with open(filename, 'w') as f:
            f.write(data['text'])
        print('Transcript saved')
    elif error:
        print("Error!!!", error)
def main():
 video = mp.VideoFileClip("How I'd Learn AI in 2023 (if I could start over).mp4")

 audio = video.audio
 audio.write_audiofile("extracted_audio.wav")
 filename = "extracted_audio.wav"
 audio_url = upload(filename)
 save_transcript(audio_url, 'transcribed_text')
if __name__ == "__main__":
  main()
