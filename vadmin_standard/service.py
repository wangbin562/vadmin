# !/usr/bin/python
# -*- coding=utf-8 -*-
import importlib
import json
import logging
import random
import traceback

from django.db.models import Q
from django.conf import settings
from vadmin import common
from vadmin import const
from vadmin import step
from vadmin import theme
from vadmin import widgets
from vadmin import admin_api
from vadmin_standard.models import Api
from vadmin_standard.models import OperationLog
from vadmin_standard.models import Todo
from utils import vadmin_2_word
from utils import vadmin_2_excel
from django.db import models

logger = logging.getLogger(__name__)


def operation_log_add(request, app_label, model_name, operation_type, obj, desc=None, data=None):
    """
    增加记录操作日志
    :param request:
    :param app_label:
    :param model_name:
    :param operation_type:
    :param obj:
    :param desc:
    :param data:
    :return:
    """
    max_len = 200
    model_admin = admin_api.get_model_admin(app_label, model_name)
    if desc is None:
        lst_desc = []
        if operation_type == 1:
            if data:
                for k, v in data.items():
                    if v in ["", None]:
                        continue

                    try:
                        db_field = admin_api.get_field(model_admin, k)
                        lst_desc.append("[%s]字段值为[%s]" % (db_field.verbose_name, str(v)[:max_len]))
                    except (BaseException,):
                        pass

            if lst_desc:
                desc = "新增[%s]数据，内容:\r\n%s" % (model_admin.model._meta.verbose_name, "\r\n".join(lst_desc))
            else:
                desc = "新增[%s]数据" % model_admin.model._meta.verbose_name

        elif operation_type == 2:
            if data:
                for k, v in data.items():
                    try:
                        db_field = admin_api.get_field(model_admin, k)
                        lst_desc.append("[%s]字段值为[%s]" % (db_field.verbose_name, str(v)[:max_len]))
                    except (BaseException,):
                        pass
            else:
                for k, v in obj.get_info().items():
                    if k in ["ID", "id"]:
                        continue

                    try:
                        db_field = admin_api.get_field(model_admin, k)
                        lst_desc.append("[%s]字段值为[%s]" % (db_field.verbose_name, str(v)[:max_len]))
                    except (BaseException,):
                        pass

            if lst_desc:
                desc = "删除[%s]数据，内容:\r\n%s" % (model_admin.model._meta.verbose_name, "\r\n".join(lst_desc))
            else:
                desc = "删除[%s]数据" % model_admin.model._meta.verbose_name

        else:  # 修改
            if data:
                for k, v in data.items():
                    try:
                        db_field = admin_api.get_field(model_admin, k)
                        lst_desc.append("[%s]字段值修改为[%s]" % (db_field.verbose_name, str(v)[:500]))
                    except (BaseException,):
                        pass
                desc = "修改[%s]数据，内容:%s" % (model_admin.model._meta.verbose_name, "\r\n".join(lst_desc))

    if data is not None:
        data = str(data)

    operation_model = "%s.%s" % (app_label, model_name)
    ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', None))
    return OperationLog.objects.create(user_id=request.user.pk, username=str(request.user),
                                       ip=ip, operation_type=operation_type,
                                       operation_model=operation_model.lower(),
                                       operation_object_id=obj.pk, operation_desc=desc,
                                       operation_data=data)


