from flask import Flask, request, jsonify
from flask_cors import CORS
from Summaries.Video import main as processVideo


demoApp = Flask(__name__)
CORS(demoApp)

# import firebase_admin
# from firebase_admin import credentials, auth, initialize_app
# cred = credentials.Certificate("firebasetest/key.json")
# default_app=initialize_app(cred)

# demoApp = Flask(__name__)
# CORS(demoApp)
# cred = credentials.Certificate("path/to/serviceAccountKey.json")  # Replace with your service account JSON file
# default_app=initialize_app(cred)
# @demoApp.route('/signup', methods=['POST'])
# def signup():
#     email = request.json['email']
#     password = request.json['password']

#     try:
#         user = auth.create_user(email=email, password=password)
#         return jsonify({'status': 'success', 'message': 'User created successfully', 'user_id': user.uid})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})

# @demoApp.route('/login', methods=['POST'])
# def login():
#     email = request.json['email']
#     password = request.json['password']

#     try:
#         user = auth.get_user_by_email(email)
#         if user:
#             auth_user = auth.sign_in_with_email_and_password(email, password)
#             return jsonify({'status': 'success', 'message': 'Login successful', 'user_id': auth_user['localId']})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': 'Invalid email or password'})
# >>>>>>> mvc

@demoApp.route('/makeFlashcards', methods=['POST'])
def makeFlashcards():
    received = request.get_json()
    chosenFile = received['value']
    processVideo("assets/input_files/videos/"+chosenFile)

    return jsonify({'status': 'success'})

if __name__ == '__main__':
    demoApp.run(debug='true')