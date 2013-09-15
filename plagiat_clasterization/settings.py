# Django settings
import os

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    ('Vitaliy Lyapota', '2vitalik@gmail.com'),
)

MANAGERS = ADMINS

PROJECT_PATH = os.path.dirname(__file__)
CURRENT_ROOT = os.path.join(PROJECT_PATH, '..')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'news_plagiat',  # 'plagiat_clasterization',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

TIME_ZONE = 'Europe/Kiev'
LANGUAGE_CODE = 'ru-ru'
SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

MEDIA_ROOT = ''
MEDIA_URL = ''
STATIC_ROOT = ''
STATIC_URL = '/static/'

STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = ')^8*56c=uxnrw=i78sr+(n%o&amp;7wue5%wf-jqzlrr6&amp;+=b8ya86'

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'plagiat_clasterization.urls'

WSGI_APPLICATION = 'plagiat_clasterization.wsgi.application'

TEMPLATE_DIRS = (
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'main',
)

LOGS_PATH = os.path.join(CURRENT_ROOT, '.logs')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[%(asctime)s] %(levelname)s: %(message)s',
        },
        'shorter': {
            'format': '[%(asctime)s] %(levelname).1s: %(message)s',
        },
        'exception': {
            'format': '\n' + ('-' * 120) + '\n' +
                      '[%(asctime)s] %(levelname)s: %(message)s' + '\n\n'
        },
        'short_exception': {
            'format': '\n'+'[%(asctime)s] %(levelname)s: %(message)s' + '\n'
        }
    },
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
        },
        'query_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'query.log'),
            'formatter': 'verbose',
        },
        'request_exception_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'request_exception.log'),
            'formatter': 'exception',
        },
        'request_warning_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'request_warning.log'),
            'formatter': 'short_exception',
        },
        'custom_error_file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'custom_error.log'),
            'formatter': 'shorter',
        },
        'custom_warning_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'custom_warning.log'),
            'formatter': 'shorter',
        },
        'custom_info_file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'custom_info.log'),
            'formatter': 'shorter',
        },
        'custom_debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'custom_debug.log'),
            'formatter': 'shorter',
        },
        'timer_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'timer.log'),
            'formatter': 'shorter',
        },
        'temp_debug_file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'temp_debug.log'),
            'formatter': 'shorter',
        },
        'temp_warning_file': {
            'level': 'WARNING',
            'class': 'logging.FileHandler',
            'filename': os.path.join(LOGS_PATH, 'temp_warning.log'),
            'formatter': 'shorter',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'request_warning_file',
                         'request_exception_file'],
            'level': 'WARNING',
            'propagate': True,
        },
        'django.db.backends': {
            'handlers': [], #['query_file'],  # 'console' only local!
            # 'handlers': ['query_file', 'console'],  # 'console' only local!
            # 'level': 'DEBUG',
            'level': 'ERROR',
            'propagate': True,
        },
        'project.custom': {
            'handlers': ['custom_debug_file', 'custom_info_file', # 'console'
                         'custom_warning_file', 'custom_error_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'project.temp': {
            'handlers': ['temp_debug_file', 'temp_warning_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'project.timer': {
            'handlers': ['timer_file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}

try:
    from local_settings import *
except ImportError:
    pass
