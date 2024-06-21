from django.urls import path
from .views import FlagCreateView, CheckFlagStatus


urlpatterns = [
    path('create-flags/', FlagCreateView.as_view(), name='create-flag'),
    path('check-status/', CheckFlagStatus.as_view(), name='check-flag'),

]
