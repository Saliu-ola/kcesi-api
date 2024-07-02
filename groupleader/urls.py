

from django.urls import path, include

from .views import *


urlpatterns = [
    path('group-leader/', GroupLeaderListCreateView.as_view(), name='group-leader-list-create'),
    path('group-leader/<int:group_id>/', GroupLeaderRetrieveUpdateDestroyView.as_view(), name='group-leader-detail'),
    path('library-options/', LibraryOptionListCreateView.as_view(), name='library-option-list-create'),
    path('library-options/<int:group_id>/', LibraryOptionRetrieveUpdateDestroyView.as_view(), name='library-option-detail'),
    path('library-files/', LibraryFileListCreateView.as_view(), name='library-file-list-create'),
    path('library-files/<int:group_id>/file/<int:libraryfile_id>', LibraryFileRetrieveUpdateDestroyView.as_view(), name='library-file-detail'),

    path('process-library-files/', ProcessLibraryFiles.as_view(), name='process-library-files'),

    path('my-groups/', GroupLeaderListView.as_view(), name='my-groups'),

    path('group-library/<int:group_id>/libraries/', GroupLibrariesRetrieveView.as_view(), name='group-libraries'),
    path('group-library/<int:group_id>/libraries/add/', AddWordsToLibraryView.as_view(), name='add-words-to-library'),
    path('group-library/<int:group_id>/libraries/delete/', DeleteWordsFromLibraryView.as_view(), name='delete-words-from-library'),
]
