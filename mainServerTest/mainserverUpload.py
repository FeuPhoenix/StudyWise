import smtplib
from flask import Flask, jsonify, render_template, request, send_from_directory, url_for, redirect, session
from config import socketio
import os
from werkzeug.utils import secure_filename
from werkzeug.security import safe_join
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
# Chat imports
import openai
import requests
import fitz  # PyMuPDF
from backend.Classes.User_Controller import UserController
app = Flask(__name__)
CORS(app, origins="*", allow_headers="*")
socketio.init_app(app, cors_allowed_origins="*") # , logger=True, engineio_logger=True

app.secret_key = os.getenv('FLASK_APP_SECRET_KEY', 'a_default_secret_key')

# Define UPLOAD_FOLDER for PDF chat functionality
CHAT_UPLOAD_FOLDER = 'C:\\Users\\AMR\\Desktop\\pro\\StudyWise\\chat_with_pdf'
app.config['UPLOAD_FOLDER'] = CHAT_UPLOAD_FOLDER  # You might need to adjust this if using both functionalities

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")



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
    if "UserID" in session : 
        print('\nClient connected: ', session["UserName"], '\n')
    else : 
        print('\nSocketIO connection established\n')

@socketio.on('disconnect')
def handle_disconnect():
    if "UserID" in session : 
        print('\nClient disconnected: ', session["UserName"], '\n')
    else : 
        print('\nSocketIO connection terminated\n')

@app.route('/')
def landing_page():
    return render_template('main_landing/index.html')

@app.route('/FAQs')
def faqs():
    return render_template('main_landing/FAQ.html')

@app.route('/plans')
def plans():
    return render_template('main_landing/plans.html')

@app.route('/login')
def login():
    handle_connect()
    return render_template('main_landing/login.html')

@app.route('/log-out')
def log_out():
    handle_disconnect()
    session.clear()
    print('\n==============================================================\n',
          '\n',
          '\t\tCLEARED SESSION VARIABLES\n',
          '\n',
          '\n==============================================================\n')
    
    return redirect(url_for('login'))

@app.route('/text-upload')
def text_home():
    session['fileType'] = 'document'
    return render_template('main_loggedin/upload-doc.html')

@app.route('/video-upload')
def video_home():
    session['fileType'] = 'video'
    return render_template('main_loggedin/upload-video-based.html')

@app.route('/process-video-link<link>')
def process_video_link(link):

    print('Link to process:', link)

    return render_template('main_loggedin/upload-video-based.html')

@app.route('/pdf-display')
def pdf_display():
    return render_template('main_loggedin/view-pdf.html')

@app.route('/video-display')
@cross_origin()
def video_display():
    return render_template('main_loggedin/view-video.html')

@app.route('/audio-display')
@cross_origin()
def audio_display():
    return render_template('main_loggedin/view-audio.html')

@app.route('/change_name', methods=['POST', 'GET'])
def change_name():
    data = request.json
    new_name = data.get('newName')
    print(new_name)
    if new_name:
        try:
            id = session['UserID']
            print("id", id)
            UserController.changeName(id, new_name)
            session['UserName'] = new_name
            return jsonify({'success': True}), 200
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'New name not provided'}), 400
    
@app.route('/change_password', methods=['POST'])
def change_password():
    data = request.json
    newPassword = data.get('newPassword')
    print(newPassword)
    if newPassword is not None:
        try:
            id = session['UserID']
            print("id", id)
            UserController.ChangePassword(session['UserID'], newPassword)
            session['UserName'] = session['UserName']
            return jsonify({'success': True}), 200
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'New Password not provided'}), 400
    
    data = request.json
    newPassword = data.get('newPassword')
    print(newPassword)
    # Your logic to update the username in Firebase or perform any other action
    # Replace this example logic with your actual implementation
    if newPassword!=None:
        try:
            id=session['UserID']
            print("id",id)
            UserController.ChangePassword(session['UserID'], newPassword)
            session['UserName'] = session['UserName']
            return jsonify({'success': True}), 200
        except Exception as e:
            print(e)
            return jsonify({'success': False, 'error': str(e)}), 500
    else:
        return jsonify({'success': False, 'error': 'New Password not provided'}), 400

