from django.shortcuts import render
from rest_framework import generics 
from .models import *
from .serializers import *
from rest_framework.permissions import IsAuthenticated , AllowAny
# Create your views here.


class GroupLeaderListCreateView(generics.ListCreateAPIView):
    queryset = GroupLeader.objects.all()
    serializer_class = GroupLeaderSerializer
    permission_classes = [AllowAny]

class GroupLeaderRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = GroupLeader.objects.all()
    serializer_class = GroupLeaderSerializer
    permission_classes = [AllowAny]



class LibraryOptionListCreateView(generics.ListCreateAPIView):
    queryset = LibraryOption.objects.all()
    serializer_class = LibraryOptionSerializer
    permission_classes = [AllowAny]

class LibraryOptionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LibraryOption.objects.all()
    serializer_class = LibraryOptionSerializer
    permission_classes = [AllowAny]