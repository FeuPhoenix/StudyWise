# import requests
# from FirestoreDB import FirestoreDB


# def fetch_json_from_url(url):
#     try:
#         # Make a GET request to download the JSON file
#         response = requests.get(url)
#         response.raise_for_status()  # Raise an exception for any HTTP error status codes
        
#         # Load the JSON data
#         data = response.json()
#         return data
#     except requests.exceptions.RequestException as e:
#         print("Error:", e)
#         return None

# # URL of the JSON file
# url = "https://storage.googleapis.com/studywise-dba07.appspot.com/user/62a9c20699654da5b14cca9d21cd8ef6/Uploaded%20Materials/Inflation%20Explained%20in%20One%20Minute/chapters.json?Expires=4868440853&GoogleAccessId=firebase-adminsdk-56dni%40studywise-dba07.iam.gserviceaccount.com&Signature=P9hjrJXBYTH6M3%2B632apIPbQ3r4dhprAgvf6cbdnlDDNkv4EDa7j7r6NU05OWxHfuhaArefXvIMfiEW33FqMYNCCwN%2BRVpI6erxZqoKdIxMJ%2Fyg4RCZA12GrPh4jypKq6nGenIR0TPPP9x7S9NsP3mzOqzFKF72DeijEsPMU8n0E7uxxrXSvk%2BfXt0X1vjVvL51gLeTXx%2FEh8qcJRyCR06SX8dzS2dTqTRaac%2BxPt%2BP9uSQFal4cW4xftdW0hjSvqVCcNqNSPJcxOQfv3Pqt5feuuPSViTuRe2Pl9S7Kpm0bhgoiBupIccvwXgiCRCkoVY2ZX0k9yRf3TgJ%2BzRuVmg%3D%3D"

# # Fetch JSON data from the URL
# json_data = fetch_json_from_url(url)

# if json_data:
#     print("JSON data:")
#     print(json_data)
# else:
#     print("Failed to fetch JSON data from the URL.")import pytesseract
import fitz  # PyMuPDF

# # Path to your PDF file
# pdf_path = "C:/Users/Abdelrahman/Downloads/محاضرة د.محمود البحيري ٢ (1).pdf"
# # Open the PDF file
# doc = fitz.open(pdf_path)

# # Iterate through pages and extract text
# for page_num in range(len(doc)):
#     page = doc.load_page(page_num)
#     text = page.get_text()
#     if text:
#         print(text)
# import easyocr
# reader = easyocr.Reader(['ch_sim','en']) # this needs to run only once to load the model into memory
# result = reader.readtext("D:/COLLEGE/StudyWise/mainServerTest/assets/output_files/Images/test/test_page_10_img_2.png",detail = 0)
# print(result)