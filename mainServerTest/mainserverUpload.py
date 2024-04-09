from flask import *
from config import socketio
import os
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from flask_cors import CORS
from dotenv import load_dotenv
# Chat imports
import openai
import fitz  # PyMuPDF

app = Flask(__name__)
CORS(app)
socketio.init_app(app, cors_allowed_origins="http://127.0.0.1:5000") # , logger=True, engineio_logger=True

app.secret_key = os.getenv('FLASK_APP_SECRET_KEY', 'a_default_secret_key')

# Define UPLOAD_FOLDER for PDF chat functionality
CHAT_UPLOAD_FOLDER = 'C:\\Users\\AMR\\Desktop\\pro\\StudyWise\\chat_with_pdf'
app.config['UPLOAD_FOLDER'] = CHAT_UPLOAD_FOLDER  # You might need to adjust this if using both functionalities

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

# Familiarizing the app with the path to input text-based files
SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join('mainServerTest', 'assets', 'input_files')
UPLOAD_FOLDER = os.path.normpath(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'doc'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



# ↓ Mainly for SocketIO connection debugging ↓
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')



@app.route('/')
def home():
    return render_template('main_loggedin/index.html')

@app.route('/text-upload')
def text_home():
    return render_template('main_loggedin/upload-doc.html')

@app.route('/video-upload')
def video_home():
    return render_template('main_loggedin/upload-video-based.html')

@app.route('/pdf-display')
def pdf_display():
    return render_template('main_loggedin/view-pdf.html')

@app.route('/video-display')
def video_display():
    return render_template('main_loggedin/view-video.html')
    
@app.route('/generateContent', methods = ['POST'])
def generate_content():
    data = request.json
    filename = data.get('filename')
    socketID = data.get('socketID')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'text_based/'+filename)

    if os.path.exists(file_path):
        from backend.Document_Controller import main as processDoc
        print("Sending path to process: "+file_path)

        socketio.emit('update', {'message': f'Starting processing for {filename}'}, to=socketID)
        processDoc(file_path)
        
        # Simulate processing completion
        socketio.emit('update', {'message': 'Processing completed'})
        
        return jsonify({'message': 'Processing initiated'}), 200
    else:
        return jsonify({'error': '('+file_path+') File not found'}), 404
    
@app.route('/generateVideoContent', methods = ['POST'])
def generate_video_content():
    data = request.json
    filename = data.get('filename')
    socketID = data.get('socketID')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'video_based/'+filename)

    if os.path.exists(file_path):
        from backend.VideoProcessed_Controller import main as processVid
        print("Sending path to process: "+file_path)

        socketio.emit('update', {'message': f'Started processing for {filename}'}, to=socketID)
        processVid(file_path)
        
        # Simulate processing completion
        socketio.emit('update', {'message': 'Processing completed'})
        
        return jsonify({'message': 'Processing initiated'}), 200
    else:
        return jsonify({'error': '('+file_path+') File not found'}), 404
    
@app.route('/uploads/<filename>')
def serve_file(filename):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    except FileNotFoundError:
        return jsonify({'error': 'File not found'}), 404
    

@app.route('/api/files/pdf/<filename>')
def serve_pdf(filename):
    directory = safe_join(app.root_path, 'assets/input_files/text_based')
    return send_from_directory(directory, filename)

@app.route('/api/files/summaries/<filename>')
def serve_summary(filename):
    directory = safe_join(app.root_path, 'assets/output_files/summaries')
    return send_from_directory(directory, filename)

@app.route('/api/files/flashcards/<filename>')
def serve_flashcards(filename):
    directory = safe_join(app.root_path, 'assets/output_files/flashcards')
    return send_from_directory(directory, filename)

@app.route('/api/files/mcqs/<filename>')
def serve_mcqs(filename):
    directory = safe_join(app.root_path, 'assets/output_files/mcq')
    return send_from_directory(directory, filename)

@app.route('/api/files/video-mp4/<filename>')
def serve_video(filename):
    directory = safe_join(app.root_path, 'assets/input_files/video_based')
    return send_from_directory(directory, filename)

@app.route('/api/files/indexing/<filename>')
def serve_indexes(filename):
    directory = safe_join(app.root_path, 'assets/output_files/Processed_Chapters')
    return send_from_directory(directory, filename)


# PDF CHAT ========================================================================
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    filename = secure_filename(file.filename)

    if allowed_file(filename, type='chat_pdf'):
        # Save the file to the specified directory (common operation)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Generate a URL to access the file (specific to chat_pdf)
        file_url = url_for('uploaded_file', filename=filename, _external=True)
        return jsonify({'status': 'success', 'fileUrl': file_url})

    elif allowed_file(filename, type='existing_functionality'):
        # The file has already been saved above
        socketio.emit('update', {'message': f'File {filename} successfully uploaded'})
        return jsonify({'message': 'File successfully uploaded'}), 200

    else:
        return jsonify({'error': 'File type not allowed'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

def extract_text_from_pdf(filepath):
    text = ''
    with fitz.open(filepath) as doc:
        for page in doc:
            text += page.get_text()
    return text

# Route to handle chat interaction
@app.route('/chat/<file>', methods=['POST'])
def chat(file):
    text_file = file.rsplit('.', 1)[0]
    text_file = text_file + ".txt"

    user_input = request.json['message']
    text_file_path = safe_join(app.root_path, f'assets/output_files/text_files/{text_file}')
    pdf_text = extract_text_from_pdf(text_file_path)

    # Combine PDF text with user input for the conversation with GPT-3.5 Turbo
    conversation_history = [
        {"role": "system", "content": pdf_text},
        {"role": "user", "content": user_input}
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=conversation_history
    )

    # Extract the response text
    response_text = response.choices[0].message['content']
    return jsonify({'response': response_text})

@app.route('/chatwithpdf')
def chat_with_pdf():
    filename = request.args.get('file')
    file_url = url_for('uploaded_file', filename=filename)
    return render_template('main_loggedin/chatwithpdf.html', file_url=file_url)

@app.route('/mcq')
def mcq():
    filename = request.args.get('file')
    file_url = url_for('uploaded_file', filename=filename)
    return render_template('main_loggedin/generate_mcqs.html', file_url=file_url)

if __name__ == '__main__':
    socketio.run(app, debug=True)