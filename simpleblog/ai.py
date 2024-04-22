import string
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import google.generativeai as genai
import pandas as pd

pd.set_option('display.max_rows', 500)
import numpy as np

# Download necessary NLTK data
nltk.download('wordnet')
nltk.download('stopwords')

# Configure Google Generative AI
GOOGLE_GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

# Initialize the lemmatizer
lemmatizer = WordNetLemmatizer()


def stop_word_removal(text, stop_word_corpus, punct_str):
    clean_text = ' '.join(
        [word.lower() for word in text.split() if word.lower() not in stop_word_corpus]
    ).replace('\n', ' ')
    return clean_text.translate(str.maketrans('', '', punct_str))


def clean_data_and_lemmatize(input_text):
    existing_texts = [input_text]

    stop_words = stopwords.words('english')

    existing_texts_cleaned = [
        stop_word_removal(headline, stop_words, string.punctuation) for headline in existing_texts
    ]

    # Convert the cleaned texts, which is in the form of a list, into a single string
    existing_texts_cleaned_string = ''.join(existing_texts_cleaned)

    # Split new_texts_cleaned by space to form a list of words
    existing_texts_cleaned_list = [x for x in existing_texts_cleaned_string.split(' ')]

    # Find the unique values of new_texts_cleaned and existing_texts_cleaned
    unique_words_existing_texts_cleaned_list = np.unique(np.array(existing_texts_cleaned_list))

    # Implementing lemmatization
    lemmatized_existing_words = [
        lemmatizer.lemmatize(word) for word in unique_words_existing_texts_cleaned_list
    ]

    # Lemmatization with: POS = ADJECTIVE
    lemmatized_existing_words_adj = [
        lemmatizer.lemmatize(word, pos="a") for word in lemmatized_existing_words
    ]

    # Lemmatization with: POS = VERB
    lemmatized_existing_words = [
        lemmatizer.lemmatize(word, pos="v") for word in lemmatized_existing_words_adj
    ]

    unique_lemmatized_existing_words = np.unique(np.array(lemmatized_existing_words))

    return unique_lemmatized_existing_words


def fetch_related_terms(description):
    """Fetch related terms for a given description, and return them as cleaned, lemmatized words with stopwords."""
    prompt = f"description: '{description}'. Fetch at least 3000 unique related terms for a given description, and return them as cleaned and lemmatized words as a list.should be in fomat [term,term,term]"

    response = model.generate_content(prompt)
    result = response.text

    # Assuming the response is a list of terms separated by commas, split the string to get a list
    related_terms_list = result.split(',')

    # Validate that the list is not empty
    if not related_terms_list:
        print("No related terms were found.")
        return []

    return related_terms_list


def get_cleaned_and_lematized_terms(description):
    return clean_data_and_lemmatize(fetch_related_terms(description))


print(get_cleaned_and_lematized_terms('reproduction in human'))
