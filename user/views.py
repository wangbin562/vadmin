# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
myuser接口
"""

import json
import traceback
import logging
import requests  # pylint: disable=E0401
from django.http import HttpResponse
from django.db import transaction
from django.contrib import auth
from utils import err_code
from utils import cache_api
from utils import field_format
from user.models import User

logger = logging.getLogger(__name__)
