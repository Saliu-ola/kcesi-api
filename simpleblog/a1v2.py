import string
import math
import pandas as pd

pd.set_option('display.max_rows', 500)
import numpy as np
import nltk

nltk.download('stopwords')
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


existingTexts = ''' Cells are the fundamental units of life in biology. They are the building blocks of all living organisms, ranging from simple single-celled organisms like bacteria to complex multicellular organisms like humans. Each cell is enclosed by a membrane that regulates the passage of substances in and out of the cell. Within the cell, various organelles carry out specific functions, such as energy production in the mitochondria, protein synthesis in the endoplasmic reticulum, and genetic information storage in the nucleus. Cells can be categorized into two main types: prokaryotic cells, which lack a nucleus and other membrane-bound organelles, and eukaryotic cells, which have a nucleus and membrane-bound organelles. The study of cells, known as cell biology or cytology, is crucial for understanding the processes of life, including growth, development, reproduction, and disease. Through advances in technology such as microscopy and molecular biology techniques, scientists continue to unravel the complexities of cells and their functions, paving the way for advancements in medicine, biotechnology, and other fields. '''

newTexts = ''' Cells are the fundamental units of life, serving as the building blocks of all living organisms. These microscopic structures exhibit remarkable diversity in size, shape, and function, yet share common features such as a plasma membrane, cytoplasm, and genetic material. Within cells, intricate biochemical processes govern essential functions like metabolism, growth, and reproduction. Specialized organelles, including the nucleus, mitochondria, and endoplasmic reticulum, facilitate these activities with precision and efficiency. Cellular communication and coordination enable multicellular organisms to maintain homeostasis and respond to environmental cues. Understanding the intricacies of cellular biology is crucial for unraveling the mysteries of life and advancing scientific knowledge. '''
existingTexts = [existingTexts]
newTexts = [newTexts]
stop_words = stopwords.words('english')
print(stop_words)


def stop_word_removal(text, stop_word_corpus, punct_str):
    clean_text = ' '.join(
        [word.lower() for word in text.split() if word.lower() not in stop_word_corpus]
    ).replace('\n', ' ')
    return clean_text.translate(str.maketrans('', '', punct_str))


existingTexts_cleaned = [
    stop_word_removal(headline, stop_words, string.punctuation) for headline in existingTexts
]

newTexts_cleaned = [
    stop_word_removal(headline, stop_words, string.punctuation) for headline in newTexts
]


newTextsCleanedString = ''.join(newTexts_cleaned)
newTextsCleanedList = [x for x in newTextsCleanedString.split(' ')]
uniqueWrdsNewTextsCleanedList = np.unique(np.array(newTextsCleanedList))
existingTextscleanedString = ''.join(existingTexts_cleaned)
existingTextsCleanedList = [x for x in existingTextscleanedString.split(' ')]
uniqueWrdsExistingTextsCleanedList = np.unique(np.array(existingTextsCleanedList))


lemmatizer = WordNetLemmatizer()

lemmatizedExistingWords = [
    lemmatizer.lemmatize(word) for word in uniqueWrdsExistingTextsCleanedList
]
lemmatizedNewWords = [lemmatizer.lemmatize(word) for word in uniqueWrdsNewTextsCleanedList]


# B. LEMMATIZATION WITH: POS = ADJECTIVE
lemmatizedExistingWordsAdj = [
    lemmatizer.lemmatize(word, pos="a") for word in lemmatizedExistingWords
]
lemmatizedNewWordsAdj = [lemmatizer.lemmatize(word, pos="a") for word in lemmatizedNewWords]

uniqueLemmatizedExistingWordsAdj = np.unique(np.array(lemmatizedExistingWordsAdj))
uniqueLemmatizedNewWordsAdj = np.unique(np.array(lemmatizedNewWordsAdj))

# C. LEMMATIZATION WITH: POS = VERB
lemmatizedExistingWords = [
    lemmatizer.lemmatize(word, pos="v") for word in lemmatizedExistingWordsAdj
]
lemmatizedNewWords = [lemmatizer.lemmatize(word, pos="v") for word in lemmatizedNewWordsAdj]

uniqueLemmatizedExistingWords = np.unique(np.array(lemmatizedExistingWords))
uniqueLemmatizedNewWords = np.unique(np.array(lemmatizedNewWords))

common = list(x for x in uniqueLemmatizedNewWords if x in uniqueLemmatizedExistingWords)

originalCount = len(uniqueLemmatizedNewWords)
commonCount = len(common)


rp = relevancePercent = round(((commonCount / originalCount) * 100), 2)
rating = ''


if rp > 59:
    rating = 'Excellent'
elif rp > 49:
    rating = 'Very Good'
elif rp > 29:
    rating = 'Good'
elif rp > 14:
    rating = 'Fair'
elif rp > 10:
    rating = 'Bad'
else:
    rating = 'Very Bad'


print("Grade: ", relevancePercent, '%', '\n')
print("Rating: ", rating)