@app.route('/home')
def home():    
    if "UserID" in session : 
        
        userID = session['UserID']
        userName = session['UserName']
        print("Username",userName)
        
        print('\n==============================USER IN HOME================================\n',
             f'\t\tID: {userID}\n',
             f'\t\tName: {userName}',
              '\n================================USER IN HOME==============================\n')
    else : 
        return redirect(url_for('login'))

    return render_template('main_loggedin/index.html')

@app.route('/get-user-name-JSON', methods=['POST'])
def get_user_name_JSON():
    return jsonify({'userName': f"{session['UserName']}"})

@app.route('/load-user-content-JSON', methods=['POST'])
def load_user_content_JSON():
    from backend.Classes.Document_Controller import DocumentProcessedController
    userID = session['UserID']
    print(userID)
    print('Fetching user content')
    contentJSON = DocumentProcessedController.fetch_all_filenames_and_filetypes_in_Video_and_Document_material(userID)
    print('Returned user content: ', contentJSON)
    session["userContent"] = contentJSON
    if "userContent" in session : 
        if contentJSON != None :
            print('\n==============================USER CONTENT================================\n',
                f'\t\t\tName: {session["UserName"]}\n',
                 f'CONTENT: \n{contentJSON}',
                  '\n================================USER CONTENT==============================\n')
            
            return jsonify(contentJSON), 200
        
        else : 
            print('\n==============================USER CONTENT================================\n',
                 f'\t\tName: {session["UserName"]}\n',
                 f'\t\tNO USER CONTENT FOUND',
                  '\n================================USER CONTENT==============================\n')
            
            return jsonify({'status': 'No user content'}), 404
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'Missing URL parameter'}), 400

    response = requests.get(url)
    if response.status_code != 200:
        return jsonify({'error': 'Failed to fetch URL'}), response.status_code

    return response.content, 200, {'Content-Type': response.headers['Content-Type']}

@app.route('/load-document-content', methods = ['POST'])
def load_document_content() : 
    if "UserID" in session : 
        userID = session['UserID']
        data = request.json
        fileName = data.get('fileName')
        print('\n===================================== JS-FILE =====================================\n',
              '\t\t\tfilename from JS: ', userID,
              '\t\t\tfilename from JS: ', fileName,
              '\n===================================== JS-FILE =====================================\n')

        from backend.Classes.Document_Controller import DocumentProcessedController as Document_Fetcher
        documentLink, Summary, Flashcards, MCQ_E, MCQ_M, MCQ_H = Document_Fetcher.fetch_document_content(userID, fileName)

        print(  '\n================================= DOCUMENT-CONTENT =================================\n',
                '\nDocument name: \n', fileName,
                '\nLink: \n', documentLink,
                '\nSummary: \n', Summary, 
                '\nFlashcards: \n', Flashcards, 
                '\n================================= DOCUMENT-CONTENT =================================\n')
        
        return jsonify({
                        'method': 'POST',
                        'headers': {
                            'Content-Type': 'application/json',
                        },
                        'data': {
                            'fileName':     fileName,       # String
                            'documentLink': documentLink,   # Fetch Link
                            'summary':      Summary,        # Fetch JSON
                            'flashcards':   Flashcards,     # Fetch JSON
                            'MCQ_E':        MCQ_E,          # Fetch JSON
                            'MCQ_M':        MCQ_M,          # Fetch JSON
                            'MCQ_H':        MCQ_H           # Fetch JSON
                        }
                    })
    else : 
        return redirect(url_for(login))