def api_module(request, module_name=None):
    content = request.POST.get(const.SUBMIT_WIDGET, "{}")
    widget_data = json.loads(content)
    api_name = request.GET.get("api-name", None)
    search = request.GET.get("search", None)
    if search:
        queryset = Api.objects.filter(Q(name__icontains=search) | Q(desc__icontains=search), del_flag=False)
    else:
        module_name = request.GET.get("module-name", None) or module_name
        queryset = Api.objects.filter(module=module_name, del_flag=False)
    queryset = queryset.order_by("module", "name")
    height = 50
    font = {"color": "#00B29C"}

    o_panel = widgets.Panel(name="module", vertical="top", width="96%",
                            horizontal="left", scroll={"y": "auto"})

    for i, obj in enumerate(queryset):
        expand = False
        if (api_name is None) and (1 == 0):
            expand = True

        o_panel_label = widgets.Panel(width="100%", height="100%", scroll={"y": "hidden"})
        o_text = widgets.Text(text=" %s" % obj.method, height=height, width=50)

        if obj.method == "GET":
            head_color = "#64B1F0"
        elif obj.method == "POST":
            head_color = "#4BCA92"
        else:
            head_color = "#FBA131"
        o_text.set_attr_value("bg", {"color": head_color})

        o_text.set_attr_value("font", {"color": "#FFFFFF", "weight": "bold"})

        o_panel_label.append(o_text)
        pattern = "%s/%s/" % (obj.module.replace(".", "/"), obj.name)
        o_panel_label.append(widgets.Text(text="{{col.10}}%s" % pattern, keyword=search))
        o_panel_label.append(widgets.Text(text="{{col.10}}%s" % obj.desc, keyword=search))

        o_panel_content = widgets.Panel(name=obj.name, width="100%", margin_left=20, margin_right=20)
        if obj.param:
            param = json.loads(obj.param)
            if isinstance(param, dict):
                param = [param, ]

            table_data = [("参数名称", "输入", "参数说明", "数据类型")]
            for dict_item in param:
                name = dict_item["name"]
                data_type = dict_item.get("type", "str")

                if data_type == "int":
                    o_input = widgets.Input(name=name)
                elif data_type == "str":
                    o_input = widgets.Input(name=name, input_type="textarea", height=36)
                elif data_type == "float":
                    o_input = widgets.Input(name=name, input_type="number")
                elif data_type == "file":
                    o_input = widgets.Upload(name=name, upload_url="")
                elif data_type == "date":
                    o_input = widgets.DatePicker(name=name)
                elif data_type == "time":
                    o_input = widgets.TimePicker(name=name)
                elif data_type == "datetime":
                    o_input = widgets.DateTimePicker(name=name)
                elif data_type == "password":
                    o_input = widgets.Input(name=name, input_type="password")
                    try:
                        if settings.V_PWD_ENCRYPT_KEY:
                            o_input.encrypt = settings.V_PWD_ENCRYPT_KEY
                    except (BaseException,):
                        pass

                else:
                    o_input = widgets.Input(name=name)

                value = widget_data.get(name, None)
                if value is None:
                    o_input.set_attr_value("value", dict_item.get("default", None))
                elif obj.name == api_name:
                    o_input.set_attr_value("value", value)

                required = dict_item.get("required", None)
                o_input.set_attr_value("required", required)

                o_input.set_attr_value("bg", {"color": "#FFFFFF"})
                if required:
                    o_text = widgets.Text("%s  *  " % dict_item["name"], keyword="*", keyword_color="#FF0000")
                else:
                    o_text = dict_item["name"]

                table_data.append([o_text, o_input, dict_item.get("desc", ""), data_type])

            o_table = widgets.LiteTable(data=table_data, space_top=10, space_bottom=10,
                                        col_width={2: "50%", 3: 140})
            o_panel_content.append(o_table)

        disabled_style = {"bg_color": "#FEF7DB", "font_color": "#000000"}
        border = {"color": "#FF0000"}
        if obj.result:
            result = obj.result
            try:
                r = json.loads(obj.result)
                if isinstance(r, (list, tuple)):
                    result = "\r\n".join(r)
            except (BaseException,):
                pass

            o_panel_content.append(widgets.Text(text="{{row.20}}返回值说明", font=font))
            o_panel_content.append(widgets.Row(10))
            o_panel_content.append(widgets.Input(input_type="textarea", disabled=True,
                                                 disabled_style=disabled_style,
                                                 border=border, width="98%", value=result, max_height=200))

        o_panel_content.append(widgets.Row(10))
        url = const.URL_RUN_SCRIPT % "vadmin_standard.service.run_api" + \
              ("/?module-name=%s&api-name=%s" % (obj.module, obj.name))
        o_step = step.Request(url=url, submit_type="child", parent=obj.name, check_required=True)
        o_panel_content.append(widgets.Button(text="执行", step=o_step))
        o_panel_content.append(widgets.Row(30))

        if api_name == obj.name:
            o_panel_result = run_api(request, obj)
        else:
            o_panel_result = widgets.Panel(name="%s_result" % obj.name, width="100%")
        o_panel_content.append(o_panel_result)

        data = [{"label": o_panel_label, "content": o_panel_content, "expand": expand}]
        o_widget = widgets.Collapse(data=data, width="100%", height=height, border_color=head_color)

        o_panel.append(o_widget)
        o_panel.append(widgets.Row(10))

    o_panel.append(widgets.Row(30))
    return o_panel


