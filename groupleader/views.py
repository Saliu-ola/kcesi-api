from django.shortcuts import render
from rest_framework import generics
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated, AllowAny
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
from rest_framework.exceptions import NotFound
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.exceptions import PermissionDenied
from simpleblog.pagination import CustomPagination
from .permissions import IsGroupLeaderPermission, CanChangeFileStatusPermission
from rest_framework.exceptions import ValidationError


class GroupLeaderListCreateView(generics.ListCreateAPIView):
    queryset = GroupLeader.objects.all()
    serializer_class = GroupLeaderSerializer
    permission_classes = [IsAuthenticated]


class GroupLeaderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroupLeader.objects.all()
    serializer_class = GroupLeaderSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        group_id = self.kwargs["group_id"]
        return get_object_or_404(GroupLeader, group=group_id)


class LibraryOptionListCreateView(generics.ListCreateAPIView):
    queryset = LibraryOption.objects.all()
    serializer_class = LibraryOptionSerializer
    permission_classes = [IsAuthenticated]


class LibraryOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryOption.objects.all()
    serializer_class = LibraryOptionSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        group_id = self.kwargs["group_id"]
        return get_object_or_404(LibraryOption, group=group_id)


class LibraryFileListCreateView(generics.ListCreateAPIView):
    queryset = LibraryFile.objects.all()
    serializer_class = LibraryFileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        group_id = self.kwargs.get('group_id')
        if not group_id:
            raise ValidationError("Ensure you pick a group")

        group = get_object_or_404(Group, id=group_id)
        is_group_leader = GroupLeader.objects.filter(user=self.request.user, group=group).exists()

        if is_group_leader:
            return LibraryFile.objects.filter(group=group)
        else:
            return LibraryFile.objects.filter(group=group, user=self.request.user)

    # def list(self, request, *args, **kwargs):
    #     queryset = self.get_queryset()
    #     page = self.paginate_queryset(queryset)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(self.add_is_group_leader(serializer.data))
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(self.add_is_group_leader(serializer.data))
    def list(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
        except ValidationError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(
                self.add_is_group_leader(serializer.data)
            )

        serializer = self.get_serializer(queryset, many=True)
        return Response(self.add_is_group_leader(serializer.data))

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(self.add_is_group_leader([serializer.data])[0], status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        group_id = self.kwargs.get('group_id')
        group = get_object_or_404(Group, id=group_id)
        serializer.save(user=self.request.user, group=group)

    def add_is_group_leader(self, data):
        group_id = self.kwargs.get('group_id')
        is_group_leader = GroupLeader.objects.filter(user=self.request.user, group_id=group_id).exists() if group_id else False
        for item in data:
            item['is_group_leader'] = is_group_leader
        return data


class LibraryFileRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryFile.objects.all()
    serializer_class = LibraryFileSerializer
    permission_classes = [IsAuthenticated, CanChangeFileStatusPermission]

    def get_object(self):
        group_id = self.kwargs["group_id"]
        libraryfile_id = self.kwargs["libraryfile_id"]
        return get_object_or_404(LibraryFile, group=group_id, pk=libraryfile_id)
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        if 'status' in request.data:
            if not GroupLeader.objects.filter(user=request.user, group=instance.group).exists():
                raise PermissionDenied("Only group leaders can change the status.")

  
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


# Ensure NLTK data files are downloaded
nltk.download("stopwords")
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("averaged_perceptron_tagger")


stop_words = stopwords.words("english")


def stop_word_removal(text, stop_word_corpus, punct_str):
    clean_text = " ".join(
        [word.lower() for word in text.split() if word.lower() not in stop_word_corpus]
    ).replace("\n", " ")
    return clean_text.translate(str.maketrans("", "", punct_str))


class ProcessLibraryFiles(GenericAPIView):
    permission_classes = [IsAuthenticated, IsGroupLeaderPermission]
    serializer_class = SyncLibraryFileSerializer

    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get('group_id')

        # Ensures d grup exists
        group = get_object_or_404(Group, id=group_id)

        # Filter LibraryFiles by group and is_synchronize flag
        library_files = LibraryFile.objects.filter(
            group=group,status='approved',
            is_synchronize=False
        )
        if not library_files.exists():
            return Response ({'message':'Up to date, no file to synchronize.'}, status = status.HTTP_200_OK)
        # print('filtered by group id')
        # library_files = LibraryFile.objects.filter(is_synchronize=False)/
        processed_files = []
        generated_words = {}

        for lib_file in library_files:
            file_url = lib_file.file_url
            if not file_url:
                continue
            # response = requests.get(lib_file.file_url)
            response = requests.get(file_url)
            if response.status_code == 200:
                with open("temp.pdf", "wb") as f:
                    f.write(response.content)

                reader = PdfReader("temp.pdf")
                fullfileText = ""
                for i in range(len(reader.pages)):
                    page = reader.pages[i]
                    fileText = page.extract_text()
                    fullfileText += fileText

                pdfs_Dataset = [fullfileText]

                # Apply lemmatization and stop word removal
                nlp = spacy.load("en_core_web_sm")
                pdfs_Dataset_Lemmatized = [
                    " ".join([token.lemma_ for token in nlp(text)])
                    for text in pdfs_Dataset
                ]
                pdfs_Dataset_cleaned = [
                    stop_word_removal(text, stop_words, string.punctuation)
                    for text in pdfs_Dataset_Lemmatized
                ]
                pdfs_Dataset_Only_Letters = [
                    " ".join([word for word in text.split() if word.isalpha()])
                    for text in pdfs_Dataset_cleaned
                ]

                # TF-IDF Processing
                vectorizer = TfidfVectorizer()
                X = vectorizer.fit_transform(pdfs_Dataset_Only_Letters)
                sklearn_df = pd.DataFrame(
                    data=X.toarray(), columns=vectorizer.get_feature_names_out()
                )

                # Extract words based on the given percentage
                percentage = 80
                number_of_docs = len(pdfs_Dataset_Only_Letters)
                final_words_for_lib = []

                for i in range(number_of_docs):
                    max_value = sklearn_df.iloc[i].max()
                    min_value = (max_value * (100 - percentage)) / 100
                    min_value -= 1e-13
                    max_value += 1e-13
                    words_in_range = sklearn_df.columns[
                        (sklearn_df.iloc[i] >= min_value)
                        & (sklearn_df.iloc[i] <= max_value)
                    ]
                    final_words_for_lib.extend(list(words_in_range))

                unique_final_words_for_lib = np.unique(np.array(final_words_for_lib))
                generated_words[lib_file.filename] = list(unique_final_words_for_lib)

                # Update the related_terms_library_b field in the Group model
                group = lib_file.group
                if group.related_terms_library_b is None:
                    group.related_terms_library_b = []
                group.related_terms_library_b.extend(unique_final_words_for_lib)
                group.related_terms_library_b = list(
                    np.unique(np.array(group.related_terms_library_b))
                )  # Remove duplicates
                group.save()

                # Update the is_synchronize field
                lib_file.is_synchronize = True
                lib_file.save()
                processed_files.append(lib_file.filename)

        return JsonResponse(
            {
                "processed_files": processed_files,
                "generated_words": generated_words,
                "message": "TF-IDF processing completed successfully",
            },
            status=status.HTTP_200_OK,
        )


# list all groups a user is the group leader


class GroupLeaderListView(generics.ListAPIView):
    serializer_class = GroupGroupLeaderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Group.objects.filter(leader__user=user)


class GroupLibrariesRetrieveView(generics.GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = GroupLibrariesSerializer
    pagination_class = CustomPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="library",
                type=str,
                description="Specify the library to retrieve (a or b)",
                required=True,
            )
        ]
    )
    def get(self, request, *args, **kwargs):
        group_id = self.kwargs.get("group_id")
        library = request.query_params.get("library")

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise NotFound("Group not found")

        # Check if the user is a group leader
        if not GroupLeader.objects.filter(user=request.user, group=group).exists():
            return Response(
                {
                    "detail": "You do not have permission to perform this action because you are not a group leader "
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if library == "a":
            terms = group.related_terms if group.related_terms is not None else []
            terms = sorted(terms)
            library_name = "Library A"
        elif library == "b":
            terms = (
                group.related_terms_library_b
                if group.related_terms_library_b is not None
                else []
            )
            terms = sorted(terms)
            library_name = "Library B"
        else:
            return Response(
                {"detail": "Invalid library"}, status=status.HTTP_400_BAD_REQUEST
            )

        if not terms:
            return Response(
                {"detail": f"{library_name} is empty", "results": []},
                status=status.HTTP_200_OK,
            )

        # return self.paginate_results(terms)

        # Paginate the terms
        page = self.paginate_queryset(terms)
        if page is not None:
            return self.get_paginated_response(page)

        return Response(terms)

    # def paginate_results(self, results):
    #     paginator = self.pagination_class()
    #     page = paginator.paginate_queryset(results, self.request, view=self)
    #     if page is not None:
    #         return paginator.get_paginated_response(page)
    #     return Response(results)


class AddWordsToLibraryView(generics.GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="library",
                type=str,
                description="Specify the library to add words to (a or b)",
                required=True,
            )
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {"words": {"type": "array", "items": {"type": "string"}}},
                "required": ["words"],
            }
        },
        responses={
            200: {"type": "object", "properties": {"detail": {"type": "string"}}},
            400: {"type": "object", "properties": {"detail": {"type": "string"}}},
            409: {"type": "object", "properties": {"detail": {"type": "string"}}},
        },
    )
    def post(self, request, *args, **kwargs):
        group_id = self.kwargs.get("group_id")
        library = request.query_params.get("library")
        new_words = request.data.get("words", [])

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise NotFound("Group not found")

        # Check if the user is a group leader
        if not GroupLeader.objects.filter(user=request.user, group=group).exists():
            return Response(
                {
                    "detail": "You do not have permission to perform this action because you are not a group leader"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not isinstance(new_words, list):
            return Response(
                {"detail": "Words should be provided as a list"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        existing_words = set()
        if library == "a":
            if group.related_terms is None:
                group.related_terms = []
            existing_words = set(group.related_terms)
        elif library == "b":
            if group.related_terms_library_b is None:
                group.related_terms_library_b = []
            existing_words = set(group.related_terms_library_b)
        else:
            return Response(
                {"detail": "Invalid library"}, status=status.HTTP_400_BAD_REQUEST
            )

        for word in new_words:
            if word in existing_words:
                return Response(
                    {"detail": f"The word '{word}' already exists in the library"},
                    status=status.HTTP_409_CONFLICT,
                )

        if library == "a":
            group.related_terms.extend(new_words)
            group.related_terms = list(set(group.related_terms))  # Remove duplicates
        elif library == "b":
            group.related_terms_library_b.extend(new_words)
            group.related_terms_library_b = list(
                set(group.related_terms_library_b)
            )  # Remove duplicates

        group.save()
        return Response(
            {"detail": "Words added successfully"}, status=status.HTTP_200_OK
        )


class DeleteWordsFromLibraryView(generics.GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="group_id", type=int, location=OpenApiParameter.PATH),
            OpenApiParameter(
                name="library",
                type=str,
                description="Specify the library to delete words from (a or b)",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name="words",
                type=str,
                description="Comma-separated words to delete from the specified library",
                required=True,
                location=OpenApiParameter.QUERY,
            ),
        ],
        responses={
            200: {
                "description": "Words deleted successfully",
                "content": {
                    "application/json": {
                        "schema": {
                            "type": "object",
                            "properties": {"detail": {"type": "string"}},
                        }
                    }
                },
            },
            400: {"description": "Invalid library or word"},
            403: {
                "description": "You do not have permission to perform this action because you are not a group leader"
            },
        },
    )
    def delete(self, request, *args, **kwargs):
        group_id = self.kwargs.get("group_id")
        library = request.query_params.get("library")
        words_to_delete = request.query_params.get("words", "")

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise NotFound("Group not found")

        # Check if the user is a group leader
        if not GroupLeader.objects.filter(user=request.user, group=group).exists():
            return Response(
                {
                    "detail": "You do not have permission to perform this action because you are not a group leader"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Convert the words_to_delete from string to list
        words_to_delete = words_to_delete.split(",")

        if library == "a":
            if group.related_terms is None:
                group.related_terms = []
            group.related_terms = [
                word for word in group.related_terms if word not in words_to_delete
            ]
        elif library == "b":
            if group.related_terms_library_b is None:
                group.related_terms_library_b = []
            group.related_terms_library_b = [
                word
                for word in group.related_terms_library_b
                if word not in words_to_delete
            ]
        else:
            return Response(
                {"detail": "Invalid library"}, status=status.HTTP_400_BAD_REQUEST
            )

        group.save()
        return Response(
            {"detail": "Words deleted successfully"}, status=status.HTTP_200_OK
        )


class EditWordsInLibraryView(generics.GenericAPIView):
    queryset = Group.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="library",
                type=str,
                description="Specify the library to edit words in (a or b)",
                required=True,
            )
        ],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "old_words": {"type": "array", "items": {"type": "string"}},
                    "new_words": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["old_words", "new_words"],
            }
        },
        responses={
            200: {"type": "object", "properties": {"detail": {"type": "string"}}}
        },
    )
    def put(self, request, *args, **kwargs):
        group_id = self.kwargs.get("group_id")
        library = request.query_params.get("library")
        old_words = request.data.get("old_words", [])
        new_words = request.data.get("new_words", [])

        try:
            group = Group.objects.get(id=group_id)
        except Group.DoesNotExist:
            raise NotFound("Group not found")

        # Check if the user is a group leader
        if not GroupLeader.objects.filter(user=request.user, group=group).exists():
            return Response(
                {
                    "detail": "You do not have permission to perform this action because you are not a group leader"
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        if not isinstance(old_words, list) or not isinstance(new_words, list):
            return Response(
                {"detail": "Old words and new words should be provided as lists"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if library == "a":
            if group.related_terms is None:
                group.related_terms = []
            for old_word, new_word in zip(old_words, new_words):
                if old_word in group.related_terms:
                    group.related_terms[group.related_terms.index(old_word)] = new_word
            group.related_terms = list(set(group.related_terms))  # Remove duplicates
        elif library == "b":
            if group.related_terms_library_b is None:
                group.related_terms_library_b = []
            for old_word, new_word in zip(old_words, new_words):
                if old_word in group.related_terms_library_b:
                    group.related_terms_library_b[
                        group.related_terms_library_b.index(old_word)
                    ] = new_word
            group.related_terms_library_b = list(
                set(group.related_terms_library_b)
            )  # Remove duplicates
        else:
            return Response(
                {"detail": "Invalid library"}, status=status.HTTP_400_BAD_REQUEST
            )

        group.save()
        return Response(
            {"detail": "Words edited successfully"}, status=status.HTTP_200_OK
        )
