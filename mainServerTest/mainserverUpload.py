from flask import Flask, jsonify, render_template, request, send_from_directory, url_for, redirect, session
import time
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

ALLOWED_EXTENSIONS = {'ppt','pptx','txt', 'pdf', 'docx', 'doc'}

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
def landing_page():
    return render_template('main_landing/login.html')

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
    
@app.route('/login')
def login():
    return render_template('main_landing/login.html')


@app.route('/home')
def home():    
    if "UserID" in session : 
        userID = session['UserID']
        userName = session['UserName']
        
        print('\n==============================USER IN HOME================================\n',
                f'\t\tID: {userID}\n',
                f'\t\tName: {userName}',
                '\n================================USER IN HOME==============================\n')
    else : 
        return redirect(url_for(login))

    return render_template('main_loggedin/index.html')

@app.route('/get-user-name-JSON', methods=['POST'])
def get_user_name_JSON():
    return jsonify({'userName':f'{session['UserName']}'})

@app.route('/load-user-content')
def load_user_content():
    from backend.Classes.Document_Controller import DocumentProcessedController
    
    contentJson = DocumentProcessedController.fetch_all_filenames_and_filetypes_in_Video_and_Document_material(userID)
    session["usercontent"]
    if "UserContent" in session : 
        if contentJson != None : 
            print('\n==============================USER CONTENT================================\n',
                f'\t\tName: {session['userName']}\n',
                f'\t\tCONTENT: \n{contentJson}',
                '\n================================USER CONTENT==============================\n')
            return contentJson, '200 - User countent sent'
        else : 
            print('\n==============================USER CONTENT================================\n',
                f'\t\tName: {session['userName']}\n',
                f'\t\tNO USER CONTENT FOUND',
                '\n================================USER CONTENT==============================\n')
            return jsonify({'status': 'No user content'}), '404 - User content not found'
        
@app.route('/sign-out')
def sign_out():
    session.clear()
    print('\n==============================================================\n',
          '\n',
          '\t\t\tCLEARED SESSION VARIABLES\n',
          '\n',
          '\n==============================================================\n')
    return redirect(url_for('login'))


@app.route('/process-signup', methods = ['POST']) 
def process_signup():
    data = request.json
    fName = data.get('fName')
    signupEmail = data.get('signupEmail')
    signupPW = data.get('signupPW')
    if fName and signupEmail and signupPW : 
        print('\n=============================_NEW SIGN UP_=============================\n',
              '\tRecieved: ', fName, signupEmail, signupPW)

        # Get socket ID to emit updates specific to it
        socketID = data.get('socketID')

        from backend.Classes.User_Controller import UserController

        status = UserController.SignUp(signupEmail, fName, signupPW) # Returns true when User is created, None if User exists
        
        print('\tDecrypted: Name:', UserController.decrypt_string(fName), ', Email:', UserController.decrypt_string(signupEmail), ', Password:', UserController.decrypt_string(signupPW), 
              '\n=============================_END SIGN UP_=============================\n')
        if status == True :
            socketio.emit('update', {'message': 'Signup Success'}, to=socketID)
            print(f"Signed up: {UserController.decrypt_string(fName)} \nWith Email: {UserController.decrypt_string(signupEmail)}\n\nLogging in\n\n")

            userID, fullName, status = UserController.Login(signupEmail, signupPW)

            if status :
                # Print Confirmation of User data
                print(f'Logged in: {fullName}')
                print(f'User ID: {userID}')
                
                # Create session variables with user's firebase ID and user's full name as values
                session["UserID"] = userID
                session["UserName"] = fullName

                return jsonify({'message': 'Signup Success'}), 200
            else :
                print(f"Failed Login attempt")
                return jsonify({'message': 'Failed Login attempt'}), 406
        
        elif status == None :
            print(f"Failed Signup attempt: USER ALREADY EXISTS")
        return jsonify({'message': 'User already exists'}), 406
    
    else :
        print(f"Failed Signup attempt")
        return jsonify({'message': 'Failed Signup attempt'}), 406


@app.route('/process-login', methods = ['POST']) 
def process_login():
    data = request.json
    loginEmail = data.get('loginEmail')
    loginPW = data.get('loginPW')
    socketID = data.get('socketID')


    from backend.Classes.User_Controller import UserController
    userID, fullName, status = UserController.Login(loginEmail, loginPW)

    if status :
        socketio.emit('update', {'message': 'Login Success'}, to=socketID)

        # Print Confirmation of User data
        print(f'Logged in: {fullName}')
        print(f'User ID: {userID}')
        
        # Create session variables with user's firebase ID and user's full name as values
        session["UserID"] = userID
        session["UserName"] = fullName

        return jsonify({'message': 'Login Success'})
    else :
        print(f"Failed Login attempt")
        return jsonify({'message': 'Failed Login attempt'}), 406

@app.route('/process-logout', methods = ['POST']) 
def process_logout():
    session.pop('UserID')
    session.pop('UserName')

@app.route('/generateContent', methods = ['POST'])
def generate_content():
    data = request.json
    filename = data.get('filename')
    socketID = data.get('socketID')
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'text-based\\'+filename)

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
    
@app.route("/generateTextContent", methods = ['POST'])
def generate_text_content():
    print('HELLO HELLO HELLO')
    data = request.json
    filename = data.get('filename')
    print('Recieved: ', filename)
    socketID = data.get('socketID')
    print('Recieved: ', socketID)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'text-based',filename)
    print('UPLOAD FOLDER: ',file_path)

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
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'video-based/'+filename)

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
    directory = safe_join(app.root_path, 'assets/input_files/text-based')
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
    # from backend.Classes.FirestoreDB import FirestoreDB
    # FirestoreDB.get_instance()
    socketio.run(app, port="5000", debug=True)