import json
import os
import re
import nltk
import pdfplumber
import numpy as np
import pandas as pd
import nltk
import re
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from gensim.models import Word2Vec
from scipy import spatial
import networkx as nx
from summarizer import Summarizer
nltk.download('punkt')
# nltk.download('stopwords')
def read_and_tokenize(file_path):
    with open(file_path, 'r') as file:
        text = file.read()
        sentences = sent_tokenize(text)
    return sentences

# Function to save sentences as bullet points in a JSON file
def save_as_json(sentences, json_file_path):
    bullet_points = [f"- {sentence}" for sentence in sentences]
    with open(json_file_path, 'w') as json_file:
        json.dump(bullet_points, json_file, indent=4, ensure_ascii=False)

# File paths


# Read and tokenize text


def delete_page_breaks(file_path):
    # Read the content of the file
    with open(file_path, 'r',encoding='utf-8') as file:
        content = file.read()

    # Remove "--- Page Break ---" occurrences
    cleaned_content = content.replace("--- Page Break ---", "")

    # Write the cleaned content back to the file
    with open(file_path, 'w') as file:
        file.write(cleaned_content)

def extract_text_from_pdf_plumber(pdf_path, txt_file_path):
    # Open the PDF file
    if not os.path.exists(txt_file_path):
     print("does not exists")
        # Create the directory, including any necessary parent directories
     with pdfplumber.open(pdf_path) as pdf:
        # Open the text file in write mode
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            # Iterate through each page in the PDF
            for page in pdf.pages:
                # Extract text from the page
                text = page.extract_text()
                
                # Write the text to the text file, if text was found
                if text:
                    txt_file.write(text)
                    
                    # Optionally, add a page break in the text file
                    txt_file.write('\n--- Page Break ---\n\n')
    
    print(f"Text extracted and saved to {txt_file_path}")
def clean_text(text):
    # Define the allowed characters, you might want to adjust this pattern
    # This pattern keeps letters, numbers, basic punctuation, and newlines
    allowed_pattern = r"[^a-zA-Z\s,.;:'\"!?()-]"
    
    # Replace characters not matching the pattern with an empty string
    cleaned_text = re.sub(allowed_pattern, '', text)
    
    # Additional cleaning steps can be added here (e.g., removing extra spaces, handling special cases)
    
    return cleaned_text
def read_text_file(file_path):
    with open(file_path, 'r',encoding='utf-8') as file:
        return file.read()


def main():
#     text=read_text_file("Summaries/full_transcript.txt")
    
#     text=clean_text(text)
    
#     sentences=sent_tokenize(text)
#     sentences_clean=[re.sub(r'[^\w\s]','',sentence.lower()) for sentence in sentences]
#     #print("11111",sentences_clean)
#     stop_words = stopwords.words('english')
#     #print("22222",stop_words)
#     sentence_tokens=[[words for words in sentence.split(' ') if words not in stop_words] for sentence in sentences_clean]
#     w2v=Word2Vec(sentence_tokens,vector_size=1,min_count=1,epochs=1000)
#     sentence_embeddings = [[w2v.wv[word][0] for word in words if word in w2v.wv] for words in sentence_tokens]
#     max_len=max([len(tokens) for tokens in sentence_tokens])
#     sentence_embeddings=[np.pad(embedding,(0,max_len-len(embedding)),'constant') for embedding in sentence_embeddings]
#     similarity_matrix = np.zeros([len(sentence_tokens), len(sentence_tokens)])
#     for i,row_embedding in enumerate(sentence_embeddings):
#         for j,column_embedding in enumerate(sentence_embeddings):
#             similarity_matrix[i][j]=1-spatial.distance.cosine(row_embedding,column_embedding)
#     nx_graph = nx.from_numpy_array(similarity_matrix)
#     scores = nx.pagerank(nx_graph)
#     top_sentence={sentence:scores[index] for index,sentence in enumerate(sentences)}
#     top=dict(sorted(top_sentence.items(), key=lambda x: x[1], reverse=True)[:int(0.2*len(sentences))])
#     for sent in sentences:
#      if sent in top.keys():
#         print("-",sent)
# if __name__ == "__main__":
#   main()

#from summarizer import Summarizer
    model = Summarizer()

    text=read_text_file("Summaries/full_transcript.txt")
        
    text=clean_text(text)


    # Use the summarizer on your text
    #summary = model(text, max_length=600, min_length=30)

    model = Summarizer()
    result = model(text,ratio=0.2)
    with open("test2.txt", 'w') as file:
            file.write(result)
            delete_page_breaks("test2.txt")
    text_file_path = 'test2.txt'  # Update with your text file path
    json_file_path = 'sentences.json'  # Desired JSON file path 
    sentences = read_and_tokenize(text_file_path)
    save_as_json(sentences, json_file_path)


if __name__ == "__main__":
  main()