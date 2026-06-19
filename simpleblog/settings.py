
from datetime import timedelta
from pathlib import Path
import dj_database_url
from decouple import config
import os
import cloudinary


# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY")
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = [
    'channels',
    'daphne',
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "group",
    "chat",
    "accounts",
    "organization",
    "platforms",
    "in_app_chat",
    "resource",
    "blog",
    "forum",
    "topics",
    "browser_history",
    "category",
    "leader",
    "feedback",
    "hate_speech",
    "groupleader",
    "activity_flag",
    "activity_log",
    # third-party-apps
    "rest_framework",
    "corsheaders",
    'django_filters',
    "rest_framework.authtoken",
    'drf_spectacular',
    "debug_toolbar",
    'cloudinary_storage',
    'cloudinary',
]

AUTH_USER_MODEL = "accounts.User"


CLIENT_URL = config('CLIENT_URL')
REDIS_URL = config('REDIS_URL', 'redis://127.0.0.1:6379')


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",


    #This is for updating d hatespeech library periodically(7days)
    "hate_speech.middleware.UpdateRelatedTermsMiddleware"
]

ROOT_URLCONF = "simpleblog.urls"
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = ['https://staging-kscei.onrender.com',"http://localhost:5173","http://localhost:3000","http://localhost:3001"]
REST_FRAMEWORK = {
    "NON_FIELD_ERRORS_KEY": "errors",
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    "DEFAULT_AUTHENTICATION_CLASSES": (
        # "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated"),
    "DEFAULT_PAGINATION_CLASS": "simpleblog.pagination.CustomPagination",
    "PAGE_SIZE": 10,
}


SPECTACULAR_SETTINGS = {
    "SCHEMA_PATH_PREFIX": r"/api/v1",
    "DEFAULT_GENERATOR_CLASS": "drf_spectacular.generators.SchemaGenerator",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_PATCH": True,
    "COMPONENT_SPLIT_REQUEST": True,
    "SWAGGER_UI_SETTINGS": {
        "deepLinking": True,
        "persistAuthorization": True,
        "displayOperationId": True,
    },
    "UPLOADED_FILES_USE_URL": True,
    "TITLE": "KCESI-API",
    "DESCRIPTION": "KCESI-API",
    "VERSION": "1.0.0",
    "LICENCE": {"name": "BSD License"},
    "CONTACT": {"name": "Oladitan Saliu ", "email": "saliuoladitan@gmail.com"},
    "POSTPROCESSING_HOOKS": ["simpleblog.schema_hooks.postprocess_schema_hooks"],
}


SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=6),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "SIGNING_KEY": SECRET_KEY,
    "AUTH_HEADER_TYPES": ("Bearer",),
    # "Bearer <Token>"
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "simpleblog.wsgi.application"
ASGI_APPLICATION = "simpleblog.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [
                {
                    "address":REDIS_URL , # "REDIS_TLS_URL"
                }
            ]
        },
    }
}

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.sqlite3",
#         "NAME": BASE_DIR / "db.sqlite3",
#     }
# }

# DATABASES["default"] = dj_database_url.parse(config("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'kseci-db',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/static/"
# Following settings only make sense on production and may break development environments.
# if not DEBUG:
#     # Tell Django to copy statics to the `staticfiles` directory
#     # in your application directory on Render.
#     STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
# # Turn on WhiteNoise storage backend that takes care of compressing static files
# # and creating unique names for each version so they can safely be cached forever.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# for Emails

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST")
EMAIL_PORT = config("EMAIL_PORT")
EMAIL_HOST_USER = config("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS = "EMAIL_USE_TLS"
# EMAIL_USE_SSL = True


GOOGLE_GEMINI_API_KEY = config("GOOGLE_GEMINI_API_KEY")

# Add your Cloudinary configuration
# cloudinary.config(
#     cloud_name=config('CLOUD_NAME'),
#     api_key=config("API_KEY"),
#     api_secret=config("API_SECRET"),
# )

# Base URL for media files
BASE_URL = 'http://103.135.45.142:8000'

DEFAULT_PASSWORD = config("DEFAULT_PASSWORD")




# At the bottom of settings.py
#import drf_spectacular.openapi

# FORCE the setting into the live API settings
#api_settings.DEFAULT_SCHEMA_CLASS = drf_spectacular.openapi.AutoSchema

# --- Your previous Monkey Patch should follow below this ---
#import drf_spectacular.plumbing
#original_sanitize = drf_spectacular.plumbing.sanitize_result_object

#def patched_sanitize_result_object(result):
#    if isinstance(result, dict) and 'paths' in result:
#        for path in result['paths'].values():
#            for method in path.values():
#                if isinstance(method, dict) and 'operationId' not in method:
#                    method['operationId'] = 'unknown_operation'
#    return original_sanitize(result)

#drf_spectacular.plumbing.sanitize_result_object = patched_sanitize_result_object