@app.route('/load-video-content', methods = ['POST'])
@cross_origin(origins="*")
def load_video_content() : 
    if "UserID" in session : 
        userID = session['UserID']
        data = request.json
        fileName = data.get('fileName')
        print('\n===================================== JS-FILE =====================================\n',
              '\t\t\tfilename from JS: ', userID,
              '\t\t\tfilename from JS: ', fileName,
              '\n===================================== JS-FILE =====================================\n')

        from backend.Classes.VideoProcessed_Controller import Video_Processed_Controller as Video_Fetcher
        videoLink, audioLink, summary, chapters, flashcards, MCQ_E, MCQ_M, MCQ_H, Transcript = Video_Fetcher.fetch_video_content(userID, fileName)
        
        print(  '\n================================== VIDEO-CONTENT ==================================\n',
                'Video name: ', fileName,
                '\n\nLink: \n', videoLink, 
                '\n\nSummary: \n', summary, 
                '\n\nChapters: \n', chapters, 
                '\n\nFlashcards: \n', flashcards, 
                '\n\nTranscript: \n', Transcript,
                '\n================================== VIDEO-CONTENT ==================================\n')

        return jsonify({
                    'method': 'POST',
                    'headers': {
                        'Content-Type': 'application/json',
                    },
                    'data': {
                        'fileName':     fileName,   # String
                        'videoLink':    videoLink,  # Fetch Link
                        'audioLink':    audioLink,  # Fetch Link
                        'summary':      summary,    # Fetch JSON
                        'chapters':     chapters,   # Fetch JSON
                        'flashcards':   flashcards, # Fetch JSON
                        'MCQ_E':        MCQ_E,      # Fetch JSON
                        'MCQ_M':        MCQ_M,      # Fetch JSON
                        'MCQ_H':        MCQ_H,      # Fetch JSON
                        'Transcript':   Transcript  # Fetch JSON
                    }
                })
    else : 
        return redirect(url_for(login))

@app.route('/save-content-notes', methods = ['POST'])
def save_content_notes() : 
    userID = session['UserID']
    data = request.json
    fileName = data.get('fileName')
    fileType = data.get('fileType')
    notes = data.get('notesArray')

    print('================================= SAVING NOTES =========================================\n')
    print('=== fileName recieved:\n', fileName)
    print('=== fileType recieved:\n', fileType)
    print('=== Notes recieved:\n', notes)
    
    from backend.Classes.Notes_Controller import Notes_Controller
    Notes_Controller.Add_Notes_tofirestore(notes, userID, fileType, fileName)

    return jsonify({"status": "success"}), 200


@app.route('/load-content-notes', methods = ['POST'])
def load_content_notes() : 
    userID = session['UserID']
    data = request.json
    fileName = data.get('fileName')
    fileType = data.get('fileType')

    print('================================= LOADING NOTES =========================================\n')
    print('=== fileName recieved:\n', fileName)
    print('=== fileType recieved:\n', fileType)
    print('\nFetching notes from Firestore...\n')
    
    from backend.Classes.Notes_Controller import Notes_Controller
    fetchedNotes = Notes_Controller.fetch_notes_if_exist(userID, fileType, fileName)

    print('=== Recieved from Firestore:\n', fetchedNotes)

    if (fetchedNotes != None) : 
        return jsonify({
                        'method': 'POST',
                        'headers': {
                            'Content-Type': 'application/json',
                        },
                        'data': {'fetchedNotes': fetchedNotes}
                    })
    else : 
        return jsonify({"status": "No notes found"}), 404

# @app.route('/proxy', methods=['GET'])
# @cross_origin(origins="*")
# def proxy():

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
        
        print('\tDecrypted: Name:', fName, ', Email:', signupEmail, ', Password:', signupPW, 
              '\n=============================_END SIGN UP_=============================\n')
        if status == True :
            socketio.emit('update', {'message': 'Signup Success'}, to=socketID)
            # print(f"Signed up: {UserController.decrypt_string(fName)} \nWith Email: {UserController.decrypt_string(signupEmail)}\n\nLogging in\n\n")

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
        session["Email"] = loginEmail
        print("email=======================",session["Email"])

        return jsonify({'message': 'Login Success'})
    else :
        print(f"Failed Login attempt")
        return jsonify({'message': 'Failed Login attempt'}), 406

@app.route('/process-logout', methods = ['POST']) 
def process_logout():
    session.pop('UserID')
    session.pop('UserName')

@app.route('/get_password', methods=['POST'])
def get_password():
    data = request.get_json()
    email = data.get('email')
    if not email:
        return jsonify({'success': False, 'message': 'Email is required.'}), 400
    
    password = UserController.get_password_by_email(email)
    if password:
        return jsonify({'success': True, 'password': password}), 200
    else:
        return jsonify({'success': False, 'message': 'Email not found.'}), 404
    
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


