import cv2
import pytesseract
import numpy as np
import json

import TextSummmariser
import NLP
  
api_key = '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'
# Configuration
pytesseract.pytesseract.tesseract_cmd = r'C:/Program Files/Tesseract-OCR/tesseract.exe'


def format_summary_to_json(summary_text):
    # Create a dictionary with the summary
    summary_dict = {
        "summary": summary_text
    }
    
    # Convert the dictionary to a JSON-formatted string
    json_output = json.dumps(summary_dict, indent=4)
    
    return json_output

# Simulated output from `extract_text_from_video`
summarized_text = "The video discusses the recent advancements in artificial intelligence and machine learning, highlighting the impact on various industries such as healthcare, automotive, and finance. It emphasizes the role of AI in enhancing efficiency, personalization, and decision-making processes."

# Use the function to format the summarized text into JSON
json_formatted_summary = format_summary_to_json(summarized_text)

print(json_formatted_summary)

def preprocess_image(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    # Binarize the image using adaptive thresholding
    thresholded = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)
    # Dilate to combine characters into solid blobs
    kernel = np.ones((2,2), np.uint8)
    dilated = cv2.dilate(thresholded, kernel, iterations=1)
    return dilated

def is_similar(new_text, old_text, threshold):
    # Simple similarity check (can be replaced with more complex logic)
    return new_text.strip() == old_text.strip()


#def extract_text_from_video(video_path, output_file_path ,frame_skip = 25):
def extract_text_from_video(video_path, frame_skip = 25):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    accumulated_text = ""
    previous_text = ""
    frame_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_skip == 0:
            preprocessed_frame = preprocess_image(frame)
            text = pytesseract.image_to_string(preprocessed_frame, lang='eng', config='--oem 1 --psm 6')
            filtered_text = NLP.filter_text(text)

            if not is_similar(filtered_text, previous_text, 0.9):  # Adjusted threshold parameter
                accumulated_text += filtered_text + '\n\n'  # Add extra newline for readability
                previous_text = filtered_text

        frame_count += 1
        
    cap.release()

    accumulated_text=TextSummmariser.get_Long_summary_from_gpt3(accumulated_text,api_key)
    #with open(output_file_path, 'w', encoding='utf-8') as file:
       # file.write(TextSummmariser.get_Long_summary_from_gpt3(accumulated_text,api_key))
    return accumulated_text