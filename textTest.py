from flask import Flask, request, jsonify
from flask_cors import CORS
from Summaries.Document2 import main as processDocument

demoApp = Flask(__name__)
CORS(demoApp)

@demoApp.route('/makeFlashcards', methods=['POST'])
def makeFlashcards():
    received = request.get_json()
    chosenFile = received['value']
    processDocument("assets/input_files/text-based/"+chosenFile)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    demoApp.run(debug='true')