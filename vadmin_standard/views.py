# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111
import datetime
import json
import logging
import os
import traceback
import zipfile
import importlib

from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import redirect

from timed_task import task
from utils import calc_time
from vadmin import admin_api
from vadmin import const
from vadmin import event
from vadmin import step
from vadmin import theme
from vadmin import widgets
from vadmin.json_encoder import Encoder
from vadmin_standard import api
from vadmin_standard import service
from vadmin_standard.models import Api
from vadmin_standard.models import AppVersion
from vadmin_standard.models import DataDump
from vadmin_standard.models import ErrorLog
from vadmin_standard.models import DBDataLog
from vadmin_standard.models import VersionPatch

logger = logging.getLogger(__name__)


def api_view(request):
    try:
        module_name = request.GET.get("module-name", None)
        search = request.GET.get("search", None)
        o_theme = theme.get_theme(request.user.pk)
        lst_api = Api.objects.filter(del_flag=False)
        dict_module = {}
        for obj in lst_api:
            dict_module.setdefault(obj.module, []).append(obj)

        o_grid = widgets.Grid(col_num=2, bg={"color": "#ECF7F2"}, vertical="top",
                              height="100vh", scroll={"y": "auto"})
        o_grid.set_col_attr(col=0, width=300)
        o_grid.set_col_attr(col=1, horizontal="center", vertical="top")

        url = const.URL_RUN_SCRIPT % "vadmin_standard.views.api_view"
        o_step = step.Get(url=url, splice="search")
        o_icon = widgets.Icon(icon="el-icon-search", font={"size": 24, "color": "#64B1F0"}, step=o_step)
        o_widget = widgets.Input(name="search", width="100%", placeholder="请输入接口名称、接口说明",
                                 height=40, bg_color="#FFFFFF", suffix=o_icon, value=search)
        o_event = event.Event(type="keydown", param=[13, 108], step=o_step)
        o_widget.add_event(o_event)
        o_grid.append(o_widget, col=0)
        menu_data = []
        for k, v in dict_module.items():
            if module_name is None:
                module_name = k  # 默认第一个
            url = const.URL_RUN_SCRIPT % "vadmin_standard.views.api_view" + ("/?module-name=%s" % k)
            menu_data.append({"label": k, "url": url, "id": k})

        if search:
            value = None
        else:
            value = module_name
        o_menu = widgets.Menu(data=menu_data, width="100%", height="100%-40",
                              value=value, bg_color=o_theme.bg_color)

        o_grid.append(o_menu, col=0)
        o_grid.append(widgets.Row(30))
        o_grid.append(service.api_module(request, module_name))
        o_page = widgets.Page()
        o_page.append(o_grid)
        o_step = step.WidgetLoad(data=o_page)
        return HttpResponse(json.dumps(o_step, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, msg_type="error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


@api.register("GET测试", "GET", [
    {"name": "str", "desc": "字符串", "type": "str", "required": True},
    {"name": "int", "desc": "整数", "type": "int", "required": True},
    {"name": "float", "desc": "浮点数", "type": "float", "required": True},
    {"name": "password", "desc": "密码", "type": "password", "required": True},
    {"name": "date", "desc": "日期", "type": "date", "required": True},
    {"name": "time", "desc": "时间", "type": "time", "required": True},
    {"name": "datetime", "desc": "日期时间", "type": "datetime", "required": True},
], "输入数据直接返回")
def api_get_test(request):
    try:
        s = request.GET.get("str", None)
        i = request.GET.get("int", None)
        f = request.GET.get("float", None)
        p = request.GET.get("password", None)
        d = request.GET.get("date", None)
        t = request.GET.get("time", None)
        dt = request.GET.get("datetime", None)

        return HttpResponse(json.dumps(request.GET, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, msg_type="error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


@api.register("POST测试", "POST", [
    {"name": "str", "desc": "字符串", "type": "str", "required": True},
    {"name": "int", "desc": "整数", "type": "int", "required": True},
    {"name": "float", "desc": "浮点数", "type": "float", "required": True},
    {"name": "password", "desc": "密码", "type": "password", "required": True},
    {"name": "date", "desc": "日期", "type": "date", "required": True},
    {"name": "time", "desc": "时间", "type": "time", "required": True},
    {"name": "datetime", "desc": "日期时间", "type": "datetime", "required": True},
    {"name": "file", "desc": "日期时间", "type": "file", "required": True}], "输入数据直接返回")
def api_post_test(request):
    try:
        s = request.POST.get("str", None)
        i = request.POST.get("int", None)
        f = request.POST.get("float", None)
        p = request.POST.get("password", None)
        d = request.POST.get("date", None)
        t = request.POST.get("time", None)
        dt = request.POST.get("datetime", None)
        file = request.FILES["file"]

        return HttpResponse(json.dumps(request.POST, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, msg_type="error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


@api.register("model通用增加接口", "POST", [
    {"name": "model_name", "desc": "model名称", "type": "str", "required": True},
    {"name": "data", "desc": "字段数据(json字符串格式)"
                             "{{\n}}例如：{'name': 'zhangsan', 'age':16}, "
                             "{{\n}}增加一条name字段为'zhangsan', age字段为16记录",
     "type": "str", "required": True},
])
def v_model_add(request):
    """
    model基类统一增加接口
    """
    from vadmin import admin_auth
    from vadmin.models import VModel
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        VModel.model_add(request)
        result = {"c": 0}
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


def v_model_del(request):
    """
    model基类统一删除接口（只能删除自已新建的数据）
    """
    from vadmin import admin_auth
    from vadmin.models import VModel
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        VModel.model_del(request)
        result = {"c": 0}
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


@api.register("model通用修改接口", "POST", [
    {"name": "model_name", "desc": "model名称", "type": "str", "required": True},
    {"name": "data", "desc": "字段数据(json字符串格式)"
                             "{{\n}}例如：{'id':1, 'name': 'zhangsan', 'age':16}, "
                             "{{\n}}将ID为1这条记录name字段值修改成'zhangsan', age字段修改成16",
     "type": "str", "required": True},
])
def v_model_edit(request):
    """
    model基类统一修改接口（只能修改自已新建的数据）
    """
    from vadmin import admin_auth
    from vadmin.models import VModel
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        VModel.model_edit(request)
        result = {"c": 0}
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


@api.register("model通用查询接口（单条）", "POST", [
    {"name": "model_name", "desc": "model名称", "type": "str", "required": True},
    {"name": "data", "desc": "过滤字段数据（json字符串格式）"
                             "{{\n}}例如："
                             "{{\n}} 1、{'pk':1}"
                             "{{\n}} 2、{'name': 'zhangsan', 'age':16}",
     "type": "str", "required": True},
])
def v_model_detail(request):
    """
    model基类统一查询详情接口
    """
    from vadmin import admin_auth
    from vadmin.models import VModel
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        result = VModel.model_detail(request)

        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


@api.register("model通用查询接口（多条）", "POST", [
    {"name": "model_name", "desc": "model名称", "type": "str", "required": True},
    {"name": "data", "desc": "过滤字段数据（json字符串格式）"
                             "{{\n}}例如："
                             "{{\n}} 1、{'pk':1}"
                             "{{\n}} 2、{'name': 'zhangsan', 'age':16}",
     "type": "str", "required": True},
])
def v_model_list_detail(request):
    """
    model基类统一查询列表详情接口
    """
    from vadmin import admin_auth
    from vadmin.models import VModel
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        result = VModel.model_list_detail(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")


@task.register(name="记录错误日志", cycle_mode="day", cycle_time="00:30:00")
def format_error_log(request=None):
    try:
        import time
        path = os.path.join(settings.BASE_DIR, "logs")
        path = os.path.abspath(path)
        for root, dirs, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                file_path = os.path.abspath(file_path)
                buf = open(file_path, "rb").read()
                lst_item = buf.split(b"[ERROR]")
                error_count = len(lst_item)
                for i in range(0, error_count):
                    item1 = str(lst_item[i], encoding="utf-8")
                    if i + 1 >= error_count:
                        break

                    item2 = str(lst_item[i + 1], encoding="utf-8")

                    lst_error = [item1.rsplit("\n", 1)[-1], "[ERROR]"]
                    item2 = item2.split("[INFO]")[0].split("[WARNING]")[0].split("[DEBUG]")[0]
                    sub = item2.rsplit("\n", 1)
                    lst_error.append(sub[0])
                    content = "".join(lst_error)
                    error_time = content[0:23]
                    obj = ErrorLog.objects.filter(error_time=error_time).first()
                    if obj is None:
                        ErrorLog.objects.create(path=file, error_time=error_time, content=content)

    except (BaseException,):
        logger.error(traceback.format_exc())


@task.register(name="数据表转储", cycle_mode="day", cycle_time="04:30:00")
def data_dump(request=None):
    try:
        path = os.path.join(settings.MEDIA_ROOT, "backup")  # 根目录，如果空间不够可以修改此目录
        if not os.path.exists(path):
            os.makedirs(path)

        now = datetime.datetime.now()
        s_date = now.strftime("%Y-%m-%d")
        for o_data_dump in DataDump.objects.filter(enable=True):
            lst_sql = []
            try:
                with transaction.atomic():
                    if o_data_dump.max_number is not None:
                        model_admin = admin_api.get_model_admin(o_data_dump.app_label, o_data_dump.model_name)
                        if o_data_dump.order_field:
                            try:
                                order_field = eval(o_data_dump.order_field)
                            except (BaseException,):
                                order_field = [o_data_dump.order_field]
                            queryset = model_admin.model.objects.all().order_by(*order_field)
                        else:
                            queryset = model_admin.model.objects.all()

                        count = queryset.count()
                        if count > o_data_dump.max_number:
                            for obj in queryset[o_data_dump.max_number:]:
                                lst_sql.append(obj.db_2_sql())
                                obj.delete()

                    elif o_data_dump.max_day is not None:
                        model_admin = admin_api.get_model_admin(o_data_dump.app_label, o_data_dump.model_name)
                        last_time = calc_time.subtract_day(now, o_data_dump.max_day)
                        dict_filter = {"%s__lte" % o_data_dump.order_field:
                                           "%s 23:59:59" % last_time.strftime("%Y-%m-%d")}
                        queryset = model_admin.model.objects.filter(**dict_filter)
                        for obj in queryset:
                            lst_sql.append(obj.db_2_sql())
                        queryset.delete()

                if lst_sql:
                    file_sql = "backup_table_%s_%s.sql" % (o_data_dump.model_name, s_date)
                    file_path = os.path.join(path, file_sql)
                    fh = open(file_path, "w")
                    fh.write("\r\n".join(lst_sql))
                    fh.close()

                    zip_path = os.path.join(path, "backup_table_%s_%s.zip" % (o_data_dump.model_name, s_date))
                    z = zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_STORED)
                    z.write(file_path, file_sql)
                    z.close()
                    os.remove(file_path)

            except (BaseException,):
                logger.error(traceback.format_exc())

    except (BaseException,):
        logger.error(traceback.format_exc())


@task.register(name="数据表条数记录", cycle_mode="week", cycle_time="5 04:30:00")
def db_data_statistics(request=None):
    for app in settings.INSTALLED_APPS:
        try:
            module = importlib.import_module("%s.models" % app)
        except (BaseException,):
            continue

        for s in module.__dict__:
            try:
                if s[0:2] == "__":
                    continue

                model = getattr(module, s)
                if (not hasattr(model, "__module__")) or (model.__module__.find(app) < 0) or \
                        (not hasattr(model, "_meta")):
                    continue

                if model._meta.proxy or (not model._meta.db_table) or model._meta.abstract:
                    continue

                number = model.objects.all().count()
                queryset = DBDataLog.objects.filter(table_name=model._meta.db_table)
                if queryset.count() > 100:
                    queryset.last().delete()

                DBDataLog.objects.create(app_name=app, verbose_name=model._meta.verbose_name,
                                         table_name=model._meta.db_table,
                                         model_name=model._meta.object_name,
                                         number=number)

            except (BaseException,):
                # print(traceback.format_exc())
                pass


@api.register(desc="下载APP(通常扫描下载使用)", method="GET",
              param_desc=[{"name": "version", "desc": '版本号'},
                          {"name": "client_type", "desc": '(1, "Android"), (2, "ios")', "type": "int", "default": 1}, ],
              )
def download_app(request):
    try:

        version = request.GET.get("version", None)
        client_type = request.GET.get("client_type", 1)

        if version is None:
            o_app_version = AppVersion.objects.filter(client_type=client_type, del_flag=False).last()
        else:
            o_app_version = AppVersion.objects.filter(client_type=client_type, version=version, del_flag=False).first()

        if o_app_version:
            if o_app_version.download_url:
                url = o_app_version.download_url
            else:
                url = o_app_version.file.name
            return redirect(url)
        else:
            url = ""
        return HttpResponse(url, content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        dict_resp = {"c": -1, "m": s_err_info}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False), content_type="application/json")


@api.register(desc="检查APP最新版本", method="GET",
              param_desc={"name": "client_type", "desc": '(1, "Android"), (2, "ios")', "type": "int", "default": 1},
              result_desc=["version:版本号", "force_update:强制更新(等于true需强制更新才能使用，否则提醒由用户选择）",
                           "download_url:文件升级包下载路径"]
              )
def new_app_version(request):
    try:
        client_type = request.GET.get("client_type", 1)
        o_app_version = AppVersion.objects.filter(client_type=client_type).last()
        dict_resp = {"c": 0, "version": "0", "force_update": False}
        if o_app_version:
            if o_app_version.download_url:
                dict_resp = {"c": 0, "version": o_app_version.version, "force_update": o_app_version.force_update,
                             "download_url": str(o_app_version.download_url)}
            elif o_app_version.file:
                dict_resp = {"c": 0, "version": o_app_version.version, "force_update": o_app_version.force_update,
                             "download_url": str(o_app_version.file.url)}

        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        dict_resp = {"c": -1, "m": s_err_info}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False), content_type="application/json")


@api.register(desc="检查版本补丁", method="GET",
              param_desc={"name": "version", "desc": '目前版本号', "type": "float"},
              result_desc=["version:新版本号", "desc:新版本说明", "upgrade:升级文件路径"]
              )
def new_patch(request):
    try:
        version = request.GET.get("version", None)
        if not version:
            obj = VersionPatch.objects.filter(enable=True).first()
        else:
            obj = VersionPatch.objects.filter(enable=True, version__gt=version).first()

        result = {"c": 0}
        if obj:
            result = {"c": 0, "version": obj.version, "desc": obj.desc, "upgrade": obj.upgrade.name}

        return HttpResponse(json.dumps(result, ensure_ascii=False), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        dict_resp = {"c": -1, "m": s_err_info}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False), content_type="application/json")
