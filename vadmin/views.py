# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
views
"""
# import time
import datetime
import importlib
import json
import logging
import os
import shutil
import threading
import traceback
import copy
import requests
from django.conf import settings
from django.contrib import auth
from django.db import models
from django.db import transaction
from django.db.models import Max, Min, F
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.views.decorators.gzip import gzip_page

from vadmin import admin
from vadmin import admin_api
from vadmin import admin_auth
from vadmin import cache_api
from vadmin import common
from vadmin import const
from vadmin import event
from vadmin import field_translate
from vadmin import menu
from vadmin import report
from vadmin import service
from vadmin import step
from vadmin import step_ex
from vadmin import theme
from vadmin import widget_view
from vadmin import widgets
from vadmin.json_encoder import Encoder
from vadmin.models import ThemeConfig
from vadmin_standard.service import operation_log_add

logger = logging.getLogger(__name__)


def v_index(request):
    return render(request, 'v_index.html', {})


def v_index_view(request):
    """
    第一页，目前是登录
    """
    try:
        if request.user.is_authenticated:
            if const.UPN_REDIRECT_URL in request.GET:
                url = request.GET[const.UPN_REDIRECT_URL]
                result = step.Get(url=url, jump=True)
            else:
                result = step.Post(url="v_home/", jump=True, submit_type="hide")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_response = cache_api.get_cache(request)
        if o_response:
            return o_response

        result = widget_view.make_index_view(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_login(request):
    try:
        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)
        username = widget_data["username"]
        pwd = widget_data["pwd"]
        if username is None:
            result = step.Msg(text="用户名不能为空!", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if pwd is None:
            result = step.Msg(text="密码不能为空!", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        user = auth.get_user_model().objects.filter(username=username).first()
        if user is None:
            result = step.Msg(text="%s用户不存在!" % username, msg_type="error")

        elif (not user.is_active) or (not user.is_staff):
            result = step.Msg(text="%s用户无权登录!" % username, msg_type="error")

        else:
            if settings.V_PWD_ENCRYPT_KEY:
                from utils import aes
                pwd = aes.cbc_decrypt(pwd, settings.V_PWD_ENCRYPT_KEY)

            user = auth.authenticate(username=username, password=pwd)
            if user is None:
                result = step.Msg(text="密码错误!", msg_type="error")

            # 等于默认密码情况
            elif settings.V_DEFAULT_PWD and (pwd == settings.V_DEFAULT_PWD):
                o_step = step.Msg(text="等于初始密码，修改后才能使用!", msg_type="warning")
                o_theme = theme.get_theme(request.user.id)
                result = [o_step, widget_view.make_update_pwd(request, o_theme, username=username)]
            else:
                if getattr(settings, "AUTH_PASSWORD_VALIDATORS", None):
                    from django.core.exceptions import ValidationError
                    for dict_validation in settings.AUTH_PASSWORD_VALIDATORS:
                        lst_interface = dict_validation['NAME'].split(".")
                        o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                        o_class = getattr(o_module, lst_interface[-1])
                        try:
                            o_class().validate(pwd)
                        except ValidationError as e:
                            o_theme = theme.get_theme(request.user.id)
                            o_step = widget_view.make_update_pwd(request, o_theme, username=username)
                            result = step_ex.MsgBox(text=const.PWD_VALIDATION_MSG % (e.messages[0], const.PWD_LENGTH),
                                                    title="密码简单，请修改", width=600, height=260,
                                                    msg_type="error", step=[o_step, step.LayerClose()])
                            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                                content_type='application/json')
                auth.login(request, user)
                result = step.Post(url="v_home/", jump=True, submit_type="hide")

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_logout(request):
    auth.logout(request)
    result = step.Get(url="v_index_view/", jump=True)
    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


def v_update_pwd(request):
    try:
        content = request.POST[const.SUBMIT_WIDGET]
        widget_data = json.loads(content)
        username = widget_data.get("username", None)
        if username is None:
            result = admin_auth.check_opera_auth(request)
            if result:
                return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                    content_type="application/json")

        old_pwd = widget_data["old_pwd"]
        new_pwd = widget_data["new_pwd"]
        repeat_pwd = widget_data["repeat_pwd"]
        if settings.V_PWD_ENCRYPT_KEY:
            from utils import aes
            old_pwd = aes.cbc_decrypt(old_pwd, settings.V_PWD_ENCRYPT_KEY)
            new_pwd = aes.cbc_decrypt(new_pwd, settings.V_PWD_ENCRYPT_KEY)
            repeat_pwd = aes.cbc_decrypt(repeat_pwd, settings.V_PWD_ENCRYPT_KEY)

        if not old_pwd:
            result = step.Msg(text="旧密码不能为空。 ", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        elif not new_pwd:
            result = step.Msg(text="新密码不能为空。 ", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        elif not repeat_pwd:
            result = step.Msg(text="确定新密码不能为空。 ", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if new_pwd != repeat_pwd:
            result = step.Msg(text="新密码和确定新密码不一致。", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if username:
            user = auth.authenticate(username=username, password=old_pwd)
        else:
            user = auth.authenticate(username=request.user.username, password=old_pwd)

        if user is None:
            result = step.Msg(text="旧密码错误!", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        elif getattr(settings, "AUTH_PASSWORD_VALIDATORS", None):
            from django.core.exceptions import ValidationError
            for dict_validation in settings.AUTH_PASSWORD_VALIDATORS:
                lst_interface = dict_validation['NAME'].split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                o_class = getattr(o_module, lst_interface[-1])
                try:
                    o_class().validate(new_pwd, request.user)
                except ValidationError as e:
                    result = step_ex.MsgBox(text=const.PWD_VALIDATION_MSG % (e.messages[0], const.PWD_LENGTH),
                                            title="请不要设置简单密码", msg_type="error", width=600, height=260)
                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")

        user.set_password(new_pwd)
        user.save()

        auth.logout(request)
        o_step = step.Msg(text="修改密码成功，请重新登录!")
        result = [o_step, step.LayerClose(), step.Post(url=const.URL_INDEX_VIEW, jump=True)]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_update_pwd_other_user(request):
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model = auth.get_user_model()
        content = request.POST[const.SUBMIT_WIDGET]
        widget_data = json.loads(content)
        new_pwd = widget_data["new_pwd"]
        repeat_pwd = widget_data["repeat_pwd"]
        username = request.GET["username"]
        if settings.V_PWD_ENCRYPT_KEY:
            from utils import aes
            new_pwd = aes.cbc_decrypt(new_pwd, settings.V_PWD_ENCRYPT_KEY)
            repeat_pwd = aes.cbc_decrypt(repeat_pwd, settings.V_PWD_ENCRYPT_KEY)

        if not new_pwd:
            result = step.Msg(text="新密码不能为空。 ", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        elif not repeat_pwd:
            result = step.Msg(text="确定新密码不能为空。 ", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if new_pwd != repeat_pwd:
            result = step.Msg(text="新密码和确定新密码不一致。", msg_type="error")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if getattr(settings, "AUTH_PASSWORD_VALIDATORS", None):
            from django.core.exceptions import ValidationError
            for dict_validation in settings.AUTH_PASSWORD_VALIDATORS:
                lst_interface = dict_validation['NAME'].split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                o_class = getattr(o_module, lst_interface[-1])
                try:
                    o_class().validate(new_pwd)
                except ValidationError as e:
                    result = step_ex.MsgBox(text=const.PWD_VALIDATION_MSG % (e.messages[0], const.PWD_LENGTH),
                                            title="请不要设置简单密码", msg_type="error", width=600, height=260)
                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")

        user = model.objects.get(username=username)
        user.set_password(new_pwd)
        user.save()

        o_step = step.Msg(text="修改%s用户密码成功!" % username)
        result = [o_step, step.LayerClose()]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_home_view(request):
    """
    主页面
    """
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        o_template = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_home_view = o_template.HomeView(request, o_theme)
        o_content = o_home_view.make_view()
        result = service.refresh_page(request, o_content=o_content)

        if o_theme.menu_position == "top":
            result.append(step.WidgetUpdate(data={"name": const.WN_MENU_TOP, "value": "url:v_home_view/"}))
            result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0", "width": 0}))
            result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1", "width": "100%"}))

        else:
            o_page_template = o_template.Page(request, o_theme)
            o_menu_left = o_page_template.create_left()
            content = request.POST.get(const.SUBMIT_HIDE, "{}")
            dict_hide = json.loads(content)
            if int(dict_hide.get(const.WN_CONTENT_HIDE, 0)) == 2:
                pass
            else:
                result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0",
                                                      "width": o_page_template.WIDTH_LEFT,
                                                      "height": "100%",
                                                      "children": [o_menu_left, ]},
                                                mode="all"))
                result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1",
                                                      "width": "100%%-%s" % o_page_template.WIDTH_LEFT,
                                                      "height": "100%"}))

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_theme_view(request):
    """
    主题界面
    """
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.pk)
        o_grid_theme = theme.make_theme_view(request)
        result = service.refresh_page(request, o_grid_theme)
        # if o_theme.menu_position == "top":
        #     result.append(step.WidgetUpdate(data={"name": const.WN_MENU_TOP, "value": None}))
        #     # result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0", "width": 0}))
        #     # result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1", "width": "100%"}))
        # else:
        o_template = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_style = o_template.Style()
        result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0", "width": o_style.WIDTH_LEFT}))
        result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1",
                                              "width": "100%%-%s" % o_style.WIDTH_LEFT}))

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_theme_submit(request):
    """主题提交，第一次获取主题"""
    try:
        # 必须要登录，这样才知道用户使用的是什么主题
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps({}, ensure_ascii=False, cls=Encoder), content_type="application/json")

        widget_data = json.loads(request.POST.get(const.SUBMIT_WIDGET, "{}"))
        if widget_data:
            template = widget_data["template"]
            skin_color = widget_data.get("skin_color", None)  # 皮肤颜色
            theme_color = widget_data["theme_color"]
            menu_position = widget_data.get("menu_position", None)
            unit = widget_data.get("unit", None)
            font_family = widget_data.get("font_family", None)
            font_size = widget_data.get("font_size", None)
            top_color = widget_data.get("top_bg_color", None)
            left_color = widget_data.get("left_bg_color", None)

            o_config = ThemeConfig.objects.filter(user_id=request.user.id).first()
            if o_config is None:
                o_config = ThemeConfig(user_id=request.user.id, template=template, color=skin_color, style="{}")

            if template != o_config.template:
                template_data = copy.deepcopy(list(settings.V_STYLE_CONFIG[template].items())[0])
                dict_style = template_data[1]
                if template == settings.V_DEFAULT_TEMPLATE:
                    theme_color = settings.V_DEFAULT_THEME_COLOR or template_data[0]
                    left_color = settings.V_DEFAULT_LEFT_COLOR
                    top_color = settings.V_DEFAULT_TOP_COLOR
                    dict_style = theme.set_theme(dict_style, theme_color, left_color, top_color)

            else:
                if skin_color in settings.V_STYLE_CONFIG[template]:
                    dict_style = copy.deepcopy(settings.V_STYLE_CONFIG[template][skin_color])
                else:
                    dict_style = copy.deepcopy(list(settings.V_STYLE_CONFIG[template].values())[0])

                dict_style = theme.set_theme(dict_style, theme_color, left_color, top_color)
                if unit:
                    dict_style["base"]["unit"] = unit

                if menu_position:
                    dict_style["base"]["menu_position"] = menu_position

            dict_style["base"]["title"] = settings.V_TITLE.replace("{{\n}}", "")
            style = json.dumps(dict_style, ensure_ascii=False, cls=Encoder)
            o_config.template = template
            o_config.style = style
            o_config.color = skin_color
            o_config.save()
            o_theme = theme.Theme(o_config)
            # cache.set("theme_!@#_%s" % request.user.id, o_theme)

        else:  # 默认值
            if request.user.id:
                ThemeConfig.objects.filter(user_id=request.user.id).delete()
            # cache.set("theme_!@#_%s" % request.user.id, None)
            o_theme = theme.get_theme(request.user.id)

        dict_style = json.loads(o_theme.style)
        dict_style["update_time"] = datetime.datetime.now()
        result = [step.ChangeTheme(data=json.dumps(dict_style, ensure_ascii=False, cls=Encoder)),
                  step.ViewOpera(reload=True)]

        # if request.POST:
        #     o_theme = theme.get_theme(request.user.id)
        #     o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        #     panel = o_module.Page(request, o_theme).create_top()
        #     result.append(step.WidgetUpdate(data=panel, mode="all"))
        # else:
        #     result.append(step.ViewOpera(reload=True))

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_license_change(request):
    try:
        license, domain, port, expire_date = common.get_license()
        result = {}
        result["license"] = license
        result["domain"] = domain
        result["port"] = port
        result["expire_date"] = expire_date
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_select_search(request):
    """
    搜索框控件接口
    """
    try:
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps([], ensure_ascii=False, cls=Encoder), content_type="application/json")

        app_label = request.GET["app_label"]
        model_name = request.GET["model_name"]
        field_name = request.GET["field_name"]
        widget_name = request.GET.get("widget_name", None)
        widget_id = request.GET.get("widget_id", None)
        parent_app_label = request.GET.get("parent_app_label", None)
        parent_model_name = request.GET.get("parent_model_name", None)
        foreign_key_app_label = request.GET["foreign_key_app_label"]
        foreign_key_model_name = request.GET["foreign_key_model_name"]
        search_field = request.GET["search_field"]
        object_id = request.GET["object_id"]
        search_term = request.GET.get("search_term", "")

        foreign_key_model = admin_api.get_model(foreign_key_app_label, foreign_key_model_name)
        # foreign_key_model_admin = admin.site._registry.get(foreign_key_model) # 有可能没有注册
        queryset = foreign_key_model.objects.all()

        if search_term:
            import operator
            from functools import reduce
            # from django.db.models import Q
            lst_field_name = eval(search_field)
            # search_fields = []
            # for field in lst_field_name:
            #     search_fields.append("%s__icontains" % field)
            # select = Q()
            # select &= reduce(lambda x, y: x | Q(**{y: search_term}), search_fields,
            #                  Q(**{search_fields[0]: search_term}))
            or_queries = [models.Q(**{"%s__icontains" % field: search_term})
                          for field in lst_field_name]
            select = reduce(operator.or_, or_queries)
            queryset = queryset.filter(select)

        model_admin = admin_api.get_model_admin(app_label, model_name)
        if parent_model_name:
            parent_model_admin = admin_api.get_model_admin(parent_app_label, parent_model_name)
            if parent_model_admin and model_admin is None:
                model = admin_api.get_model(app_label, model_name)
                for inline in parent_model_admin.get_v_inlines(request):
                    if inline.model == model:
                        if object_id:
                            obj = model.objects.filter(pk=object_id).first()
                        else:
                            obj = None

                        db_field = model._meta.get_field(field_name)
                        obj_inline = inline(model=model, admin_site=admin.site)

                        queryset_filter = obj_inline.v_foreign_key_filter(request, queryset=queryset, db_field=db_field,
                                                                          obj=obj)  # 外键过滤
                        if isinstance(queryset_filter, QuerySet):
                            queryset = queryset_filter
                        break

        elif (model_admin is not None) and hasattr(model_admin, "foreign_key_filter"):
            try:
                if object_id:
                    obj = model_admin.model.objects.filter(pk=object_id).first()
                else:
                    obj = None
                db_field = admin_api.get_field(model_admin, field_name)
                queryset = model_admin.foreign_key_filter(request, queryset, db_field=db_field,
                                                          obj=obj)  # 外键过滤
            except (BaseException,):
                pass
        else:
            # 此外要判断是否需要过滤
            try:
                foreign_model_admin = admin_api.get_model_admin(foreign_key_app_label, foreign_key_model_name)
                queryset, use_distinct = foreign_model_admin.get_search_results(request, queryset, search_term)
            except (BaseException,):
                pass

        lst_data = []
        for obj in queryset[0:50]:
            lst_data.append((obj.pk, str(obj)))

        # 此处后面要改成updatewidgets，不能特殊处理
        if widget_id:
            result = step.WidgetUpdate(data={"id": widget_id, "data": lst_data})
        else:
            result = step.WidgetUpdate(data={"name": widget_name, "data": lst_data})
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        return HttpResponse(json.dumps([], ensure_ascii=False, cls=Encoder), content_type="application/json")


# def v_select_change(request, app_label, model_name, field_name, object_id=None):
#     """
#     搜索框(下拉框)联动过滤接口
#     """
#     try:
#         if not request.user.is_authenticated:
#             return HttpResponse(json.dumps([], ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#         model_admin = admin_api.get_model_admin(app_label, model_name)
#         db_field = admin_api.get_field(model_admin, field_name)
#         if object_id is not None:
#             obj = model_admin.get_object(request, object_id)
#         else:
#             obj = None
#
#         o_step = model_admin.select_change(request, db_field, obj)
#     except (BaseException,):
#         o_step = admin_auth.save_error(request)
#
#     return HttpResponse(json.dumps(o_step, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_input_search(request, app_label, model_name, search_field):
    try:
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps([], ensure_ascii=False, cls=Encoder), content_type="application/json")

        search_term = request.POST.get("search_term", "")
        model_admin = admin_api.get_model_admin(app_label, model_name)
        queryset = model_admin.opts.model.objects.all()
        queryset, use_distinct = model_admin.get_search_results(request, queryset, search_term)

        # 过滤后再搜索
        if search_term:
            import operator
            from functools import reduce
            lst_field_name = eval(search_field)
            or_queries = [models.Q(**{"%s__icontains" % field: search_term})
                          for field in lst_field_name]
            select = reduce(operator.or_, or_queries)
            queryset = queryset.filter(select)

        lst_data = []
        for obj in queryset[0:50]:
            lst_data.append(str(obj))

        # 此处后面要改成updatewidgets，不能特殊处理
        return HttpResponse(json.dumps(lst_data, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        return HttpResponse(json.dumps([], ensure_ascii=False, cls=Encoder), content_type="application/json")


def v_upload_file(request, callback=None):
    """
    上传文件
    """
    try:
        from utils import storage
        o_file = request.FILES["file"]
        obj = storage.ImageStorage()
        file_name = o_file.name
        now = datetime.datetime.now()
        now_date = now.strftime("%Y-%m-%d")
        path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, "files", now_date))
        if not os.path.exists(path):
            os.makedirs(path)

        src_path = os.path.normpath(os.path.join(path, file_name))
        if os.path.exists(src_path):
            name, suffix = os.path.splitext(file_name)
            file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
            src_path = os.path.normpath(os.path.join(path, file_name))

        url = obj._save(src_path, o_file)
        dst_path = None

        try:
            from file_manager.models import File
            md5 = common.get_md5(src_path)
            obj = File.objects.filter(md5=md5, completed=True, del_flag=False).first()
            flag = True
            if obj:
                save_path = obj.get_path()
                if os.path.exists(save_path):
                    flag = False
            # 新建
            if flag:
                size = os.path.getsize(src_path)
                file_type, duration = common.get_file_type(src_path)

                name, suffix = os.path.splitext(o_file.name)
                file_name = common.format_file_name(name)
                dst_path = os.path.normpath(os.path.join(path, file_name))
                if os.path.exists(dst_path):
                    file_name = "%s-%s%s" % (file_name, now.strftime("%H%M%S%f"), suffix)
                    dst_path = os.path.normpath(os.path.join("files", now_date, file_name))

                if not obj:
                    obj = File.objects.create(name=file_name, path=dst_path, md5=md5, size=size, completed=True,
                                              type=file_type, duration=duration)
                else:
                    obj.name = file_name
                    obj.path = dst_path
                    obj.size = size
                    obj.completed = True
                    obj.type = file_type
                    obj.duration = duration
                    obj.save()

                dst_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, dst_path))
                if src_path != dst_path:
                    shutil.copyfile(src_path, dst_path)

            if src_path != dst_path:
                try:
                    os.remove(src_path)
                except (BaseException,):
                    pass

            file_name = obj.get_name()
            url = obj.get_url()

        except (BaseException,):
            # 没有加载文件管理
            pass

        result = None
        callback = callback or request.GET.get("callback", None)
        if callback:
            lst_interface = callback.split(".")
            o_module = importlib.import_module(".".join(lst_interface[0:-1]))
            fun = getattr(o_module, lst_interface[-1])
            result = fun(request, obj)

        if isinstance(result, list):
            result.append(step.OperaSuccess(data={"name": file_name, "url": url}))
        else:
            result = [result, step.OperaSuccess(data={"name": file_name, "url": url})]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


