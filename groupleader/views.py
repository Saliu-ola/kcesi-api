from django.shortcuts import render
from rest_framework import generics 
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated , AllowAny
import string
import nltk
import requests
import pandas as pd
import numpy as np
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from rest_framework.views import APIView 
from rest_framework.response import Response
from rest_framework import status
from pypdf import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from nltk.corpus import stopwords
from rest_framework.generics import GenericAPIView
import spacy 

class GroupLeaderListCreateView(generics.ListCreateAPIView):
    queryset = GroupLeader.objects.all()
    serializer_class = GroupLeaderSerializer
    permission_classes = [IsAuthenticated]

    
class GroupLeaderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroupLeader.objects.all()
    serializer_class = GroupLeaderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        group_id = self.kwargs['group_id']
        return get_object_or_404(GroupLeader,group=group_id)



class LibraryOptionListCreateView(generics.ListCreateAPIView):
    queryset = LibraryOption.objects.all()
    serializer_class = LibraryOptionSerializer
    permission_classes = [IsAuthenticated]

class LibraryOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryOption.objects.all()
    serializer_class = LibraryOptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        group_id = self.kwargs['group_id']
        return get_object_or_404(LibraryOption,group=group_id)


class LibraryFileListCreateView(generics.ListCreateAPIView):
    queryset = LibraryFile.objects.all()
    serializer_class = LibraryFileSerializer
    permission_classes = [IsAuthenticated]

class LibraryFileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryFile.objects.all()
    serializer_class = LibraryFileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        group_id = self.kwargs['group_id']
        libraryfile_id =self.kwargs['libraryfile_id']
        return get_object_or_404(LibraryFile,group=group_id,pk=libraryfile_id)



# Ensure NLTK data files are downloaded
# nltk.download('stopwords')
# nltk.download('punkt')
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')


stop_words = stopwords.words('english')

def stop_word_removal(text, stop_word_corpus, punct_str):
    clean_text = ' '.join([word.lower() for word in text.split() if word.lower()
                 not in stop_word_corpus]).replace('\n',' ')
    return clean_text.translate(str.maketrans('', '', punct_str))

class ProcessLibraryFiles(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = SyncLibraryFileSerializer
    def get(self, request, *args, **kwargs):
        library_files = LibraryFile.objects.filter(is_synchronize=False)
        processed_files = []
        generated_words = {}

        for lib_file in library_files:
            response = requests.get(lib_file.file_url)
            if response.status_code == 200:
                with open('temp.pdf', 'wb') as f:
                    f.write(response.content)
                
                reader = PdfReader('temp.pdf')
                fullfileText = ""
                for i in range(len(reader.pages)):
                    page = reader.pages[i]
                    fileText = page.extract_text()
                    fullfileText += fileText

                pdfs_Dataset = [fullfileText]

                # Apply lemmatization and stop word removal
                nlp = spacy.load('en_core_web_sm')
                pdfs_Dataset_Lemmatized = [' '.join([token.lemma_ for token in nlp(text)]) for text in pdfs_Dataset]
                pdfs_Dataset_cleaned = [stop_word_removal(text, stop_words, string.punctuation) for text in pdfs_Dataset_Lemmatized]
                pdfs_Dataset_Only_Letters = [' '.join([word for word in text.split() if word.isalpha()]) for text in pdfs_Dataset_cleaned]

                # TF-IDF Processing
                vectorizer = TfidfVectorizer()
                X = vectorizer.fit_transform(pdfs_Dataset_Only_Letters)
                sklearn_df = pd.DataFrame(data=X.toarray(), columns=vectorizer.get_feature_names_out())

                # Extract words based on the given percentage
                percentage = 80
                number_of_docs = len(pdfs_Dataset_Only_Letters)
                final_words_for_lib = []

                for i in range(number_of_docs):
                    max_value = sklearn_df.iloc[i].max()
                    min_value = (max_value * (100 - percentage)) / 100
                    min_value -= 1e-13
                    max_value += 1e-13
                    words_in_range = sklearn_df.columns[(sklearn_df.iloc[i] >= min_value) & (sklearn_df.iloc[i] <= max_value)]
                    final_words_for_lib.extend(list(words_in_range))

                unique_final_words_for_lib = np.unique(np.array(final_words_for_lib))
                generated_words[lib_file.filename] = list(unique_final_words_for_lib)
                
                # Update the related_terms_library_b field in the Group model
                group = lib_file.group
                if group.related_terms_library_b is None:
                    group.related_terms_library_b = []
                group.related_terms_library_b.extend(unique_final_words_for_lib)
                group.related_terms_library_b = list(np.unique(np.array(group.related_terms_library_b)))  # Remove duplicates
                group.save()

                # Update the is_synchronize field
                lib_file.is_synchronize = True
                lib_file.save()
                processed_files.append(lib_file.filename)

        return JsonResponse({
            'processed_files': processed_files,
            'generated_words': generated_words,
            'message': 'TF-IDF processing completed successfully'
        }, status=status.HTTP_200_OK)