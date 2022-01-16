# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hmi.settings")
application = get_wsgi_application()