def v_update_file_resume(request, callback=None):
    try:
        md5 = request.POST["md5"]
        content = request.FILES.get("content", None)
        file_name = request.POST.get("name", None)
        size = None
        if "size" in request.POST:
            size = int(request.POST["size"])

        from file_manager.models import File  # 没有加载文件管理，不支持断点续传
        callback = callback or request.GET.get("callback", None)
        obj = File.objects.filter(md5=md5, del_flag=False).first()
        if obj:
            if obj.completed:
                result = {"name": obj.name, "url": obj.get_url(), "upload_size": obj.size}

            else:
                file_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, obj.path.name))
                if content:
                    buf = content.file.read()
                    length = len(buf)
                    if "position" in request.POST:
                        position = int(request.POST["position"])
                        if position == 0:
                            open(file_path, "wb").write(buf)
                        else:
                            file_buf = open(file_path, "rb").read()
                            open(file_path, "wb").write(file_buf[0:position] + buf)
                        obj.upload_size = position + length
                    else:
                        open(file_path, "ab").write(buf)
                        obj.upload_size += length
                    obj.state = 6
                    obj.save()

                if obj.upload_size >= obj.size:
                    file_type, duration = common.get_file_type(file_path)
                    obj.type = file_type
                    obj.duration = duration
                    obj.completed = True
                    obj.state = 0
                    obj.save()
                    result = {"name": obj.name, "url": obj.get_url(), "upload_size": obj.upload_size}
                else:
                    result = {"upload_size": obj.upload_size}

            if obj.completed and callback:
                lst_interface = callback.split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                fun = getattr(o_module, lst_interface[-1])
                result_callback = fun(request, obj, end=True)
                if result_callback:
                    return HttpResponse(json.dumps(result_callback, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")

        else:
            with transaction.atomic():
                now = datetime.datetime.now()
                now_date = now.strftime("%Y-%m-%d")
                path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, "files", now_date))
                if not os.path.exists(path):
                    os.makedirs(path)

                file_path = os.path.normpath(os.path.join(path, file_name))
                if os.path.exists(file_path):
                    name, suffix = os.path.splitext(file_name)
                    name = common.format_file_name(name)
                    file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
                    file_path = os.path.normpath(os.path.join(path, file_name))

                if content:
                    open(file_path, "ab").write(content.file.read())

                url = os.path.normpath(os.path.join("files", now_date, file_name))
                obj = File.objects.create(md5=md5, size=size, name=file_name, path=url, upload_size=0, state=6)
                if callback:
                    lst_interface = callback.split(".")
                    o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                    fun = getattr(o_module, lst_interface[-1])
                    result_callback = fun(request, obj)
                    if result_callback:
                        return HttpResponse(json.dumps(result_callback, ensure_ascii=False, cls=Encoder),
                                            content_type="application/json")

            result = {"upload_size": 0}

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


