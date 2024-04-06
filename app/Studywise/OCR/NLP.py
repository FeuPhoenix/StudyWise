import spacy
import nltk
import re
from nltk.tokenize import sent_tokenize
from nltk.corpus import words as nltk_words

# Load the spaCy model and nltk words
nlp = spacy.load("en_core_web_sm")
nltk.download('punkt')
nltk.download('words')
english_words = set(nltk_words.words())

def is_coherent_sentence(text):
    # Checks if the sentence is coherent by looking for a verb
    doc = nlp(text)
    return any(token.pos_ == "VERB" for token in doc)

def is_mostly_alphabetic(text):
    # Check if the majority of characters in the text are alphabetic
    alphabetic_chars = [char for char in text if char.isalpha()]
    return len(alphabetic_chars) / len(text) > 0.6 

def contains_valid_words(text):
    # Check if the text contains a significant amount of valid English words
    words_in_text = text.split()
    valid_words = [word for word in words_in_text if word.lower() in english_words]
    return len(valid_words) / len(words_in_text) > 0.5  

def filter_text(text):
    # Filters out non-sentences, incoherent sentences, and non-alphabetic segments
    filtered_text = ""
    sentences = sent_tokenize(text)
    for sentence in sentences:
        if (is_coherent_sentence(sentence) and
            is_mostly_alphabetic(sentence) and contains_valid_words(sentence)):
            filtered_text += sentence + " "
    return filtered_text

