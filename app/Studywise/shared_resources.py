import os
from werkzeug.utils import secure_filename
from flask import Flask, request, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS


# Main flask testing being made by DIDO. 
# DO NOT CHANGE

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# import firebase_admin
# from firebase_admin import credentials, auth, initialize_app
# cred = credentials.Certificate("firebasetest/key.json")
# default_app=initialize_app(cred)

# app = Flask(__name__)
# CORS(app)
# cred = credentials.Certificate("path/to/serviceAccountKey.json")  # Replace with your service account JSON file
# default_app=initialize_app(cred)
# @app.route('/signup', methods=['POST'])
# def signup():
#     email = request.json['email']
#     password = request.json['password']

#     try:
#         user = auth.create_user(email=email, password=password)
#         return jsonify({'status': 'success', 'message': 'User created successfully', 'user_id': user.uid})
#     except Exception as e:
#         return jsonify({'status': 'error', 'message': str(e)})

# @app.route('/login', methods=['POST'])
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

@app.route('/generateContent', methods=['POST'])
def generateContent():
    from Model.Document_Controller import main as processDoc

    try:
        received = request.get_json()
        chosenFile = received.get('value')
        print("File Name:\n", chosenFile)
        if not chosenFile:
            return jsonify({'status': 'error', 'message': 'No file specified'}), 400
        
        # Use secure_filename to avoid path traversal vulnerabilities
        safe_filename = secure_filename(chosenFile)
        file_path = os.path.join(app.root_path, 'assets', 'input_files', 'text_based', safe_filename)
        print("File Path:\n", file_path)

        # Check if file exists
        if not os.path.isfile(file_path):
            return jsonify({'status': 'error', 'message': 'File not found'}), 404
        
        # Run main backend processing for document
        processDoc(file_path)

        return jsonify({'status': 'success'})
    
    except Exception as e:
        # Log the exception here
        return jsonify({'status': 'error', 'message': 'Internal Server Error'}), 500

if __name__ == '__main__':
    socketio.run(app, debug=True)