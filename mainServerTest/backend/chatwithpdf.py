import os
from flask import Flask, request, jsonify, render_template, session, send_from_directory, url_for
import openai
import fitz  # PyMuPDF
from dotenv import load_dotenv
from io import BytesIO
from werkzeug.utils import secure_filename

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_APP_SECRET_KEY', 'a_default_secret_key')
UPLOAD_FOLDER = 'C:\\Users\\AMR\\Desktop\\pro\\StudyWise\\chat_with_pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

openai.api_key = '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'

# Route to render the frontend HTML
@app.route('/')
def home():
    return render_template('chatwithpdf.html')

# Route to handle file upload and text extraction from PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        # Secure the filename
        filename = secure_filename(file.filename)
        # Save the file to the specified directory
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        # Generate a URL to access the file
        file_url = url_for('uploaded_file', filename=filename, _external=True)
        return jsonify({'status': 'success', 'fileUrl': file_url})
    else:
        return jsonify({'error': 'No file uploaded'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to handle chat interaction
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json['message']
    pdf_text = session.get('pdf_text', '')  # Retrieve the stored PDF text

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

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}

def extract_text_from_pdf(file):
    # Read the file stream into a BytesIO object
    file_stream = BytesIO(file.read())
    with fitz.open(stream=file_stream, filetype="pdf") as doc:
        text = ''
        for page in doc:
            text += page.get_text()
    return text

if __name__ == '__main__':
    app.run(debug=True)