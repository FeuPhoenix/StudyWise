import os
from flask import Flask, request, jsonify, render_template, session, send_from_directory, url_for
import openai
import fitz  # PyMuPDF
from io import BytesIO
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.getenv('FLASK_APP_SECRET_KEY', 'a_default_secret_key')
UPLOAD_FOLDER = 'C:\\Users\\AMR\\Desktop\\pro\\StudyWise\\chat_with_pdf'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

openai.api_key = os.getenv('OPENAI_API_KEY')

# Route to render the frontend HTML
@app.route('/')
def home():
    return render_template('chatwithpdf.html')

# Route to handle file upload and text extraction from PDF
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files.get('file')
    if not file:
        return jsonify({'error': 'No file uploaded'}), 400

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text from the uploaded PDF
        try:
            pdf_text = extract_text_from_pdf(filepath)
            session['pdf_text'] = pdf_text  # Store extracted text in session
        except Exception as e:
            return jsonify({'error': f'Failed to extract text from PDF: {e}'}), 500

        file_url = url_for('uploaded_file', filename=filename, _external=True)
        return jsonify({'status': 'success', 'fileUrl': file_url})
    else:
        return jsonify({'error': 'Invalid file type'}), 400

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route to handle chat interaction
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message')
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400

    pdf_text = session.get('pdf_text', '')
    if not pdf_text:
        return jsonify({'error': 'No PDF text available. Please upload a PDF first.'}), 400

    try:
        conversation_history = [
            {"role": "system", "content": pdf_text},
            {"role": "user", "content": user_input}
        ]
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=conversation_history
        )
        response_text = response.choices[0].message['content']
        return jsonify({'response': response_text})
    except Exception as e:
        return jsonify({'error': f'Failed to get response from chatbot: {e}'}), 500


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'pdf'}

def extract_text_from_pdf(filepath):
    try:
        text = ''
        with fitz.open(filepath) as doc:
            for page in doc:
                text += page.get_text()
        return text
    except Exception as e:
        raise Exception(f'Error extracting text: {e}')


if __name__ == '__main__':
    app.run(debug=True)