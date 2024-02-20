from flask import Flask, request, jsonify
from flask_cors import CORS
from Summaries.Video import main as processVideo

demoApp = Flask(__name__)
CORS(demoApp)

@demoApp.route('/makeFlashcards', methods=['POST'])
def makeFlashcards():
    received = request.get_json()
    chosenFile = received['value']
    processVideo("assets/input_files/videos/"+chosenFile)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    demoApp.run(debug='true')