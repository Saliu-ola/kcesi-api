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
