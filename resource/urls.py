from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ResourceDownloadViewSet, ResourcesViewSets, ResourceDeleteView, FileSizeCreateView, FileSizeListView, FileSizeRetrieveView, FileSizeUpdateView

app_name = 'resource'

router = DefaultRouter()

# router.register('', ResourceDownloadViewSet)
router.register(r'resource-downloads', ResourceDownloadViewSet)
router.register('', ResourcesViewSets)

urlpatterns = [
    path('', include(router.urls)),

    path('filesize/create/', FileSizeCreateView.as_view(), name='filesize-create'),
    path('delete/<int:id>/', ResourceDeleteView.as_view(), name='resource-destroy-view'),
    path('filesize/update/', FileSizeUpdateView.as_view(), name='filesize-update'),
    path('filesize/<str:file_type>/', FileSizeRetrieveView.as_view(), name='filesize-retrieve'),
    path('filesizes/list/', FileSizeListView.as_view(), name='filesize-list'),

]