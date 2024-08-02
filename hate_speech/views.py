from rest_framework import generics, mixins, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from .models import BadWord
from .serializers import BadWordSerializer, HateSpeechCheckerSerializer
from rest_framework import generics, status, viewsets, filters
from rest_framework.decorators import action
from simpleblog.ai import clean_data_and_lemmatize
import joblib
from simpleblog.pagination import CustomPagination

model = joblib.load("trained_model.pkl")
cv = joblib.load("vectorizer.pkl")


def get_bad_word_prediction_score_using_model(new_text):
    text = cv.transform([new_text]).toarray()
    speech_with_predicted_model = model.predict(text)
    return speech_with_predicted_model


class BadWordsViewSets(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = BadWordSerializer
    permission_classes = [AllowAny]
    queryset = BadWord.objects.all()
    pagination_class = CustomPagination

    def create(self, request, *args, **kwargs):
        if BadWord.objects.exists():
            return Response(
                {
                    "error": "Only one collection is allowed to be saved. You can only remove or add."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            for obj in page:
                obj.related_terms = sorted(obj.related_terms)
            return self.get_paginated_response(
                self.get_serializer(page, many=True).data
            )

        for obj in queryset:
            obj.related_terms = sorted(obj.related_terms)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=BadWordSerializer,
        url_path="add-words",
    )
    def add_words(self, request, pk=None):
        serializer = BadWordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            obj = self.get_queryset().first()
            if obj is None:
                return Response(
                    {
                        "error": "No BadWord instance found. Ensure to create an instance"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_words = serializer.validated_data["related_terms"]
            old_words = obj.related_terms
            merged_words = list(set(new_words + old_words))
            obj.related_terms = merged_words
            obj.save()

            return Response(status=200, data={"message": "words added successfully"})
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=BadWordSerializer,
        url_path="remove-words",
    )
    def remove_words(self, request, pk=None):
        serializer = BadWordSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            obj = self.get_queryset().first()
            if obj is None:
                return Response(
                    {"error": "No BadWord instance found.Ensure to create an instance"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            new_words = serializer.validated_data["related_terms"]
            old_words = obj.related_terms
            merged_words = [word for word in old_words if word not in new_words]
            obj.related_terms = merged_words
            obj.save()

            return Response(status=200, data={"message": "words removed successfully"})
        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=HateSpeechCheckerSerializer,
        url_path="check-hate-speech",
    )
    def check_hate_speech(self, request, pk=None):
        serializer = HateSpeechCheckerSerializer(data=request.data)
        if serializer.is_valid():
            incoming_text = serializer.validated_data["text"]
            clean_and_lematize_text = clean_data_and_lemmatize(incoming_text)
            bad_words = self.get_queryset().first().related_terms
            bad_words_in_input = [
                word for word in clean_and_lematize_text if word in set(bad_words)
            ]
            bad_word_count = len(bad_words_in_input)
            if bad_word_count > 0:
                return Response(
                    status=400,
                    data={
                        "message": "'Alert! The text contains one or more bad words.'"
                    },
                )
            else:
                return Response(
                    status=200,
                    data={"message": "OK"},
                )

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        methods=["POST"],
        detail=False,
        permission_classes=[AllowAny],
        serializer_class=HateSpeechCheckerSerializer,
        url_path="predict-word-with-model",
    )
    def predict_word_with_model(self, request, pk=None):
        serializer = HateSpeechCheckerSerializer(data=request.data)
        if serializer.is_valid():
            incoming_text = serializer.validated_data["text"]
            predicted_text = get_bad_word_prediction_score_using_model(incoming_text)
            return Response(status=200, data={"message": predicted_text})

        return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)