def run_api(request, obj=None):
    font = {"color": "#00B29C"}
    disabled_style = {"bg_color": "#FEF7DB", "font_color": "#000000"}
    border = {"color": "#FF0000"}
    content = request.POST.get(const.SUBMIT_WIDGET, "{}")
    widget_data = json.loads(content)

    update = True
    if obj:
        module_name = obj.module
        api_name = obj.name
        update = False
    else:
        module_name = request.GET["module-name"]
        api_name = request.GET["api-name"]
        obj = Api.objects.filter(module=module_name, name=api_name, del_flag=False).first()

    o_module = importlib.import_module(module_name)

    fun = getattr(o_module, api_name)
    pattern = "%s/%s/" % (obj.module.replace(".", "/"), obj.name)

    if obj.method == "GET":
        dict_get = {}
        if obj.param:
            param = json.loads(obj.param)
            if isinstance(param, dict):
                param = [param, ]

            for dict_item in param:
                name = dict_item["name"]
                value = widget_data.get(name, "")
                if value is None:
                    value = ""

                dict_get[name] = value

        param = []
        for k, v in dict_get.items():
            param.append("%s=%s" % (k, v))

        if param:
            if 'HTTP_ORIGIN' in request.META:
                run_url = "%s/%s?%s" % (request.META['HTTP_ORIGIN'], pattern, "&".join(param))
            elif 'wsgi.url_scheme' in request.META and 'HTTP_HOST' in request.META:
                run_url = "%s://%s/%s" % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'], pattern)
            else:
                run_url = "%s%s?%s" % (request.META['HTTP_REFERER'], pattern, "&".join(param))
        else:
            if 'HTTP_ORIGIN' in request.META: # request.META['wsgi.url_scheme'], request.META["HTTP_HOST"]
                run_url = "%s/%s" % (request.META['HTTP_ORIGIN'], pattern)
            elif 'wsgi.url_scheme' in request.META and 'HTTP_HOST' in request.META:
                run_url = "%s://%s/%s" % (request.META['wsgi.url_scheme'], request.META['HTTP_HOST'], pattern)
            else:
                run_url = "%s%s" % (request.META['HTTP_REFERER'], pattern)

        try:
            mutable = request.GET._mutable
            request.GET._mutable = True
            request.GET.clear()
            request.GET.update(dict_get)
            request.GET._mutable = mutable
            common.make_request_url(request, dict_get)
            r = fun(request)
            run_result = bytes.decode(r.content)
        except (BaseException,):
            run_result = traceback.format_exc()
    else:
        dict_post = {}
        if obj.param:
            param = json.loads(obj.param)
            for dict_item in param:
                name = dict_item["name"]
                dict_post[name] = widget_data.get(name, "")

        run_url = "%s%s" % (request.META['HTTP_REFERER'], pattern)
        try:
            mutable = request.GET._mutable
            request.POST._mutable = True
            request.POST.clear()
            request.POST.update(dict_post)
            request.POST._mutable = mutable
            r = fun(request)
            run_result = bytes.decode(r.content)
        except (BaseException,):
            run_result = traceback.format_exc()

    o_panel_result = widgets.Panel(name="%s_result" % obj.name, width="100%")
    o_panel_result.append(widgets.Text(text="请求URL", font=font))
    o_panel_result.append(widgets.Row(10))
    o_panel_result.append(widgets.Input(disabled=True, value=run_url,
                                        disabled_style=disabled_style,
                                        border=border, width="98%", height=50))

    o_panel_result.append(widgets.Row(10))
    o_panel_result.append(widgets.Text(text="返回数据{{row.6}}", font=font))
    o_panel_result.append(widgets.Json(text=run_result, width="98%", max_height=600,
                                       bg={"color": "#FEF7DB"}))
    o_panel_result.append(widgets.Row(10))

    if update:
        return step.WidgetUpdate(data=o_panel_result, mode="all")

    return o_panel_result


def todo_complete(request):
    object_id = request.GET[const.UPN_OBJECT_ID]
    obj = Todo.objects.filter(pk=object_id).first()
    if obj:
        obj.complete = True
        obj.save()

    return step.WidgetOpera(name="todo-table", opera=const.OPERA_TABLE_ROW_DEL, data={"row_id": object_id})


