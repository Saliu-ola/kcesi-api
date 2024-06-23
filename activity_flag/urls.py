from django.urls import path
from .views import FlagCreateView, CheckFlagStatus
# from .views import FlagActivityView

urlpatterns = [
    path('create-flags/', FlagCreateView.as_view(), name='create-flag'),
    path('check-status/', CheckFlagStatus.as_view(), name='check-flag'), #Test Purposes

    # path('create-flags/', FlagActivityView.as_view(), name='flag-activity'),





]
