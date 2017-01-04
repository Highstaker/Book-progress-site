"""
WSGI config for myresite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
from os import path
import sys
SCRIPT_DIR = path.dirname(path.realpath(__file__))
sys.path = [path.join(path.dirname(path.dirname(SCRIPT_DIR)), i) for i in ["",
				"env/lib/python3.4",
				 "env/lib/python3.4/plat-x86_64-linux-gnu",
				 "env/lib/python3.4/lib-dynload",
				 "env/lib/python3.4/site-packages",
]] + sys.path # for some reason it won't import my env libraries, only global ones. Had to prepend em manually.

# print("Python path:", sys.path)#debug
# import django
# import django_extensions
# print("Django version:", django.VERSION)#debug #should be 1.10
# print("Django path:", django.__path__)#debug
# print("Django extensions version:", django_extensions.VERSION)#debug

from django.core.wsgi import get_wsgi_application
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myresite.prod_settings")

application = get_wsgi_application()