def v_upload_file_by_model(request, app_label, model_name, field_name):
    """
    上传文件
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model = admin_api.get_model(app_label, model_name)
        db_field = model._meta.get_field(field_name)
        o_file = request.FILES["file"]

        from utils import storage
        obj_storage = storage.ImageStorage()
        if hasattr(db_field, "upload_to") and db_field.upload_to:
            try:
                path1, path2 = db_field.upload_to.rsplit("/", 1)
                file_path = os.path.normpath(os.path.join(path1, datetime.datetime.now().strftime(path2),
                                                          o_file.name))
            except (BaseException,):
                file_path = os.path.normpath(os.path.join(db_field.upload_to, o_file.name))
        else:
            file_path = o_file.name

        url = obj_storage._save(file_path, o_file)
        url = settings.MEDIA_URL + url
        # result = step.WidgetUpdate(widgets.Upload(name=field_name, value=url))
        # if o_field.upload_to:
        #     url = "/media/%s/%s" % (o_field.upload_to.strip().strip("/"), file_name)
        # else:
        #     url = file_name

        result = step.OperaSuccess(data={"name": o_file.name, "url": url})
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


def v_upload_ueditor(request, app_label, model_name, field_name):
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        from vadmin import ueditor
        action = request.GET.get("action", "")

        reponse_action = {
            "config": ueditor.get_ueditor_settings,
            "uploadimage": ueditor.upload_file,
            "uploadscrawl": ueditor.upload_file,
            "uploadvideo": ueditor.upload_file,
            "uploadfile": ueditor.upload_file,
            "catchimage": ueditor.catcher_remote_image,
            # "listimage": list_files,
            # "listfile": list_files
        }
        value = reponse_action[action](request)
        return HttpResponse(json.dumps(value, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_word(request):
    try:
        url = request.GET.get("url", None)
        file_id = request.GET.get("file_id", None)
        if url:
            now = datetime.datetime.now()
            now_date = now.strftime("%Y-%m-%d")
            path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, "word", now_date))
            if not os.path.exists(path):
                os.makedirs(path)

            file_name = os.path.split(url)[1]
            file_path = os.path.normpath(os.path.join(path, file_name))
            if os.path.exists(file_path):
                name, suffix = os.path.splitext(file_name)
                file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
                file_path = os.path.normpath(os.path.join(path, file_name))

            # 下载文件
            r = requests.get(url)
            with open(file_path, "wb") as code:
                code.write(r.content)

            from file_manager.models import File
            from utils import word_2_vadmin
            md5 = common.get_md5(file_path)
            obj = File.objects.filter(md5=md5).first()
            if obj:
                try:
                    os.remove(file_path)
                except (BaseException,):
                    pass
                file_path = obj.get_path()

            o_word = word_2_vadmin.generate(file_path)
            o_widget = widgets.Word(value=o_word)
        else:
            o_widget = widgets.Word()

        o_panel = widgets.Panel(vertical="top", width="100%", height="100%")
        o_panel.append(o_widget)
        result = step.WidgetLoad(data=o_panel)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, "error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_word_template(request):
    try:
        file_id = request.GET.get("file_id", "")
        o_panel = widgets.Panel(width=794, bg_color="#FFFFFF", min_height=1123)

        if file_id:
            from file_manager.models import File
            from utils import word_template_2_vadmin
            obj = File.objects.filter(pk=file_id).first()
            if obj:
                file_path = obj.get_path()
                param = dict(request.GET)
                del param["file_id"]
                obj.default_param = json.dumps(param, ensure_ascii=False)
                obj.save()

                o_panel = word_template_2_vadmin.generate(file_path, request.GET)

        o_page = widgets.Page(vertical="top", horizontal="center", width="100%",
                              height="100%", bg_color="#F2F4F7", scroll={"y": "auto"})
        url = "/v_word_template_save/?file_id=%s" % file_id
        o_page.add_event(event.Event(type="destroy", step=step.Post(url=url)))
        o_page.append(o_panel)
        result = step.WidgetLoad(data=o_page)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, "error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_word_template_save(request):
    """模板数据保存"""
    try:
        file_id = request.GET.get("file_id", "")
        from file_manager.models import File
        result = {}
        if file_id:
            obj = File.objects.filter(pk=file_id).first()
            if obj:
                content = request.POST.get(const.SUBMIT_WIDGET, None)
                if content:
                    obj.param = content
                    obj.save()
                    result = {"file_id": obj.pk}
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_word_info(request):
    """
    获取word数据
    1、获取使用模板保存后的填写数据
    2、获取使用填写数据生成的word文件
    """
    try:
        file_id = request.GET["file_id"]
        from file_manager.models import File
        from utils import word_template_2_word
        obj = File.objects.filter(pk=file_id).first()
        result = {}
        if obj:
            template_path = obj.get_path()
            param = obj.param or "{}"
            param = json.loads(param)
            now = datetime.datetime.now()
            path, file_name = os.path.split(template_path)
            name, suffix = os.path.splitext(file_name)
            name = name.split("-")[0]
            file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
            file_path = os.path.normpath(os.path.join(path, file_name))

            word_template_2_word.generate(template_path, file_path, param)
            lst_path = os.path.split(template_path)[0].split("/")

            file_url = os.path.normpath(os.path.join(settings.MEDIA_URL, lst_path[-2], lst_path[-1], file_name))
            result = {"param": param, "file_url": file_url}

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_get_word_url(request):
    """根据文件ID，获取修改后的文件"""
    try:
        file_id = request.GET["file_id"]
        from file_manager.models import File
        obj = File.objects.create(pk=file_id)
        result = obj.get_url()
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_generate_file_id(request):
    """生产word文件ID"""
    try:
        from file_manager.models import File
        url = request.GET.get("file_url", None)

        now = datetime.datetime.now()
        now_date = now.strftime("%Y-%m-%d")
        path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, "word", now_date))
        if not os.path.exists(path):
            os.makedirs(path)

        file_name = os.path.split(url)[1]
        file_path = os.path.normpath(os.path.join(path, file_name))
        if os.path.exists(file_path):
            name, suffix = os.path.splitext(file_name)
            file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
            file_path = os.path.normpath(os.path.join(path, file_name))

        # 下载文件
        r = requests.get(url)
        with open(file_path, "wb") as code:
            code.write(r.content)

        obj = File.objects.create(type=1, path=file_path)
        result = {"file_id": obj.pk}
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_export_word(request):
    try:
        lst_node = request.POST["lst_node"]
        lst_node = json.loads(lst_node)
        page = request.POST["page"]
        page = json.loads(page)

        from utils import vadmin_2_word
        now = datetime.datetime.now()
        now_date = now.strftime("%Y-%m-%d")
        path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, "word", now_date))
        if not os.path.exists(path):
            os.makedirs(path)

        file_name = page.get("file_name", "a") + ".docx"
        file_path = os.path.normpath(os.path.join(path, file_name))
        if os.path.exists(file_path):
            name, suffix = os.path.splitext(file_name)
            file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
            file_path = os.path.normpath(os.path.join(path, file_name))

        url = os.path.normpath(os.path.join(settings.MEDIA_URL, "word", now_date, file_name))
        vadmin_2_word.generate(file_path, page, lst_node)
        return HttpResponse(json.dumps(url, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_import_word(request):
    try:
        o_file = request.FILES["file"]
        now = datetime.datetime.now()
        now_date = now.strftime("%Y-%m-%d")
        path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, "word", now_date))
        if not os.path.exists(path):
            os.makedirs(path)

        file_name = o_file.name
        file_path = os.path.normpath(os.path.join(path, file_name))
        if os.path.exists(file_path):
            name, suffix = os.path.splitext(file_name)
            file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
            file_path = os.path.normpath(os.path.join(path, file_name))

        from utils import word_2_vadmin
        from utils import storage
        obj = storage.ImageStorage()
        obj._save(file_path, o_file)

        # from file_manager.models import File
        # md5 = common.get_md5(file_path)
        # obj = File.objects.filter(md5=md5).first()
        # if obj:
        #     o_word = pickle.load(open(obj.dump, "rb"))
        # else:
        #     o_word = word_2_vadmin.generate(file_path)
        #     name, suffix = os.path.splitext(file_path)
        #     dump_path = "%s.dump" % name
        #     pickle.dump(o_word, open(dump_path, "wb"), pickle.HIGHEST_PROTOCOL)
        #     File.objects.create(md5=md5, name=file_name, path=file_path, type=1, suffix=suffix, dump=dump_path)

        o_word = word_2_vadmin.generate(file_path)
        # pickle.dumps(o_word, pickle.HIGHEST_PROTOCOL)
        return HttpResponse(json.dumps(o_word, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_document_2_page(request):
    """文档显示"""
    try:
        from utils import word_2_vadmin
        path = request.GET["path"]
        suffix = os.path.splitext(path)[1].lower().strip()
        if suffix not in [".docx", ".pdf", ".jpg", '.jpeg', ".png", ".gif", ".bmp", ".svg"]:
            o_step = step.Msg(text="文档显示只支持*.docx, *.pdf文件！")
            return HttpResponse(json.dumps(o_step, ensure_ascii=False, cls=Encoder), content_type='application/json')

        script = request.GET.get(const.UPN_CALLBACK_SCRIPT, None)
        if script:
            lst_interface = script.split(".")
            o_module = importlib.import_module(".".join(lst_interface[0:-1]))
            fun = getattr(o_module, lst_interface[-1].strip("/\\"))

            o_step = fun(request)
            if isinstance(o_step, HttpResponse):
                return o_step

        else:
            o_page = widgets.Page(width="100%", horizontal="center")

            if suffix == ".pdf":
                from utils import vadmin_2_pdf
                if request.GET.get(const.UPN_PDF_2_IMAGE, None):
                    o_widget = vadmin_2_pdf.pdf_2_image(path, cache=True)
                else:
                    o_widget = widgets.Pdf(common.get_download_url(path))

            elif suffix == ".docx":
                if common.is_phone_terminal(request):
                    o_widget = word_2_vadmin.generate(path, show_width=request.GET.get("width", None),
                                                      padding=[6, 6, 6, 6], cache=True)
                else:
                    o_widget = word_2_vadmin.generate(path, show_width=request.GET.get("width", None),
                                                      cache=True)
            else:
                o_widget = widgets.Image(common.get_download_url(path))

            o_page.append(o_widget)
            o_step = step.WidgetLoad(o_page)
        return HttpResponse(json.dumps(o_step, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_save(request, app_label, model_name):
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model_admin = admin_api.get_model_admin(app_label, model_name)
        content = request.POST.get(const.SUBMIT_WIDGET, "[]")
        widget_data = json.loads(content)
        table_name = const.WN_TABLE % (app_label, model_name)
        row = widget_data.get(table_name, {})
        if isinstance(row, str):  # 有可能是弹出框选择单条数据
            return HttpResponse(json.dumps({}, ensure_ascii=False, cls=Encoder), content_type='application/json')
        else:
            save_data = row.get("row", [])
        with transaction.atomic():
            for row_data in save_data:
                row_id = row_data["row_id"]

                update_data = {}
                for k, v in row_data.items():
                    if row_id == "row_id":
                        continue

                    if hasattr(model_admin.model, k):
                        update_data[k] = v
                    elif hasattr(model_admin.model, "%s_id" % k):
                        update_data["%s_id" % k] = v

                if update_data:
                    model_admin.model.objects.filter(pk=row_id).update(**update_data)

        result = step.Msg(text="保存完成!", msg_type="success")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_export(request, app_label, model_name):
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model_admin = admin_api.get_model_admin(app_label, model_name)
        queryset = report.get_export_queryset(request, model_admin)
        if isinstance(queryset, QuerySet):
            count = queryset.count()
        else:
            count = len(queryset)

        if count > 65535:
            result = step.Msg("最大只能导出65535条记录！")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

        export_config = model_admin.get_export_config(request)
        if export_config.get("async", True):
            # 异步处理
            path, file_url = report.get_export_file_name(request, model_admin)

            o_thread = threading.Thread(target=report.export_excel,
                                        args=(request, model_admin, queryset, path))
            o_thread.start()

            url = common.make_url("v_list_export_async", param={"path": path, "file_url": file_url})
            result = step.RequestAsync(url=url)
        else:
            file_url = report.export_excel(request, model_admin, queryset)
            result = step.DownloadFile(href=file_url)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_export_async(request):
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        result = None
        path = request.GET["path"]
        file_url = request.GET["file_url"]
        if os.path.exists(path):
            result = step.DownloadFile(href=file_url)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


@gzip_page
def v_home(request):
    """所有访问入口"""
    try:
        result = admin_auth.check_login(request)
        if result:  # 未登录，跳转到登录页面
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        # 手机端

        content = request.POST.get(const.SUBMIT_HIDE, "{}")
        dict_hide = json.loads(content)

        result = []
        menu_id = request.GET.get(const.UPN_MENU_ID, None)
        if int(dict_hide.get(const.WN_CONTENT_HIDE, 0)) and menu_id:
            # 选择顶部，要更新左边
            o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
            o_page_template = o_module.Page(request, o_theme)
            if const.UPN_TOP_ID in request.GET:
                o_menu_left = o_page_template.create_left()
                if o_menu_left and o_menu_left.get_attr_value("data"):
                    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0",
                                                          "width": o_page_template.WIDTH_LEFT,
                                                          "children": [o_menu_left, ],
                                                          "scroll": {"y": "auto"}},
                                                    mode="all"))
                    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1",
                                                          "width": "100%%-%s" % o_page_template.WIDTH_LEFT,
                                                          "height": "100%"}))
                else:
                    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0",
                                                          "width": 0}))
                    result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|1",
                                                          "width": "100%",
                                                          "height": "100%"}))

                # 后可能是回退（要修改顶部菜单）
                result.append(step.WidgetUpdate(data={"name": const.WN_MENU_TOP,
                                                      "value": request.GET[const.UPN_TOP_ID]}))

            mode, param = menu_id.split(":", 1)
            if mode == "url":
                panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, url=param, margin=[0, 0, 0, 0],
                                      padding=[0, 0, 0, 0], width="100%", height="100%", vertical="top")
                result.append(step.WidgetUpdate(mode="all", data=panel))

            elif mode == "href":
                panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, href=param, margin=[0, 0, 0, 0],
                                      padding=[0, 0, 0, 0], width="100%",
                                      height="100vh-%s" % o_page_template.HEIGHT_TOP, vertical="top")
                result.append(step.WidgetUpdate(mode="all", data=panel))

            elif mode == "model":
                app_label, model_name = param.split(".")
                model_name = model_name.split("/")[0]
                o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
                o_content = o_module.ChangeList(request, app_label, model_name, o_theme).make_list_view()
                result.append(step.WidgetUpdate(data=o_content, mode="all"))

            elif mode == "id":
                mode2, param2 = menu.get_mode_param_by_id(settings.V_MENU_ITEMS, param)
                if mode2 == "url":
                    panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, url=param2, margin=[0, 0, 0, 0],
                                          padding=[0, 0, 0, 0], width="100%", height="100%")
                    result.append(step.WidgetUpdate(mode="all", data=panel))

                elif mode2 == "href":
                    panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, href=param2, margin=[0, 0, 0, 0],
                                          padding=[0, 0, 0, 0], width="100%",
                                          height="100vh-%s" % o_page_template.HEIGHT_TOP)
                    result.append(step.WidgetUpdate(mode="all", data=panel))

                elif mode2 == "model":
                    app_label, model_name = param2.split(".")
                    model_name = model_name.split("/")[0]
                    o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
                    o_content = o_module.ChangeList(request, app_label, model_name, o_theme).make_list_view()
                    result.append(step.WidgetUpdate(data=o_content, mode="all"))

        else:
            # 全量更新
            o_page = service.make_page(request, o_theme=o_theme)
            result = [step.WidgetLoad(data=o_page), step.AddHide(data={const.WN_CONTENT_HIDE: 1})]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_top(request):
    try:
        result = admin_auth.check_login(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        panel = o_module.Page(request, o_theme).create_top()
        result = step.WidgetLoad(data=panel)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


@gzip_page
def v_left(request):
    try:
        result = admin_auth.check_login(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        result = []
        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_left = o_module.Page(request, o_theme).create_left()
        if o_left:
            result.append(step.WidgetLoad(data=o_left))

        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_page_template = o_module.Page(request, o_theme)
        result.append(step.WidgetUpdate(data={"name": const.WN_CONTENT + "|0",
                                              "width": o_page_template.WIDTH_LEFT}))
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_right(request):
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        if const.UPN_MENU_ID in request.GET:

            # 通过菜单ID获取app_name和model_name
            menu_id = request.GET[const.UPN_MENU_ID]
            menu_type, menu_id = menu_id.split(":")
            if menu_type == "model":
                app_label, model_name = menu_id.split(".")
                o_template = importlib.import_module("vadmin.templates.%s" % o_theme.template)
                o_content = o_template.ChangeList(request, app_label, model_name, o_theme).make_list_view()
                result = step.WidgetLoad(data=o_content)
            elif menu_type == "url":
                result = step.Get(url=menu_id, jump=True)
            else:
                result = step.Get(href=menu_id, jump=True)
        else:
            content = widget_view.make_home_view(request, o_theme)
            result = step.WidgetLoad(data=content)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list(request, app_label, model_name):
    """
    change_list
    """
    try:

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        # o_response = cache_api.get_cache(request)
        # if o_response:
        #     return o_response

        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_panel = o_module.ChangeList(request, app_label, model_name, o_theme).make_list_view()
        result = service.refresh_page(request, o_panel)

        o_response = HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
        # cache_api.set_cache(request, o_response)
        return o_response

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_del_view(request, app_label, model_name):
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_del=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model_admin = admin_api.get_model_admin(app_label, model_name)
        o_theme = theme.get_theme(request.user.id)
        lst_obj_id = []
        if int(request.GET.get(const.WN_SELECT_ALL, 0) or 0):  # 全部(过滤后的）
            queryset = admin_api.get_filter_queryset(request, model_admin)
            # queryset = model_admin.get_queryset(request)
            search_name = const.WN_SEARCH % (app_label, model_name)
            search_term = request.GET.get(search_name, "")
            queryset, use_distinct = model_admin.get_search_results(request, queryset, search_term)
            count = queryset.count()
            max_number = 300
            if const.UPN_DEL_SECTION in request.GET:
                queryset = queryset[0:int(request.GET[const.UPN_DEL_SECTION])]
                o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
                o_grid = o_module.ChangeDel(request, model_admin, o_theme, lst_obj_id).make_del_view(queryset=queryset)

                result = service.refresh_page(request, o_grid)

            elif count > max_number:
                url = common.make_url(const.URL_LIST_DEL_VIEW % (app_label, model_name),
                                      request, {const.UPN_DEL_SECTION: max_number})
                o_step = step.Get(url=url)
                result = step_ex.ConfirmBox(title="删除", step=o_step,
                                            text="共%s条，最大只能删除%s条，是否删除前%s条？" % (count, max_number, max_number))
            else:
                o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
                o_grid = o_module.ChangeDel(request, model_admin, o_theme, lst_obj_id).make_del_view(
                    queryset=queryset)

                result = service.refresh_page(request, o_grid)

        else:
            table_name = const.WN_TABLE % (app_label, model_name)
            obj_id = request.GET.get(table_name, "")
            if obj_id:
                lst_obj_id = eval(obj_id)

            if lst_obj_id:
                o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
                o_grid = o_module.ChangeDel(request, model_admin, o_theme, lst_obj_id).make_del_view()
                result = service.refresh_page(request, o_grid)

            else:
                result = [step.Msg(text=_("Items must be selected in order to perform actions on them. No items have "
                                          "been changed."), msg_type="warning"),
                          step.ExitStep()]

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_del(request, app_label, model_name):
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_del=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model_admin = admin_api.get_model_admin(app_label, model_name)
        object_id = request.GET.get('id', "[]")
        if object_id:
            try:
                object_id = eval(object_id)
            except (BaseException,):
                pass
        else:
            object_id = []

        if int(request.GET.get(const.WN_SELECT_ALL, 0) or 0):  # 全部
            common.make_request_url(request, filter=["id"])
            queryset = admin_api.get_filter_queryset(request, model_admin)

            if const.UPN_DEL_SECTION in request.GET:
                queryset = queryset[0:int(request.GET[const.UPN_DEL_SECTION])]

        elif object_id:
            if isinstance(object_id, (tuple, list)):
                queryset = model_admin.model.objects.filter(pk__in=object_id)
            else:
                queryset = model_admin.model.objects.filter(pk=object_id)
        else:
            queryset = []

        v_change_list = model_admin.get_change_list_url(request)
        p_name = const.WN_PAGINATION % model_name
        url = common.make_url(v_change_list, request, filter=["id", const.WN_SELECT_ALL, p_name])

        if queryset:
            with transaction.atomic():
                for obj in queryset:
                    if (auth.get_user_model() == model_admin.model) and (obj.pk == request.user.pk):  # 等于自已不能删除
                        result = [step.Post(url=url, jump=True), step.Msg(text="不能删除登录用户!", msg_type="warning")]
                        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                            content_type="application/json")
                    if settings.V_OPERATION_LOG:
                        operation_log_add(request, app_label, model_name, 2, obj)
                    model_admin.delete_model(request, obj)

        result = [step.Post(url=url, jump=True), step.Msg(text="删除完成!", msg_type="success")]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_opera(request, app_label, model_name, action_name):
    """
    列表操作
    :param request:
    :param app_label:
    :param model_name:
    :param action_name:
    :return:
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_edit=True, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)
        content = request.POST.get(const.SUBMIT_OPERA, "[]")
        opera_data = json.loads(content)
        model_admin = admin_api.get_model_admin(app_label, model_name)

        msg = "未找到对应接口！"
        if int(widget_data.get(const.WN_SELECT_ALL, 0) or 0):
            # 按过滤条件查询
            queryset = model_admin.get_queryset(request)
            queryset, use_distinct = model_admin.get_search_results(request, queryset, dict_filter=widget_data)
        else:
            lst_object_id = admin_api.get_opera_data(opera_data, const.TABLE_ROW_OPERA)
            queryset = model_admin.model.objects.filter(pk__in=lst_object_id)

        action = admin_api.get_action(model_admin, action_name)
        if action is None:
            dict_resp = {"step": step.Msg(msg)}
        else:
            if queryset.count() == 0:
                msg = _("Items must be selected in order to perform actions on them. No items have "
                        "been changed.")
                dict_resp = {"step": step.Msg(msg)}
            else:
                v_change_list = model_admin.get_v_change_list(request)
                url = admin_api.make_url_by_para(v_change_list, widget_data,
                                                 lst_not_para=["change_list_select_all", ])
                msg = action(model_admin, request, queryset)
                if msg is None:  # 兼容django模式
                    if request._messages._queued_messages:
                        msg = str(request._messages._queued_messages[-1])
                        dict_resp = {"step": [step.Post(url=url, jump=True), step.Msg(msg)]}
                elif isinstance(msg, step.Step):
                    dict_resp = {"step": msg}
                elif isinstance(msg, (str,)):
                    dict_resp = {"step": [step.Post(url=url, jump=True), step.Msg(msg)]}
                else:
                    dict_resp = {"step": [step.Post(url=url, jump=True), msg]}

        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_order(request, app_label, model_name):
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        prev_id = request.GET.get(const.UPN_PREV_ID, "")
        next_id = request.GET.get(const.UPN_NEXT_ID, "")
        order_id = request.GET.get(const.UPN_ORDER_ID, "")

        if (prev_id == "") and (next_id == ""):
            result = step.Msg(text="一条记录，无须排序。 ")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if prev_id:
            try:
                if int(prev_id) < 0:
                    result = step.Msg(text="有未保存数据，无法排序。 ", msg_type="warning")
                    response = HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                            content_type="application/json")
                    return response
            except (BaseException,):
                pass

        if order_id:
            try:
                if int(order_id) < 0:
                    result = step.Msg(text="有未保存数据，无法排序。 ", msg_type="warning")
                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")
            except (BaseException,):
                pass

        if next_id:
            try:
                if int(next_id) < 0:
                    result = step.Msg(text="有未保存数据，无法排序。 ", msg_type="warning")
                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")
            except (BaseException,):
                pass

        model_admin = admin_api.get_model_admin(app_label, model_name)
        if model_admin is None:
            model = admin_api.get_model(app_label, model_name)
            queryset = model.objects.all()
            ordering = model._meta.ordering
        else:
            model = model_admin.model
            queryset = model_admin.get_queryset(request)
            ordering = None
            if model_admin.ordering:
                ordering = model_admin.ordering
                # queryset = queryset.order_by(*ordering)  # 使用model_admin配置排序
            elif model_admin.model._meta.ordering:
                ordering = model_admin.model._meta.ordering

        if not ordering:
            result = step.Msg(text="没有配置ordering，无法排序!", msg_type="warning")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if ("order" not in ordering) and ("-order" not in ordering):
            result = step.Msg(text="ordering中必须定义order字段!", msg_type="warning")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

        db_field = model._meta.get_field("order")
        if db_field.default != 2147483647:
            result = step.Msg(text="order字段default属性必须等于2147483647!", msg_type="warning")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

        is_int = True
        db_field = model._meta.pk
        if isinstance(db_field, (models.CharField,)):
            is_int = False
            if (len(ordering) == 1) or (ordering[1] not in ["create_time", "-create_time"]):
                result = step.Msg(text="主键为字符串类型时，"
                                       "ordering中必须定义create_time字段, 且create_time字段必须定义auto_now_add属性!",
                                  msg_type="error")
                return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                    content_type="application/json")

        try:
            db_field = model._meta.get_field("create_time")
        except (BaseException,):
            result = step.Msg(text="model中必须定义create_time字段!", msg_type="warning")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

        if not db_field.auto_now_add:
            result = step.Msg(text="create_time字段auto_now_add属性必须等于True!", msg_type="warning")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

        queryset = queryset.order_by(*ordering)  # 使用model配置排序
        if "order" in ordering:
            direction = 1
        else:
            direction = 0

        obj = model.objects.get(pk=order_id)
        with transaction.atomic():
            if prev_id in ["", None]:  # 最上面
                if direction == 1:  # 升序
                    min_value = queryset.aggregate(Min('order'))["order__min"]
                    queryset.update(order=F("order") - 1)
                    obj.order = min_value - 2
                    obj.save()

                else:
                    max_value = queryset.aggregate(Max('order'))["order__max"]
                    if max_value == 2147483647:
                        queryset.update(order=F("order") - 1)

                    obj.order = 2147483647
                    obj.save()

            elif next_id in ["", None]:  # 最下面
                if direction == 1:  # 升序
                    max_value = queryset.aggregate(Max('order'))["order__max"]
                    if max_value == 2147483647:
                        queryset.update(order=F("order") - 1)
                    obj.order = 2147483647
                    obj.save()
                else:
                    min_value = queryset.aggregate(Min('order'))["order__min"]
                    queryset.update(order=F("order") - 1)
                    obj.order = min_value - 2
                    obj.save()

            else:
                obj_prev = queryset.get(pk=prev_id)
                obj_next = queryset.get(pk=next_id)

                if direction == 1:  # 升序
                    if is_int:
                        sub = queryset.filter(order__lte=obj_prev.order).filter(pk__lte=obj_prev.pk)
                        max_value = sub.aggregate(Max('order'))["order__max"]
                        sub.update(order=F("order") - 3)
                        obj.order = max_value - 2
                        obj.save()
                        obj_next.order = max_value - 1
                        obj_next.save()
                    else:
                        sub = queryset.filter(order__lte=obj_prev.order)
                        # if "create_time" in ordering:
                        #     sub = sub.filter(create_time__lte=obj_prev.create_time)
                        # else:
                        #     sub = sub.filter(create_time__gte=obj_prev.create_time)
                        max_value = sub.aggregate(Max('order'))["order__max"]
                        sub.update(order=F("order") - 3)
                        obj.order = max_value - 2
                        obj.save()
                        obj_next.order = max_value - 1
                        obj_next.save()
                else:
                    if is_int:
                        sub = queryset.filter(order__lte=obj_next.order).filter(pk__lte=obj_next.pk)
                        max_value = sub.aggregate(Max('order'))["order__max"]
                        sub.update(order=F("order") - 3)
                        obj.order = max_value - 2
                        obj.save()
                        obj_prev.order = max_value - 1
                        obj_prev.save()
                    else:
                        sub = queryset.filter(order__lte=obj_next.order)
                        # if "create_time" in ordering:
                        #     sub = sub.filter(create_time__gte=obj_next.create_time)
                        # else:
                        #     sub = sub.filter(create_time__lte=obj_next.create_time)
                        max_value = sub.aggregate(Max('order'))["order__max"]
                        sub.update(order=F("order") - 3)
                        obj.order = max_value - 2
                        obj.save()
                        obj_prev.order = max_value - 1
                        obj_prev.save()

        result = step.Msg(text="排序已修改。 ")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_popup(request, app_label, model_name):
    """
    列表弹出
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        object_id = request.GET.get(const.UPN_OBJECT_ID, None)
        related_field_name = request.GET[const.UPN_RELATED_FIELD]
        related_app_label = request.GET[const.UPN_RELATED_APP]
        related_model_name = request.GET[const.UPN_RELATED_MODEL]
        related_id = request.GET.get(const.UPN_RELATED_ID, None)
        model_admin = admin_api.get_model_admin(app_label, model_name)
        related_model_admin = admin_api.get_model_admin(related_app_label, related_model_name)

        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_change_list = o_module.ChangeList(request, app_label, model_name, o_theme)
        o_change_list.related_model_admin = related_model_admin

        queryset = admin_api.get_filter_queryset(request, model_admin)
        db_field = admin_api.get_field(related_model_admin, related_field_name.split("|")[-1])

        field = None
        if db_field.to_fields and db_field.to_fields[0]:
            field = db_field.to_fields[0]

        if field is None:
            field = "pk"

        # if object_id:
        #     obj = model_admin.model.objects.filter(**{field: object_id}).first()
        # else:
        #     obj = None

        if related_id:
            related_obj = related_model_admin.model.objects.filter(pk=related_id).first()
        else:
            related_obj = None

        queryset = related_model_admin.foreign_key_filter(request, queryset, db_field, related_obj)
        o_panel = o_change_list.make_list_view(queryset, object_id, field)
        display_mode = request.GET.get(const.UPN_DISPLAY_MODE, None)
        if display_mode:
            o_panel.height = "100%"

        result = step.LayerPopup(data=o_panel, esc_close=True, mask=True, width="90%",
                                 height="90%", bg_color=o_theme.bg_color)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_filter(request, app_label, model_name):
    """
    弹出列表过滤
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        result = service.change_list_update(request, app_label, model_name)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_select_close(request, app_label, model_name):
    """
    列表弹出单选
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_add=True, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        related_field = request.GET.get(const.UPN_RELATED_FIELD, None)
        widget_id = request.GET.get(const.UPN_WIDGET_ID, None)
        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)

        table_name = const.WN_TABLE % (app_label, model_name)
        table_value = widget_data.get(table_name, "")
        field_value = widget_data[related_field]
        result = [step.LayerClose()]

        # 规避界面提交错误
        if isinstance(table_value, dict):
            if "value" in table_value:
                if isinstance(table_value["value"], list):
                    if table_value["value"]:
                        table_value = table_value["value"][0]
                    # else:
                    #     result = step.Msg(text="请选择数据！", msg_type="warning")
                    #     return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                    #                         content_type="application/json")
                else:
                    table_value = table_value["value"]

        if table_value != field_value:
            related_app_label = request.GET[const.UPN_RELATED_APP]
            related_model_name = request.GET[const.UPN_RELATED_MODEL]
            related_model_admin = admin_api.get_model_admin(related_app_label, related_model_name)
            db_field = admin_api.get_field(related_model_admin, related_field.split("|")[-1])

            # query_foreign_key_data接口obj暂时不处理
            data = field_translate.query_foreign_key_data(request, related_model_admin, db_field, None,
                                                          table_value)
            o_step = step.WidgetUpdate(data=widgets.Select(id=widget_id, name=related_field, data=data,
                                                           value="" if table_value is None else table_value))
            result.append(o_step)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_delete_close(request, app_label, model_name):
    """弹出提示框删除"""
    try:
        object_id = request.GET['id']
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = model_admin.get_object(request, object_id)
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_edit=True, obj=obj, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        if (auth.get_user_model() == model_admin.model) and (obj.pk == request.user.pk):  # 等于自已不能删除
            result = step.Msg(text="不能删除登录用户!", msg_type="warning")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
        #
        with transaction.atomic():
            if settings.V_OPERATION_LOG:
                from vadmin_standard import service as vadmin_standard_service
                vadmin_standard_service.operation_log_add(request,
                                                          model_admin.opts.app_label, model_admin.opts.model_name,
                                                          2, obj)
            model_admin.delete_model(request, obj)

        # 跟新表格子表格
        result = []
        o_step = service.change_list_update(request, app_label, model_name)
        result.append(o_step)
        result.append(step.LayerClose())
        result.append(step.Msg(text="删除完成!", msg_type="success"))

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_add(request, app_label, model_name):
    """
    增加单条记录
    """
    try:
        object_id = request.GET.get('id', None)
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = None
        if object_id is not None:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_add=True, is_auth=True, obj=obj)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)

        if object_id is not None:
            o_form = o_module.ChangeForm(request, model_admin, o_theme, obj, is_copy=True).make_form_view()
        else:
            o_form = o_module.ChangeForm(request, model_admin, o_theme).make_form_view()

        result = service.refresh_page(request, o_form)
        change_fields = model_admin.get_change_form_change_fields(request, obj)
        for field_name in change_fields:
            if obj:
                value = getattr(obj, field_name)
            else:
                value = None

            db_field = admin_api.get_field(model_admin, field_name)
            lst_step = model_admin.select_change(request, db_field, value, obj, False)
            if isinstance(lst_step, (list, tuple)):
                result.extend(lst_step)
            else:
                result.append(lst_step)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


@gzip_page
def v_form(request, app_label, model_name):
    """
    表单请求
    """
    try:
        object_id = request.GET.get('id', None)
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = None
        if object_id is not None:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_auth=True, obj=obj)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        user_agent = request.META["HTTP_USER_AGENT"].lower()
        if ("android" in user_agent) or ("iphone" in user_agent):
            # o_module = importlib.import_module("vadmin.templates.style_phone")
            # o_style = o_module.ChangeListStyle(request, model_admin, o_theme, page_index)
            o_grid = None
        else:
            o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
            o_grid = o_module.ChangeForm(request, model_admin, o_theme, obj).make_form_view()
            if "readonly" in request.GET and request.GET["readonly"]:
                o_grid.readonly = True

        result = service.refresh_page(request, o_grid)
        change_fields = model_admin.get_change_form_change_fields(request, obj)
        for field_name in change_fields:
            if obj:
                value = getattr(obj, field_name)
            else:
                value = None

            db_field = admin_api.get_field(model_admin, field_name)
            lst_step = model_admin.select_change(request, db_field, value, obj, False)
            if lst_step:
                if isinstance(lst_step, (list, tuple)):
                    result.extend(lst_step)
                else:
                    result.append(lst_step)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_popup(request, app_label, model_name):
    """
    表单弹出显示, 有保存和关闭，关联
    """
    try:
        object_id = request.GET.get('object_id', None)
        if object_id in [None, ""]:
            result = step.Msg(text="无数据，无法编辑!")
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model_admin = admin_api.get_model_admin(app_label, model_name)
        if const.UPN_RELATED_TO_FIELD in request.GET:
            to_field = request.GET[const.UPN_RELATED_TO_FIELD]
            obj = model_admin.model.objects.filter(**{to_field: object_id}).first()
        else:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_auth=True, obj=obj)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        o_grid = service.change_form(request, app_label, model_name, const.DM_FORM_LINK, object_id)

        result = step.LayerPopup(data=o_grid, esc_close=True, move=True, mask=True,
                                 bg_color=o_theme.bg_color, width="90%", height="90%")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_child_popup(request, app_label, model_name):
    """
    表单弹出显示, 有保存和关闭，子表
    """
    try:
        object_id = request.GET.get("id", None)
        obj = None
        model_admin = admin_api.get_model_admin(app_label, model_name)
        if object_id:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_auth=True, obj=obj)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        o_grid = service.change_form(request, app_label, model_name, const.DM_FORM_POPUP)
        result = step.LayerPopup(data=o_grid, top=60, esc_close=True, move=True, mask=True,
                                 bg_color=o_theme.bg_color, width="90%", max_height="90%")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_save(request, app_label, model_name):
    try:
        object_id = request.GET.get('id', None)
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = None
        if object_id not in ["", None]:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_edit=True, obj=obj, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)

        inline_data = service.parse_inline_data(request, model_admin, widget_data)
        obj, dict_error, msg = service.change_form_save(request, model_admin, obj, widget_data, inline_data)
        if dict_error or msg:
            if isinstance(msg, step.Step):
                result = msg
            else:
                result = step.OperaFailed(data=dict_error, msg=msg)

        else:
            o_step_msg = step.Msg(text='记录"%s"保存成功！' % str(obj), msg_type="success")
            if request.GET.get(const.UPN_STEPS_IDX, None):
                steps = model_admin.get_steps(request, obj)
                steps_num = len(steps)
                steps_idx = int(request.GET[const.UPN_STEPS_IDX])
                if steps_idx == steps_num:
                    url = model_admin.get_change_list_url(request, obj=obj)
                else:
                    url = model_admin.get_change_form_url(request, obj)
                    url = common.make_url(url, request,
                                          filter=[const.UPN_TOP_ID, const.UPN_SCREEN_WIDTH, const.UPN_SCREEN_HEIGHT])
                # o_step = step.Post(url=url, jump=True, section=lst_filter_name)
            elif request.GET.get(const.UPN_REDIRECT_URL, None):
                url = request.GET[const.UPN_REDIRECT_URL]
            else:
                url = model_admin.get_change_list_url(request, obj=obj)

            result = [step.Post(url=url, jump=True), o_step_msg]

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_save_edit(request, app_label, model_name):
    try:
        object_id = request.GET.get('id', None)
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = None
        if object_id not in ["", None]:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_edit=True, obj=obj, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        display_mode = request.GET.get(const.UPN_DISPLAY_MODE, None)
        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)
        inline_data = service.parse_inline_data(request, model_admin, widget_data)
        obj_new, dict_error, msg = service.change_form_save(request, model_admin, obj, widget_data, inline_data)
        change_fields = model_admin.get_change_form_change_fields(request, obj)
        lst_change_step = []
        for field_name in change_fields:
            if obj_new:
                value = getattr(obj_new, field_name)
            else:
                value = None

            db_field = admin_api.get_field(model_admin, field_name)
            lst_step = model_admin.select_change(request, db_field, value, obj_new, False)
            if isinstance(lst_step, (list, tuple)):
                lst_change_step.extend(lst_step)
            else:
                lst_change_step.append(lst_step)

        if dict_error or msg:
            if isinstance(msg, step.Step):
                result = msg
            else:
                result = step.OperaFailed(data=dict_error, msg=msg)

        elif display_mode == const.DM_FORM_POPUP:
            o_step_msg = step.Msg(text='记录"%s"保存成功！' % str(obj_new), msg_type="success")
            o_grid = service.change_form(request, app_label, model_name, const.DM_FORM_POPUP, obj_new.pk)
            o_step = service.change_list_update(request, app_label, model_name, display_mode=const.DM_LIST_CHILD)
            result = [o_step, step.WidgetUpdate(data=o_grid, mode="all"), o_step_msg]
            result.extend(lst_change_step)

        elif display_mode == const.DM_FORM_LINK:
            o_step_msg = step.Msg(text='记录"%s"保存成功！' % str(obj_new), msg_type="success")
            o_grid = service.change_form(request, app_label, model_name, const.DM_FORM_LINK, obj_new.pk)
            result = [step.WidgetUpdate(data=o_grid, mode="all"), o_step_msg]
            result.extend(lst_change_step)

        else:
            o_step_msg = step.Msg(text='记录"%s"保存成功！' % str(obj_new), msg_type="success")
            v_change_form = model_admin.get_change_form_url(request, obj_new)
            url = common.make_url(v_change_form, request, param={"id": obj_new.pk})
            if (obj is not None) and ("v_form/" in url):  # 如果是标准流程直接修改
                # o_theme = theme.get_theme(request.user.pk)
                # o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
                # o_grid = o_module.ChangeForm(request, model_admin, o_theme, obj_new).make_form_view()
                o_grid = service.change_form(request, app_label, model_name, object_id=obj_new.pk)
                result = [o_step_msg, step.WidgetUpdate(data=o_grid, mode="all")]
                result.extend(lst_change_step)

            else:
                result = [o_step_msg, step.Get(url=url, jump=True)]

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_save_close(request, app_label, model_name):
    try:
        object_id = request.GET.get('id', None)

        display_mode = request.GET.get(const.UPN_DISPLAY_MODE, None)
        obj = None
        model_admin = admin_api.get_model_admin(app_label, model_name)
        if object_id not in ["", None]:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_edit=True, obj=obj, is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)
        inline_data = service.parse_inline_data(request, model_admin, widget_data)
        obj_new, dict_error, msg = service.change_form_save(request, model_admin, obj, widget_data, inline_data)
        if dict_error or msg:
            if isinstance(msg, step.Step):
                result = msg
            else:
                result = step.OperaFailed(data=dict_error, msg=msg)

        elif display_mode == const.DM_FORM_LINK:
            # 要获取关联的字段，修改显示值
            o_step_msg = step.Msg(text='记录"%s"保存成功！' % str(obj_new), msg_type="success")
            result = [o_step_msg, step.LayerClose()]

            if str(obj) != str(obj_new):  # 显示的名称已修改，要更新
                related_app_label = request.GET[const.UPN_RELATED_APP]
                related_model_name = request.GET[const.UPN_RELATED_MODEL]
                related_model_admin = admin_api.get_model_admin(related_app_label, related_model_name)
                related_field = request.GET[const.UPN_RELATED_FIELD]
                db_field = admin_api.get_field(related_model_admin, related_field)
                data = field_translate.query_foreign_key_data(request, related_model_admin, db_field, None,
                                                              request.GET[const.UPN_RELATED_ID])
                o_step = step.WidgetUpdate(data=widgets.Select(name=related_field, data=data, value=object_id),
                                           mode="all")
                result.append(o_step)

        elif display_mode == const.DM_FORM_POPUP:
            # 跟新表格子表格
            o_step = service.change_list_update(request, app_label, model_name, display_mode=const.DM_LIST_CHILD)
            result = [o_step, step.LayerClose()]

        else:
            # 跟新列表
            # result = service.change_list_update(request, app_label, model_name, related_app_label, related_model_name)
            # result.append(step.LayerClose())
            pass

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


#
# def v_form_close(request, app_label, model_name):
#     try:
#         object_id = request.GET.get('id', None)
#         parent_id = eval(request.GET.get(const.PARENT_ID, "None"))
#         related_field_name = request.GET.get(const.RELATED_FIELD_NAME, None)
#         if related_field_name == "None":
#             related_field_name = None
#
#         model_admin = admin_api.get_model_admin(app_label, model_name)
#
#         content = request.POST.get(const.SUBMIT_WIDGET, "{}")
#         widget_data = json.loads(content)
#
#         dict_error = dict()
#         service.fields_check(request, model_admin, widget_data, dict_error, None)
#         result = None
#         if dict_error:
#             msg = "请修正下面的错误。 "
#             o_step_msg = step.Msg(msg, theme="error")
#             o_step_error = step.WidgetOperaError(dict_error)
#             lst_step = step.make_step(o_step_msg, o_step_error)
#             result = lst_step
#         else:
#             o_theme = theme.get_theme(request.user.id)
#             o_module = importlib.import_module("vadmin.templates.%s" % o_theme.style)
#             o_template = o_module.ChangeListStyle(request, model_admin, o_theme)
#             o_template.is_child = True
#             o_template.related_field_name = related_field_name
#             if object_id:
#                 obj = model_admin.model.objects.filter(pk=object_id).first()
#                 for k, v in widget_data.items():
#                     setattr(obj, k, v)
#                 obj.save()
#                 data = o_template.make_change_list_row(obj)
#                 row_id = object_id
#             elif parent_id:
#                 widget_data[related_field_name] = parent_id
#                 obj = model_admin.model(**widget_data)
#                 obj.save()
#                 data = o_template.make_change_list_row(obj)
#                 row_id = obj.pk
#             else:
#                 obj = model_admin.model(**widget_data)
#                 now = datetime.datetime.now()
#                 row_id = "%s%s%s" % (now.minute, now.second, now.microsecond)
#                 row_id = -1 * int(row_id)
#                 obj.pk = row_id
#                 data = o_template.make_change_list_row(obj)
#
#             o_step = step.TableOpera(name=const.WIDGET_TABLE_NAME % (app_label, model_name), data=data, row_id=row_id)
#             result = [o_step, step.GridClose()]
#
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#     except (BaseException,):
#         result = admin_auth.save_error(request)
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_save_add(request, app_label, model_name):
    try:
        object_id = request.GET.get('id', None)
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = None
        if object_id not in ["", None]:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_edit=True, is_add=True, obj=obj,
                                             is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)

        model_admin = admin_api.get_model_admin(app_label, model_name)
        inline_data = service.parse_inline_data(request, model_admin, widget_data)
        obj, dict_error, msg = service.change_form_save(request, model_admin, obj, widget_data, inline_data)

        if dict_error or msg:
            if isinstance(msg, step.Step):
                result = msg
            else:
                result = step.OperaFailed(data=dict_error, msg=msg)

        else:
            o_step_msg = step.Msg(text='记录"%s"保存成功！' % str(obj), msg_type="success")
            url = const.URL_FORM_ADD % (app_label, model_name)
            url = common.make_url(url, request, filter=["id", ])
            result = [step.Post(url=url, jump=True), o_step_msg]

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_save_copy_add(request, app_label, model_name):
    try:
        object_id = request.GET.get('id', None)
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = None
        if object_id not in ["", None]:
            obj = model_admin.get_object(request, object_id)

        result = admin_auth.check_opera_auth(request, app_label, model_name, is_edit=True, is_add=True, obj=obj,
                                             is_auth=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)

        model_admin = admin_api.get_model_admin(app_label, model_name)
        inline_data = service.parse_inline_data(request, model_admin, widget_data)
        obj, dict_error, msg = service.change_form_save(request, model_admin, obj, widget_data, inline_data)
        if dict_error or msg:
            if isinstance(msg, step.Step):
                result = msg
            else:
                result = step.OperaFailed(data=dict_error, msg=msg)
        else:
            o_step_msg = step.Msg(text='记录"%s"保存成功！' % str(obj), msg_type="success")
            url = const.URL_FORM_COPY_ADD % (app_label, model_name, obj.pk)
            url = common.make_url(url, request)
            result = [step.Post(url=url, jump=True), o_step_msg]

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_del_view(request, app_label, model_name):
    """
    删除显示页面
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_del=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model_admin = admin_api.get_model_admin(app_label, model_name)
        object_id = request.GET['id']
        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_grid = o_module.ChangeDel(request, model_admin, o_theme, [object_id, ]).make_del_view()
        result = service.refresh_page(request, o_grid)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_form_field_change(request, app_label, model_name, field_name):
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_del=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        model_admin = admin_api.get_model_admin(app_label, model_name)
        object_id = request.GET.get('id', None)
        value = request.GET['value']
        if object_id in [None, ""]:
            obj = None
        else:
            obj = model_admin.model.objects.filter(pk=object_id).first()

        db_field = field_name
        try:
            db_field = admin_api.get_field(model_admin, field_name)
            if isinstance(db_field.choices[0][0], int):
                value = int(value)
        except (BaseException,):
            pass
        result = model_admin.select_change(request, db_field, value, obj)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_row_save(request, app_label, model_name):
    """
    表格行保存
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_del=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_OPERA, "{}")
        opera_data = json.loads(content)

        model_admin = admin_api.get_model_admin(app_label, model_name)
        with transaction.atomic():
            row_id = opera_data['data']['row_id']
            row_data = opera_data['data']['row_data']
            obj = model_admin.get_object(request, row_id)
            if obj:
                for k, v in row_data.items():
                    setattr(obj, k, v)

                obj.save()
                result = step.Msg(text="保存成功!", msg_type="success")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_list_tree_load(request, app_label, model_name, parent_field):
    """
    加载树表格
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_del=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        object_id = request.GET["id"]
        model_admin = admin_api.get_model_admin(app_label, model_name)
        o_theme = theme.get_theme(request.user.pk)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_template = o_module.ChangeList(request, app_label, model_name, o_theme)
        filter = {parent_field: object_id}

        result = []
        for sub_obj in model_admin.model.objects.filter(**filter):
            sub_row_data = o_template.make_list_row(sub_obj)
            sub_filter = {parent_field: sub_obj.pk}
            if model_admin.model.objects.filter(**sub_filter).exists():
                sub_item = {"id": sub_obj.pk, "row": sub_row_data}
            else:
                sub_item = {"id": sub_obj.pk, "row": sub_row_data, "children": []}
            result.append(sub_item)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_inline_del(request, app_label, model_name, related_app_label, related_model_name):
    """
    子列表删除请求
    """
    try:
        result = admin_auth.check_opera_auth(request, app_label, model_name, is_del=True)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_OPERA, "{}")
        opera_data = json.loads(content)

        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj_inline = admin_api.get_model_admin(related_app_label, related_model_name)
        with transaction.atomic():
            object_id = opera_data['data']['row_id']

            msg = model_admin.delete_inline(request, obj_inline, [object_id, ])
            if msg is None:
                result = step.Msg(text="删除完成!", msg_type="success")
            else:
                result = [step.Msg(text=msg, msg_type="error"), step.OperaFailed()]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_tree_opera(request, app_label, model_name, field_name):
    """
    树组件操作
    """
    try:
        if not request.user.is_authenticated:
            return HttpResponse(json.dumps([], ensure_ascii=False, cls=Encoder), content_type="application/json")

        content = request.POST.get(const.SUBMIT_OPERA, "[]")
        opera_data = json.loads(content)
        model_admin = admin_api.get_model_admin(app_label, model_name)

        result = None
        with transaction.atomic():
            if opera_data["opera"] == const.OPERA_TREE_NODE_ADD:
                result = service.tree_node_add(request, model_admin, field_name, opera_data)

            elif opera_data["opera"] == const.OPERA_TREE_NODE_DEL:
                result = service.tree_node_del(request, model_admin, field_name, opera_data)

            elif opera_data["opera"] == const.OPERA_TREE_NODE_UPDATE:
                result = service.tree_node_update(request, model_admin, field_name, opera_data)

            elif opera_data["opera"] == const.OPERA_TREE_NODE_ORDER:
                pass

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


def v_run_script(request, script):
    try:
        # result = service.check_login(request)
        # if result:
        #     return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        lst_interface = script.split(".")
        o_module = importlib.import_module(".".join(lst_interface[0:-1]))
        fun = getattr(o_module, lst_interface[-1].strip("/\\"))

        # with transaction.atomic():
        result = fun(request)
        if isinstance(result, HttpResponse):
            return result

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')
