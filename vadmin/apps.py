# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111
import traceback
from django.apps import AppConfig
from django.db.utils import ProgrammingError, OperationalError


# from django.utils.module_loading import autodiscover_modules

class AppConfigEx(AppConfig):
    name = 'vadmin'
    verbose_name = 'VAdmin'

    def ready(self):
        try:
            from vadmin_standard.models import Api
            Api.objects.filter(del_flag=False).update(del_flag=True)
        except ProgrammingError as e:
            pass
        except OperationalError as e:
            pass
        except (BaseException,):
            print(traceback.format_exc())

        from django.conf import settings
        app_path = getattr(settings, 'WSGI_APPLICATION')
        init_vadmin_settings(app_path)

        try:
            from vadmin import menu
            menu.MenuAuthManage().init_permissions()
            menu.MenuAuthManage().init_menu_permission()
        except ProgrammingError as e:
            pass
        except OperationalError as e:
            pass
        except (BaseException,):
            print(traceback.format_exc())


def init_vadmin_settings(app_path):
    import importlib
    import vadmin.settings as vadmin_settings
    from vadmin import const
    from django.conf import settings as django_settings

    settings = importlib.import_module("%s.settings" % app_path.split(".")[0])
    importlib.reload(settings)
    for key in dir(vadmin_settings):
        if key.find("V_") == 0:
            if hasattr(settings, key):
                setattr(django_settings, key, getattr(settings, key))
            else:
                setattr(django_settings, key, getattr(vadmin_settings, key))

    if "href" in (django_settings.V_INDEX_PAGE or {}):
        django_settings.V_MENU_ITEMS.insert(0, {'label': django_settings.V_INDEX_PAGE.get("label", "首页"),
                                                'href': django_settings.V_INDEX_PAGE["href"],
                                                'icon': django_settings.V_INDEX_PAGE.get('icon', 'fa-home')})
    elif "url" in (django_settings.V_INDEX_PAGE or {}):
        django_settings.V_MENU_ITEMS.insert(0, {'label': django_settings.V_INDEX_PAGE.get("label", "首页"),
                                                "url": django_settings.V_INDEX_PAGE.get("url", const.URL_HOME_VIEW),
                                                'icon': django_settings.V_INDEX_PAGE.get('icon', 'fa-home')})
