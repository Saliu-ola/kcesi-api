

from django.urls import path, include

from .views import *


urlpatterns = [
    path('group-leader/', GroupLeaderListCreateView.as_view(), name='group-leader-list-create'),
    path('group-leader/<int:pk>/', GroupLeaderRetrieveUpdateDestroyView.as_view(), name='group-leader-detail'),
    path('library-options/', LibraryOptionListCreateView.as_view(), name='library-option-list-create'),
    path('library-options/<int:pk>/', LibraryOptionRetrieveUpdateDestroyView.as_view(), name='library-option-detail'),
    path('library-files/', LibraryFileListCreateView.as_view(), name='library-file-list-create'),
    path('library-files/<int:pk>/', LibraryFileRetrieveUpdateDestroyView.as_view(), name='library-file-detail'), 

    path('process-library-files/', ProcessLibraryFiles.as_view(), name='process-library-files'),
]