# MODIFIED UPLOAD FUNCTION HANDLES ALL VIDEO AND TEXT-BASED FILES (UPLOADING AND PROCESSING) ===============
@app.route('/upload-file', methods=['POST'])
async def upload_file():
    file = request.files.get('file')
    session['uploadedFileType'] = request.form.get('FileType')
    print('Got File Type:', session['uploadedFileType'])
    fileType = session.get('uploadedFileType', '').lower()
    userID = session.get('UserID')
    
    if file:
        socketID = request.form.get('socketID')
        print('\nClient\'s Socket ID: ', socketID)

        if fileType == 'document':
            from backend.Classes.Document_Controller import DocumentProcessedController
            
            # Save the file to the specified directory (documents)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'text-based', file.filename)
            file.save(filepath)
            
            # Send an initiation update message to the client
            socketio.emit('update', {'message': f'Processing {file.filename}...'}, to=socketID)

            # Call DocumentProcessedController to upload the document
            file_name, material_id = await DocumentProcessedController.upload_document(filepath, userID)
            
            # Send a completion update message to the client
            socketio.emit('update', {'message': 'Processing completed'}, to=socketID)

            print('\n!!! :) !!! Files generated and uploaded to Firebase. !!! :) !!!\n',
                  'Firebase File name: ', file_name,
                  'Firebase doc ID: ', material_id)

            return jsonify({'message': f'Document {file_name} uploaded successfully. ~DIDO', 'filename': file_name}), 200
        
        elif fileType == 'video':
            from backend.Classes.VideoProcessed_Controller import Video_Processed_Controller

            # Save the file to the specified directory (videos)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'video-based', file.filename)
            file.save(filepath)       

            if request.form.get('audiocut') == 'True' :
                print(f'Starting processing on video (Audiocut) {file.filename}\n')
            
                # Send an initiation update message to the client
                socketio.emit('update', {'message': f'Processing {file.filename}...'}, to=socketID)

                # Call VideoProcessedController to upload the video
                processed_video = Video_Processed_Controller.upload_video_cut(filepath, userID)
            
            elif request.form.get('audiocut') == 'False' :
                print(f'Starting processing on video (NON Audiocut) {file.filename}\n')
            
                # Send an initiation update message to the client
                socketio.emit('update', {'message': f'Processing {file.filename}...'}, to=socketID)

                # Call VideoProcessedController to upload the video
                processed_video = Video_Processed_Controller.upload_video(filepath, userID)

            # Send a completion update message to the client
            socketio.emit('update', {'message': 'Processing completed'}, to=socketID)

            print('\n!!! :) !!! Files generated and uploaded to Firebase. !!! :) !!!\n',
                  'Firebase File name: ', processed_video)

            return jsonify({'message': f'Video: {file.filename} processed. ~DIDO', 'filename': processed_video}), 200
        else:
            return jsonify({'message': 'Invalid file type. ~DIDO'}), 400
    
    else:
        return jsonify({'message': 'No file detected ~DIDO'}), 406

@app.route('/filename', methods=['POST'])
def receive_filename():
    data = request.get_json()
    filename = data.get('filename')
    if filename:
        # Do something with the filename
        return jsonify({'message': 'Filename received', 'filename': filename}), 200
    return jsonify({'message': 'No filename received'}), 400


# PDF CHAT ========================================================================
@app.route('/upload', methods=['POST'])
def upload():
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
    text_file = file + ".txt"

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
@app.route('/delete_account', methods=['POST'])
def delete_account():
    user_id = session.get('UserID')
    email=session.get("Email")
    print(email)
    print(f"Deleting account for user ID {user_id}")
    if not user_id:
        return jsonify({'success': False, 'error': 'User not authenticated'}), 401

    try:
        # Call the UserController to delete the user by ID
        UserController.deleteUser(user_id,email)

        # Clear the session after deleting the account
        session.clear()
        return jsonify({'success': True}), 200

    except Exception as e:
        print(f"Error deleting account for user ID {user_id}: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/chatwithpdf')
def chat_with_pdf():
    return render_template('main_loggedin/chatwithpdf.html')

@app.route('/mcq')
def mcq():
    return render_template('main_loggedin/generate_mcqs.html')

@app.route('/leaderboard')
def leaderboard():
    return render_template('main_loggedin/leaderboard.html')

if __name__ == '__main__':
    # socketio.run(app, host='0.0.0.0', debug=True)
    socketio.run(app, debug=True)