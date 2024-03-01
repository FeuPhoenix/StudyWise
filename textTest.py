from flask import Flask, request, jsonify
from flask_cors import CORS
<<<<<<< HEAD
from Summaries.Video import main as processVideo
=======
from Summaries.Document2 import main as processDocument
>>>>>>> mvc

demoApp = Flask(__name__)
CORS(demoApp)

@demoApp.route('/makeFlashcards', methods=['POST'])
def makeFlashcards():
    received = request.get_json()
    chosenFile = received['value']
<<<<<<< HEAD
    processVideo("assets/input_files/text-based/"+chosenFile)
=======
    processDocument("assets/input_files/text-based/"+chosenFile)
>>>>>>> mvc

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    demoApp.run(debug='true')