# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111
import importlib
import json
import traceback

from django.apps import AppConfig
from django.conf.urls import url


class AppConfigEx(AppConfig):
    name = "vadmin_standard"
    verbose_name = u"通用"

    def ready(self):
        from django.conf import settings
        from django.db.utils import ProgrammingError, OperationalError

        for app in settings.INSTALLED_APPS:
            try:
                module = importlib.import_module("%s.views" % app)
            except (BaseException,):
                continue

        module = importlib.import_module(settings.ROOT_URLCONF)
        dict_url = {}
        for url_pattern in module.urlpatterns:
            pattern = url_pattern.pattern
            dict_url[str(pattern)] = url_pattern

        # 加载到URL中
        try:
            from vadmin_standard.models import Api
            queryset = Api.objects.filter(del_flag=False)
            for obj in queryset:
                pattern = "%s/%s/" % (obj.module.replace(".", "/"), obj.name)
                # pattern = "%s/%s/" % (obj.module.split(".")[0], obj.name)
                if obj.param:
                    param = json.loads(obj.param)
                    for p in param:
                        if "paramType" in p and p["paramType"].lower() == "path":
                            pattern = pattern + ("/%s/" % p["name"])

                if pattern in dict_url:
                    continue

                try:
                    api_module = importlib.import_module(obj.module)
                    url_pattern = url(pattern, getattr(api_module, obj.name))
                    module.urlpatterns.append(url_pattern)
                except (BaseException,):
                    pass
        except ProgrammingError as e:
            pass
        except OperationalError as e:
            pass

        except (BaseException,):
            print(traceback.format_exc())
            pass

        try:
            from vadmin_standard.models import Environment
            obj = Environment.objects.all().first()
            if not obj:
                Environment.objects.create()

        except (BaseException,):
            pass
