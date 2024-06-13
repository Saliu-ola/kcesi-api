#TF-IDF-BASED LIBRARY


#pip install pypdf
from pypdf import PdfReader
import string
import math
import pandas as pd
import numpy as np
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer

# Use pandas to increase the number of rows to display on the tf-idf table
pd.set_option('display.max_rows', 500)

# Load the spacy model (comment later if you don't use)
import spacy
nlp = spacy.load('en_core_web_sm')

# Lemmatization with NLTK
from nltk.stem import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize

# Download necessary NLTK data files
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')




pdfs_Dataset = []


reader =PdfReader('C:/Users/USER/Downloads/random_paragraph.pdf')
page = reader.pages[0]
fullfile1Text = " "
for i in range(len(reader.pages)):
  page = reader.pages[i]
  file1Text = page.extract_text()
  fullfile1Text += file1Text

pdfs_Dataset.append(fullfile1Text)


reader =PdfReader('C:/Users/USER/Downloads/two_paragraphs.pdf')
page = reader.pages[0]
fullfile2Text = " "
for i in range(len(reader.pages)):
  page = reader.pages[i]
  file2Text = page.extract_text()
  fullfile2Text += file2Text

pdfs_Dataset.append(fullfile2Text)



# Do the lemmatization using spaCy
# Great and short, but can make some rare errors which can be ignored depending on the use case


counterLemma = 0
pdfs_Dataset_Lemmatized = []

for i in pdfs_Dataset:
  fileContentWords = pdfs_Dataset[counterLemma]
  doc = nlp(fileContentWords)

  # Lemmatize each token in the sentence
  lemmatizedWordsList = [token.lemma_ for token in doc]
  lemmatizedWordsSentence = ' '.join(lemmatizedWordsList)
  pdfs_Dataset_Lemmatized.append(lemmatizedWordsSentence)
  counterLemma +=1

# print(pdfs_Dataset, '\n')
# print(pdfs_Dataset_Lemmatized)



stop_words = stopwords.words('english')

def stop_word_removal(text, stop_word_corpus, punct_str):
    clean_text = ' '.join([word.lower() for word in text.split() if word.lower()
                 not in stop_word_corpus]).replace('\n',' ')
    return clean_text.translate(str.maketrans('', '', punct_str))


# Clean up the dataset using the stop_word_removal function (pass it to the function, element by element)
pdfs_Dataset_cleaned = [stop_word_removal(fileContent,stop_words,string.punctuation)
                for fileContent in pdfs_Dataset_Lemmatized]



# Extract words that contain only letters
# Loop through the words in each element of the pdfs_Dataset_cleaned list
# Save the result in pdfs_Dataset_Only_Letters list

counter = 0
pdfs_Dataset_Only_Letters = []

for i in pdfs_Dataset_cleaned:
  fileContentWordList = pdfs_Dataset_cleaned[counter].split()          # Split a file content to a list of words
  onlyLetterWords = [i for i in fileContentWordList if i.isalpha()]    # Extract only the words that contain only letters by checking each word in the file content
  onlyLetterWordsSentence = ' '.join(onlyLetterWords)                  # Join the words that contain only letters back to a sentence
  pdfs_Dataset_Only_Letters.append(onlyLetterWordsSentence)            # Add the sentence to the list: pdfs_Dataset_Only_Letters
  counter +=1





# For the sake of convenience, let variable 'vectorizer' equal the TfidfVectorizer()
# The TfidfVectorizer() tool imported from scikit-learn library will be used to transform the texts into a vector (a sparse matrix)
# It the the vector type that will be used to create the Pandas DataFrame (tf-idf table) which is the 'sklearn_df' with the help of pandas

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(pdfs_Dataset_Only_Letters)  # Fit the vectorizer to the data and transform it to see the tf-idf result for each word in a file
sklearn_df = pd.DataFrame(data = X.toarray(),columns=vectorizer.get_feature_names_out()) # Use the vectorizer result to create a table by mapping the result with the names of the columns (with thehelp of columns=vectorizer.get_feature_names_out()) which will be the texts themselves

print (X,'\n')
print(X.toarray())

# sklearn_df


# Get the given % score range
# We should pick a high percentage because some words might be important but were not used much across the files
# Also, for a word to have a value other than zero(0), it means that it is relevant to some degrees.
# So we can't just ignore most of them like that

percentage = 80
number_of_docs = 2  # Note: This will be picked automatically
final_words_for_lib = []

counter3 = 0

for i in range(number_of_docs):
    # Check if the row index is within the DataFrame bounds
    if counter3 >= 0 and counter3 < sklearn_df.shape[0]:
        # Calculation of the range (max and min) of values to be extracted
        # Max = max in the row and add 0.000001 for range accuracy purpose
        max_value = sklearn_df.iloc[counter3].max()

        # Min - calculate it
        min_value = (max_value * (100 - percentage)) / 100

        # Adjust min and max values slightly for range accuracy
        min_value -= 1e-13
        max_value += 1e-13

        # Get the columns where the row values fall within the specified range
        words_in_range = sklearn_df.columns[(sklearn_df.iloc[counter3] >= min_value) & (sklearn_df.iloc[counter3] <= max_value)]

        # Append the words in range to the final list
        final_words_for_lib.extend(list(words_in_range))
    
    else:
        print(f"Error: row_index {counter3} is out-of-bounds")

    counter3 += 1

# Print the final list of words for verification
print(final_words_for_lib)

# Find unique words
unique_final_words_for_lib = np.unique(np.array(final_words_for_lib))

# print('Total number of words in the table: ', sklearn_df.shape[1],'\n')
# print('Number of final words: ', len(final_words_for_lib),'\n')
# print('Number of unique final words: ', len(unique_final_words_for_lib),'\n')
# print('Unique Final Words: ',unique_final_words_for_lib)