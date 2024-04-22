import string
import os
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import google.generativeai as genai
import pandas as pd
import numpy as np

pd.set_option('display.max_rows', 500)

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


def clean_data_and_lemmatize(input_texts):
    if isinstance(input_texts, str):
        input_texts = [input_texts]  # Convert single string to list

    stop_words = stopwords.words('english')
    punct_str = string.punctuation

    existing_texts_cleaned = [
        stop_word_removal(text, stop_words, punct_str) for text in input_texts
    ]

    existing_texts_cleaned_string = ' '.join(existing_texts_cleaned)
    existing_texts_cleaned_list = [x for x in existing_texts_cleaned_string.split(' ')]

    unique_words_existing_texts_cleaned_list = np.unique(np.array(existing_texts_cleaned_list))

    lemmatized_existing_words = [
        lemmatizer.lemmatize(word) for word in unique_words_existing_texts_cleaned_list
    ]

    return lemmatized_existing_words


def fetch_related_terms(description):
    prompt = f"description: '{description}'. Fetch at least 3000 unique related terms for a given description, and return them as cleaned and lemmatized words as a list.should be in fomat [term,term,term]"
    response = model.generate_content(prompt)
    result = response.text
    related_terms_list = result.split(',')
    if not related_terms_list:
        print("No related terms were found.")
        return []
    return related_terms_list

def check_percentage_relevance_of_uncommon_words(uncommon_words,description):
    prompt = f" for description: '{description}', what is the percentage relevance or relation of the words '{uncommon_words}',return only the percentage digits, e.g 24.55 in 2d.p,if the words are not relevant return 0.00 "
    response = model.generate_content(prompt)
    result = response.text
    return result


def get_cleaned_and_lematized_terms(description):
    related_terms = fetch_related_terms(description)
    return clean_data_and_lemmatize(related_terms)


def get_relevance_percentage_for_new_texts_and_its_uncommon_words(new_text, existing_text):

    lemmatized_and_clean_new_text = clean_data_and_lemmatize(new_text.split(','))
    lemmatized_and_clean_existing_text = clean_data_and_lemmatize(existing_text)

    common = list(
        x for x in lemmatized_and_clean_new_text if x in lemmatized_and_clean_existing_text
    )
    uncommon = list(
        x for x in lemmatized_and_clean_new_text if x not in lemmatized_and_clean_existing_text
    )

    new_text_count = len(lemmatized_and_clean_new_text)
    common_count = len(common)

    relevance_percentage = round(((common_count / new_text_count) * 100), 2)
    return relevance_percentage, uncommon


def get_percentage_relevancy(new_text, existing_text):
    return get_relevance_percentage_for_new_texts_and_its_uncommon_words(new_text, existing_text)[0]

def get_foreign_terms(new_text, existing_text):
    return get_relevance_percentage_for_new_texts_and_its_uncommon_words(new_text, existing_text)[1]





# uncommon_words = get_relevance_percentage_for_new_texts_and_its_uncommon_words(
#     new_text="sometimes we have movement,reproduction,respiration as characterisitics of adaption a living thing",
#     existing_text=["nutriton", "respiration", "movement", "reproduction", "death", "growth"],
# )[1]

# print(check_percentage_relevance_of_uncommon_words(uncommon_words,'football is a game of chance'))
