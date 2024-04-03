from flask import *
from flask_socketio import SocketIO
import os
from werkzeug.utils import secure_filename
from flask_cors import CORS
from app.Studywise.Model.Document_Controller import main as processDoc

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Familiarizing the app with the path to input text-based files
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(SERVER_DIR, '..', 'assets', 'input_files', 'text_based')
UPLOAD_FOLDER = os.path.normpath(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        socketio.emit('update', {'message': f'File {filename} successfully uploaded'})
        return jsonify({'message': 'File successfully uploaded'}), 200
    else:
        return jsonify({'error': 'File type not allowed'}), 400
    
@app.route('/generateContent', methods=['POST'])
def generate_content():
    data = request.json
    filename = data.get('filename')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

    if os.path.exists(file_path):
        processDoc(file_path)
        socketio.emit('update', {'message': f'Processing started for {filename}'})
        
        # Simulate processing completion
        socketio.emit('update', {'message': f'Processing completed for {filename}'})
        
        return jsonify({'message': 'Processing initiated'}), 200
    else:
        return jsonify({'error': 'File not found'}), 404
    
@app.route('/uploads/<filename>')
def serve_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404

if __name__ == '__main__':
    socketio.run(app, debug=True)