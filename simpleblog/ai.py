import string
import google.generativeai as genai
import os


GOOGLE_GEMINI_API_KEY = os.environ.get("GOOGLE_GEMINI_API_KEY")
genai.configure(api_key=GOOGLE_GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')


def fetch_related_terms(keyword_title, description, input_sentence):
    """Fetch related terms for a given keyword and description, and return them as cleaned and lemmatized words."""
    response = model.generate_content(
        f"Assuming i have a keyword '{keyword_title}' and its description: '{description}' , what is the percentage relevance of the words in the input sentence '{input_sentence}' as regards to the  keyword and description?. return the percentage alone. nothing else aside a percentage please.always append the percentage,even if it is 0%"
    )
    result = response.text

    return result


print(
    fetch_related_terms(
        keyword_title="Biology",
        description="study of reproduction",
        input_sentence="I love football",
    )
)


# from nltk.corpus import stopwords
# from nltk.stem import WordNetLemmatizer
# from nltk.tokenize import word_tokenize
# import string
# import openai


# def fetch_related_terms(keyword_title, description):
#     # Define the system message to set the context for the conversation
#     system_message = {
#         "role": "system",
#         "content": f"You are a helpful assistant that provides related terms for the topic '{keyword_title}' based on the description '{description}'.",
#     }

#     # Define the user message to prompt the model
#     user_message = {"role": "user", "content": "What are some related terms?"}

#     # Combine the system and user messages
#     messages = [system_message, user_message]

#     # Send the request to the ChatGPT API
#     response = openai.Completion.create(
#         engine="gpt-3.5-turbo",
#         prompt=messages,
#         max_tokens=100,  # Adjust the number of tokens as needed
#     )

#     # Extract the generated text
#     generated_text = response['choices'][0]['text']

#     # Split the generated text into words
#     words = generated_text.split()

#     return words


# def clean_normalize_lemmatize(words):
#     # Convert to lowercase
#     words = [word.lower() for word in words]

#     # Remove punctuation
#     words = [''.join(c for c in w if c not in string.punctuation) for w in words]

#     # Remove stopwords
#     stop_words = set(stopwords.words('english'))
#     words = [word for word in words if word not in stop_words]

#     # Lemmatize
#     lemmatizer = WordNetLemmatizer()
#     words = [lemmatizer.lemmatize(word) for word in words]

#     return words


# # Example usage
# keyword_title = "biology"
# description = "study of living things"

# # Fetch related terms using the placeholder function
# related_terms = fetch_related_terms(keyword_title, description)

# # Clean, normalize, and lemmatize the terms
# base_words = clean_normalize_lemmatize(related_terms)

# print(base_words)
