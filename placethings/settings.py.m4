# Django settings for placethings project.
# Preprocessed with m4


DEBUG = ifdef(`debug', `True', `False') 
TEMPLATE_DEBUG = DEBUG

DOMAIN = 'domain'

ADMINS = (
    ('Johntron', 'john.syrinek@gmail.com'),
    ('ashokrbp', 'ashokrbp@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'ifdef(`debug',`placethings_dev',`placethings')'             # Or path to database file if using sqlite3.
DATABASE_USER = 'placethings'             # Not used with sqlite3.
DATABASE_PASSWORD = 'XfZgtIr[h/TrWSo6'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"

MEDIA_ROOT = '/www/placethings.com/www/public_html/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = 'http://domain/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = '@+$5==^$sllrlbwv43rpw(iuy6a$uyjdqx=9tv#x28h#)n2s8s'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
	#'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
	'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.doc.XViewMiddleware',
   	'placethings.api.middleware.ResponseFormatter',
)

INTERNAL_IPS = ('127.0.0.1','10.211.55.2','10.37.129.2')

ROOT_URLCONF = 'placethings.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/www/placethings.com/www/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'placethings.api',
    #'placethings.activity_stream',
    'placethings.users',
    'placethings.things',
    'placethings.analytics',
    'placethings.youtube_auth',
    'placethings.mediahandler',
    'placethings.min',

)


AUTHENTICATION_BACKENDS = (
	'placethings.youtube_auth.backends.YoutubeBackend',
	'django.contrib.auth.backends.ModelBackend',
	'placethings.auth.backends.TwitterBackend',
)

FACEBOOK_CACHE_TIMEOUT = 1800
FACEBOOK_API_KEY = '5d56290fdf9ed3ccaef36bafbb26a23c'
FACEBOOK_SECRET_KEY = '3efb48afc6f643f8ae97ff0d420aa40f'
FACEBOOK_INTERNAL = True
REST_SERVER = 'http://api.facebook.com/restserver.php'

AUTH_PROFILE_MODULE = 'users.Profile'

VALID_UPLOAD_TYPES = {
	'I': ['png', 'jpg', 'jpeg', 'gif'],
	'A': ['mp3', 'mp4', 'm4p'],
	'T': ['txt'],
}

TWITTER_KEY = '6O7Xp7dXEDjW0FGnv3bPg'
TWITTER_SECRET = 'unA4E67v90wJPFfyfQmHGGFxxXlf5QuOwPgDM7KTSM'