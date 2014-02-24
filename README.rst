===============
django-yplaces
===============

YPLACES == Yet/Why Another Django Places App


Installation
============

1. Download dependencies:
    - Python 2.6+
    - Django 1.5+
    
2. ``pip install django-yplaces`` or ``easy_install django-yplaces``


Configuration
=============

settings.py
-----------

1. Add "yplaces" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        # all other installed apps
        'yplaces',
    )
      
2. Add logger handler::

    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            # all other handlers
            'log_file_yplaces': {
                'level': 'DEBUG',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(os.path.join(os.path.dirname( __file__ ), '..'), 'logs/yplaces.log'),
                'maxBytes': '16777216', # 16megabytes
             },
        },
        'loggers': {
            # all other loggers
            'yplaces': {
                'handlers': ['log_file_yplaces'],
                'propagate': True,
                'level': 'DEBUG',
            }
        }
    }

3. Configure YPLACES's settings::

    YPLACES = {
        # API URL Namespace (e.g. YPLACES URL is in /api/v1, and the respective Django URL namespaces are 'api' and 'v1')
        'api_url_namespace': 'api:v1',
    }

4. Don't forget to set the 'MEDIA_URL' variable, which defines the root folder to where files will be uploaded (e.g. profile pictures) and the
variable necessary for the full URL's of the pictures to be built::

    MEDIA_ROOT = os.path.join(BASE_DIR, 'static/uploads/')
    MEDIA_URL = HOST_URL + '/static/uploads/'

Logs
----

Create a 'logs' folder in your project's root folder (if you don't have one already).
Your project folder should look something like this::

    myproject/
        __init__.py
        settings.py
        urls.py
        wsgi.py
    logs/
    manage.py

Database
--------

Run ``python manage.py syncdb`` to create the yplaces models.

URLs
----

1. Add app URL namespace to top-level ``urls.py``::

    # myproject/urls.py
    # ============

    urlpatterns = patterns('',
       # all other url mappings
       url(r'^places', include('yplaces.urls', namespace='yplaces')),
    )
	
2. Add app to API namespace::

    # myproject/api/urls.py
    # ============
    
    urlpatterns = patterns('',
        # all other api url mappings
        url(r'^/places', include('yplaces.api.urls', namespace='yplaces')),
    )