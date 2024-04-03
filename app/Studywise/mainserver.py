from flask import *
from flask_socketio import SocketIO
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
from Model.Document_Controller import main as processDoc

# Familiarizing the app with the path to input text-based files
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(SERVER_DIR, '..', 'assets', 'input_files', 'text_based')
UPLOAD_FOLDER = os.path.normpath(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/generateContent', methods=['POST'])
def generate_content():
    data = request.json
    filename = data.get('filename')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        # Process the file in a background task
        socketio.start_background_task(processDoc, file_path)
        return jsonify({'message': 'File processing started'}), 200
    else:
        return jsonify({'error': 'File not found'}), 404