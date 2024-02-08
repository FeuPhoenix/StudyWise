from flask import Flask, request, jsonify
from flask_cors import CORS
from flashcards_from_pdf.flashcard_creator import runFlashcards

demoApp = Flask(__name__)
CORS(demoApp)

@demoApp.route('/makeFlashcards', methods=['POST'])
def makeFlashcards():
    received = request.get_json()
    chosenFile = received['value']
    runFlashcards("assets/input_files/text-based/"+chosenFile)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    demoApp.run(debug='true')