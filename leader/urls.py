from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CombinationViewSets,
    InternalizationViewSets,
    SocializationViewSets,
    ExternalizationViewSets,
    SECIActivityLeadersView,
)

app_name = 'leaders-table'

router = DefaultRouter()
router.register('soicalization', SocializationViewSets)
router.register('externalization', ExternalizationViewSets)
router.register('internalization', InternalizationViewSets)
router.register('combination', CombinationViewSets)


urlpatterns = [
    path('', include(router.urls)),
    path('seci-activity-leaderss/', SECIActivityLeadersView.as_view(), name='activity-scores'),
]
