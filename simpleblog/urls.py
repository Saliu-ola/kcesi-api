from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("groups/", include("group.urls")),
    path("categories/", include("category.urls")),
    path("seci-activity-score/", include("leader.urls")),
    path("organizations/", include("organization.urls")),
    path("resources/", include("resource.urls")),
    path("forums/", include("forum.urls")),
    path("browser-histories/", include("browser_history.urls")),
    path("topics/", include("topics.urls")),
    path("platforms/", include("platforms.urls")),
    path("chats/", include("in_app_chat.urls")),
    path("blogs/", include("blog.urls")),
    path("feedbacks/", include("feedback.urls")),
    path("hate-speech/", include("hate_speech.urls")),
    path("auth/", include("accounts.urls")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v2/doc/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/v2/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