def export_db_2_excel(request):
    """"""
    lst_widget = []
    row_idx = 0

    def db_field_2_data_type(db_field):
        data_type = None
        data_length = None
        if isinstance(db_field, models.CharField):
            data_type = "VARCHAR"
            data_length = db_field.max_length
        elif isinstance(db_field, models.TextField):
            data_type = "TEXT"
        elif isinstance(db_field, (models.FloatField, models.DecimalField)):
            data_type = "DOUBLE"
            data_length = 16
        elif isinstance(db_field, (models.BigIntegerField, models.BigAutoField)):
            data_type = "BIGINT"
            data_length = 8
        elif isinstance(db_field, (models.SmallIntegerField, models.PositiveSmallIntegerField)):
            data_type = "SMALLINT"
            data_length = 2
        elif isinstance(db_field, (models.IntegerField, models.PositiveIntegerField, models.AutoField)):
            data_type = "INT"
            data_length = 4
        elif isinstance(db_field, (models.BooleanField, models.NullBooleanField)):
            data_type = "TINYINT"
            data_length = 1
        elif isinstance(db_field, models.DateTimeField):
            data_type = "DATETIME"
        elif isinstance(db_field, models.DateField):
            data_type = "DATE"
        elif isinstance(db_field, models.TimeField):
            data_type = "TIME"
        elif isinstance(db_field, (models.FileField, models.ImageField)):
            data_type = "VARCHAR"
            data_length = db_field.max_length

        return data_type, data_length

    for app in settings.INSTALLED_APPS:
        if app.find("django") == 0:  # 过滤系统默认
            continue

        try:
            module = importlib.import_module("%s.models" % app)
        except (BaseException,):
            continue

        col_width = {0: 200, 1: 200, 2: 200, 3: 200, 4: 120, 5: 80, 6: 80, 7: 120, 8: 80, 9: 80,
                     10: 80, 11: 200, 12: 180, 13: 180, 14: 180}

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

                cell_style = {}
                data = []
                row = ["表名", "中文说明", "字段英文名称", "字段中文名称", "数据类型", "长度", "是否必填", "默认值",
                       "主键", "索引", "唯一", "字段枚举", "外键关系", "数据来源", "数据举例"]
                data.append(row)
                for i, db_field in enumerate(model._meta.fields):
                    row = []
                    if i == 0:
                        row.append(model._meta.db_table)
                        row.append(str(model._meta.verbose_name))
                        cell_style["%s-0:%s-14" % (row_idx, row_idx)] = {"bg": {"color": "#00B441"}}
                        begin_idx = row_idx + 1
                    else:
                        row.append(None)
                        row.append(None)
                    field_name = db_field.get_attname()
                    row.append(field_name)
                    row.append(str(db_field.verbose_name))

                    if isinstance(db_field, models.ForeignKey):
                        data_type, data_length = db_field_2_data_type(db_field.target_field)
                    else:
                        data_type, data_length = db_field_2_data_type(db_field)

                    row.append(data_type)
                    row.append(data_length)

                    if db_field.null:
                        row.append("否")
                    else:
                        row.append("是")

                    if ("NOT_PROVIDED" not in str(db_field.default)) and (not callable(db_field.default)):
                        row.append(db_field.default)
                    else:
                        row.append(None)

                    if db_field.primary_key:
                        row.append("是")
                    else:
                        row.append("否")

                    if db_field.db_index:
                        row.append("是")
                    else:
                        row.append("否")

                    if db_field.unique:
                        row.append("是")
                    else:
                        row.append("否")

                    if db_field.choices:
                        choices = []
                        for k, v in db_field.choices:
                            choices.append("%s:%s" % (k, v))
                        row.append("\r\n".join(choices))  # 字段枚举
                    else:
                        row.append(None)  # 字段枚举
                    if isinstance(db_field, models.ForeignKey):
                        row.append("%s表%s字段" % (db_field.target_field.model._meta.db_table,
                                                db_field.target_field.get_attname()))
                    else:
                        row.append(None)  # 外键关系

                    row.append(None)  # 数据来源
                    row.append(None)  # 数据举例
                    data.append(row)

                row_idx += len(model._meta.fields)
                merged_cells = []
                merged_cells.append("%s-0:%s-0" % (begin_idx, row_idx))
                merged_cells.append("%s-1:%s-1" % (begin_idx, row_idx))
                row_idx += 1
                merged_cells.append("%s-0:%s-14" % (row_idx, row_idx))
                o_table = widgets.LiteTable(data=data,
                                            merged_cells=merged_cells,
                                            col_width=col_width, row_height=36,
                                            horizontal="center", vertical="center",
                                            col_border={"color": "#000000"},
                                            row_border={"color": "#000000"},
                                            cell_style=cell_style)
                lst_widget.append(o_table)
                lst_widget.append(widgets.Row(height=40))
                row_idx += 1

            except (BaseException,):
                logger.error(traceback.format_exc())

    path = common.get_export_path(suffix=".xlsx")
    vadmin_2_excel.generate(path, lst_widget)
    return step.DownloadFile(common.get_download_url(path))


def export_db_2_word(request):
    """"""
    pass
