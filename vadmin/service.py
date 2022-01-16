# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
vadmin service
"""
import copy
import datetime
import importlib
import json
import logging
import os
import re

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import fields
from django.db.utils import IntegrityError

from vadmin import admin_api
from vadmin import admin_fields
from vadmin import const
from vadmin import step
from vadmin import theme
from vadmin import widgets

logger = logging.getLogger(__name__)


def refresh_page(request, o_content=None, menu_value=None):
    """
    界面部分修改或全量刷新
    :param request:
    :param o_content: 内容布局
    :param menu_value:
    :return:
    """
    content = request.POST.get(const.SUBMIT_HIDE, "{}")
    dict_hide = json.loads(content)
    if o_content:
        o_content.name = const.WN_CONTENT_RIGHT

    result = []
    if int(dict_hide.get(const.WN_PART_LOAD, 0)):
        result = [step.WidgetLoad(data=o_content), ]
    elif int(dict_hide.get(const.WN_CONTENT_HIDE, 0)) or int(request.GET.get(const.WN_CONTENT_HIDE, 0)):
        result = [step.WidgetUpdate(data=o_content, mode="all"), ]
    else:
        user_agent = request.META["HTTP_USER_AGENT"].lower()
        if ("android" in user_agent) or ("iphone" in user_agent):  # 手机入口
            result = [step.WidgetLoad(data=widgets.Page(children=o_content)), ]

        elif const.UPN_SHOW_MODE in request.GET:
            lite = request.GET[const.UPN_SHOW_MODE]
            if lite == "none":  # 不显示菜单
                result = [step.WidgetLoad(data=o_content), ]
            elif lite == "top":  # 显示头部菜单
                pass
            elif lite == "left":  # 显示左边菜单
                pass

        else:
            o_theme = theme.get_theme(request.user.id)
            o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
            o_page = o_module.Page(request, o_theme).create(o_content)
            result = [step.WidgetLoad(data=o_page),
                      # step.WidgetUpdate(data=o_content, mode="all"),
                      step.AddHide(data={const.WN_CONTENT_HIDE: 1})
                      ]

    return result


def make_page(request, o_theme):
    o_page = widgets.Page(bg_color=o_theme.bg_color)

    # o_grid_top.opacity = 50
    user_agent = request.META["HTTP_USER_AGENT"].lower()
    if ("android" in user_agent) or ("iphone" in user_agent):
        pass

    elif int(request.GET.get(const.UPN_SHOW_MODE, 0)):
        pass

    # elif int(request.GET.get(const.VERSION_LEFT_MENU, 0)):
    #     pass
    # elif int(request.GET.get(const.VERSION_TOP_MENU, 0)):
    #     pass

    else:
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_page = o_module.Page(request, o_theme).create()

    return o_page


def make_list(request, **kwargs):
    app_label = request.GET[const.UPN_APP_NAME]
    model_name = request.GET[const.UPN_MODEL_NAME]
    model_admin = admin_api.get_model_admin(app_label, model_name)
    p_name = const.WN_PAGINATION % model_name
    page_index = int(request.GET.get(p_name, 1))

    o_theme = theme.get_theme(request.user.id)
    o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
    o_template = o_module.ChangeList(request, app_label, model_name, o_theme)
    o_grid = o_template.make_list_view()
    # o_grid = widgets.Grid()

    return step.WidgetUpdate(data=o_grid, mode="all")


def make_form(request, **kwargs):
    pass


def select_search_queryset(request, app_label, model_name, search_field, search_term, queryset=None):
    """
    """
    from functools import reduce
    from django.db.models import Q
    model_admin = admin_api.get_model_admin(app_label, model_name)

    if queryset is None:
        queryset = model_admin.get_queryset(request)

    # try:
    #     queryset = model_admin.get_select_search_results(request, queryset, search_field)
    # except (BaseException,):
    #     pass
    # search_fields = self.get_search_fields()
    select = Q()
    # term = search_term.replace('\t', ' ')
    # term = search_term.replace('\n', ' ')
    # for t in [t for t in term.split(' ') if not t == '']:
    search_fields = ["%s__icontains" % search_field]
    select &= reduce(lambda x, y: x | Q(**{y: search_term}), search_fields,
                     Q(**{search_fields[0]: search_term}))

    return queryset.filter(select).distinct()[0:50]  # 最大50个


def change_form_save(request, model_admin, old_obj, data, inline_data=None):
    """
    检查并保存
    :param request:
    :param model_admin:
    :param old_obj:
    :param data:界面提交的数据
    :param inline_data:子表数据
    """
    dict_error = {}
    if old_obj:
        # old_obj = model_admin.get_object(request, object_id)
        obj = copy.copy(old_obj)
        change = True
    else:
        # old_obj = None
        obj = model_admin.opts.model()
        change = False

    msg = None
    update_data = {}  # 界面提交和数据库中不一样的数据
    save_data = {}  # 界面提交数据
    m2m_data = {}  # ManyToManyField字段数据

    msg = model_admin.save_before(request, old_obj, data, dict_error, inline_data)
    if dict_error or msg:
        return obj, dict_error, msg

    dict_foreign_key = {}  #
    for k, v in data.items():
        if "__" in k:
            field, field_sub = k.split("__")[0:2]
            try:
                db_field = admin_api.get_field(model_admin, field)
            except (BaseException,):
                continue
            # db_field_name = db_field.get_attname()
            # if db_field_name not in data:
            #     dict_error[k] = "子字段的外键对象不存在！"
            # elif (v is not None) and (data[db_field_name] is None):
            #     # dict_error[k] = "子字段的父类不能为空！"
            #     dict_error[db_field_name] = "外键字段已有值，外键对象不能为空！"
            # else:
            db_field_sub = admin_api.get_field_by_model(db_field.related_model, field_sub)
            dict_foreign_key.setdefault(field, {})
            dict_foreign_key[field][db_field_sub.get_attname()] = v

        elif "--" in k:  # 表格
            continue
        else:
            try:
                db_field = admin_api.get_field(model_admin, k)
                k = db_field.get_attname()
            except (BaseException,):
                save_data[k] = v
                continue

            is_equal, new_value = submit_data_compare(db_field, k, v, old_obj)
            if not is_equal:
                update_data[k] = new_value
            save_data[k] = new_value

    # 没有修改，也没有子表数据
    # if (not update_data) and (not inline_data):
    #     if hasattr(model_admin, "v_save_after"):
    #         msg = model_admin.v_save_after(request, old_obj, obj, save_data, update_data, m2m_data, dict_error,
    #                                        inline_data, change)
    #     # return obj, dict_error, msg

    if dict_error or msg:
        return obj, dict_error, msg

    for k, v in update_data.items():
        if isinstance(v, (list, tuple)):  # m2m
            m2m_data[k] = v
            continue

        setattr(obj, k, v)

    # 检查数据是否正确
    fields_check(request, model_admin, save_data, dict_error, obj)

    if dict_error or msg:
        return obj, dict_error, msg

    with transaction.atomic():
        # 保存外键关联数据
        for fk_field_name, dict_fk_value in dict_foreign_key.items():
            fk_id = getattr(obj, "%s_id" % fk_field_name)
            if fk_id:  # 修改保存
                obj_fk = getattr(obj, fk_field_name)
                for k, v in dict_fk_value.items():
                    setattr(obj_fk, k, v)

                msg, sub_field_name = save_check(obj_fk.save)
                if msg:
                    dict_error["%s__%s" % (fk_field_name, sub_field_name)] = msg
                    return obj, dict_error, msg

            else:  # 新建保存
                db_field = admin_api.get_field(model_admin, fk_field_name)

                try:
                    fk_obj = db_field.related_model.objects.create(**dict_fk_value)
                    setattr(obj, "%s_id" % fk_field_name, fk_obj.pk)
                except IntegrityError as e:
                    field_name = None

                    if e.args[0] == 1062:
                        msg = "%s唯一约束错误！%s" % (db_field.verbose_name, e.args[1])
                        field_name = re.findall("Duplicate entry .* for key '(.*)'", e.args[1], re.S | re.I)[0]
                        dict_error["%s__%s" % (fk_field_name, field_name)] = msg

                    elif e.args[0] == 1048:
                        msg = "%s字段不能为空。%s" % (db_field.verbose_name, e.args[1])
                        field_name = re.findall("Column '(.*)' cannot be null", e.args[1], re.S | re.I)[0]
                        dict_error["%s__%s" % (fk_field_name, field_name)] = msg

                    if (dict_error or msg) and field_name:
                        dict_error[field_name] = msg
                        return obj, dict_error, msg

        if change:
            if m2m_data:
                for k, v in m2m_data.items():
                    try:
                        getattr(obj, k).set(v)  # ManyToManyField字段可以直接用=[1,2]重新赋值, 保存m2m时，obj.pk必须有值
                    except (BaseException,):
                        pass

            if update_data:
                msg, field_name = save_check(model_admin.save_model, request, obj, None, change)  # 保存，同时检查
                if dict_error or msg:
                    dict_error[field_name] = msg
                    return obj, dict_error, msg

        else:
            msg, field_name = save_check(model_admin.save_model, request, obj, None, change)
            if dict_error or msg:
                dict_error[field_name] = msg
                return obj, dict_error, msg

            if m2m_data:
                for k, v in m2m_data.items():
                    getattr(obj, k).set(v)  # ManyToManyField字段可以直接用=[1,2]重新赋值, 保存m2m时，obj.pk必须有值
                obj.save()  # 有m2m且新建时，要保存两次

        # if update_data:
        #     if change:
        #         model_admin.log_change(request, obj,
        #                                '[{"changed": {"fields": [%s]}}]' % ".".join(list(update_data.keys())))
        #     else:
        #         model_admin.log_addition(request, obj,
        #                                  '[{"added": {"fields": [%s]}}]' % ".".join(list(update_data.keys())))

        # 保存子表数据
        for inline_name, lst_data in (inline_data or {}).items():  #
            if not lst_data:
                continue

            obj_inline = admin_api.get_inline(request, model_admin, inline_name)
            if obj_inline is None:
                continue

            # obj_inline = inline(model=inline.model, admin_site=admin.site)
            field_name = admin_api.get_foreign_key_field(obj_inline, model_admin.model)
            db_field = admin_api.get_field(obj_inline, field_name)
            if db_field.to_fields and db_field.to_fields[0]:
                foreign_key_id = getattr(obj, db_field.to_fields[0])
            else:
                foreign_key_id = obj.pk

            for dict_data in lst_data:
                if not dict_data:
                    continue

                obj_sub = None
                row_id = dict_data["id"]
                try:
                    if int(row_id) < 0:
                        del dict_data["id"]
                    else:
                        obj_sub = obj_inline.model.objects.filter(pk=row_id).first()
                except (BaseException,):
                    obj_sub = obj_inline.model.objects.filter(pk=row_id).first()

                db_field = admin_api.get_field(obj_inline, field_name)
                try:
                    field_name = db_field.get_attname()
                except (BaseException,):
                    pass

                dict_data[field_name] = foreign_key_id
                obj_sub, dict_error_sub, msg_sub = change_form_save(request, obj_inline, obj_sub, dict_data)
                if dict_error_sub or msg_sub:
                    for field_name_sub, error in dict_error_sub.items():
                        app_label, model_name = obj_inline.opts.app_label, obj_inline.opts.model_name
                        table_name = const.WN_TABLE % (app_label, model_name)
                        name = "%s|%s|%s" % (table_name, row_id, field_name_sub)
                        dict_error[name] = error
                        # dict_error.setdefault(table_name, []).append({"field": field_name_sub,
                        #                                               "id": row_id, "error": error})
                    try:
                        obj.pk = "error" * 50  # 手动抛异常，让批处理失败
                        obj.save()
                    except (BaseException,):
                        pass

                    return obj, dict_error, msg_sub

        msg = model_admin.save_after(request, old_obj, obj, save_data, update_data, m2m_data, dict_error,
                                     inline_data, change)
        if dict_error or msg:
            try:
                obj.pk = "error" * 50  # 手动抛异常，让批处理失败
                obj.save()
            except (BaseException,):
                pass
            return obj, dict_error, msg

    # 最后要删除文件
    if change and (not (dict_error or msg)):
        for k, v in update_data.items():
            if isinstance(v, (list, tuple)):  # m2m
                continue

            db_field = admin_api.get_field(model_admin, k)
            if isinstance(db_field, (admin_fields.ImageField, fields.files.ImageField,
                                     fields.files.FileField, admin_fields.FileField)):
                value = str(getattr(old_obj, k))
                if not value:
                    continue

                new_value = str(getattr(obj, k))

                lst_value = []
                try:
                    lst_value = eval(value)
                except (BaseException,):
                    lst_value.append(value)

                lst_new_value = []
                if new_value:
                    try:
                        lst_new_value = eval(new_value)
                    except (BaseException,):
                        lst_new_value.append(new_value)

                for value in lst_value:
                    if value not in lst_new_value:
                        try:
                            path = os.path.abspath(os.getcwd() + value)
                            os.remove(path)
                        except (BaseException,):
                            pass

    if not (dict_error or msg):
        """记录操作日志"""
        if settings.V_OPERATION_LOG:
            from vadmin_standard import service as vadmin_standard_service
            if old_obj:
                if update_data:
                    vadmin_standard_service.operation_log_add(request,
                                                              model_admin.opts.app_label, model_admin.opts.model_name,
                                                              3, obj, data=update_data)
            else:
                vadmin_standard_service.operation_log_add(request,
                                                          model_admin.opts.app_label, model_admin.opts.model_name,
                                                          1, obj, data=update_data)

    return obj, dict_error, msg


def get_change_form_fields(request, model_admin, obj):
    lst_field = []
    fieldsets = model_admin.get_fieldsets(request, obj)
    for fieldset in fieldsets:
        name, dict_field = fieldset
        for key, val in dict_field.items():
            if key == "classes":
                continue

            for s_field in val:
                if isinstance(s_field, (tuple, list)):
                    for (i, s_field_2) in enumerate(s_field):
                        lst_field.append(s_field_2)
                else:
                    lst_field.append(s_field)

    return lst_field


def parse_inline_data(request, model_admin, widget_data):
    inline_data = {}  # 格式化子表数据
    for key, dict_data in widget_data.items():
        if not isinstance(dict_data, dict):
            continue
        elif "row" not in dict_data:
            continue

        try:
            table_key, field_name, inline_name = key.split("-")
            if table_key != "table":
                continue

        except (BaseException,):
            continue

        inline = []
        for dict_row in dict_data["row"]:
            dict_inline = {}
            for k, v in dict_row.items():
                if k == "row_id":
                    dict_inline["id"] = v
                elif isinstance(v, dict):
                    dict_inline.update(v)
                else:
                    dict_inline[k] = v

            inline.append(dict_inline)
        inline_data[inline_name] = inline

    return inline_data


def fields_check(request, model_admin, save_data, dict_error, obj):
    """
    检查界面提交的数据(默认检查，如果需要业务关联检查，请重新v_check方法）
    :param request:
    :param model_admin:
    :param save_data:保存数据
    :param dict_error:错误数据
    :param obj：对象数据(为前obj,提交后的值已赋值到obj上)
    """
    if model_admin:
        readonly_fields = model_admin.get_readonly_fields(request, obj)
    else:
        readonly_fields = []
    lst_field = save_data.keys()

    for field in lst_field:
        if field in readonly_fields:  # 只读不检查
            continue

        # 自定义的
        if hasattr(model_admin, field) and callable(getattr(model_admin, field)):
            continue

        try:
            db_field = admin_api.get_field(model_admin, field)
        except (BaseException,):
            continue

        if isinstance(db_field, fields.AutoField):
            continue

        if isinstance(db_field, forms.fields.CharField):
            continue

        # if ("fields.NOT_PROVIDED" not in str(db_field.default)) and \
        #         (save_data[field] is None):
        #     save_data[field] = db_field.default
        #     setattr(obj, field, db_field.default)

        if not (db_field.null or db_field.blank):  # 两个都等于false, 非空
            if isinstance(db_field, fields.related.ForeignKey):
                if (field in save_data) and (save_data[field] is None):
                    dict_error[field] = "%s是必填项。" % db_field.verbose_name

                # elif ("%s_id" % field in save_data) and (save_data["%s_id" % field] in ["", None]):
                #     dict_error[field] = _("This field is required.")

                # elif check_obj and getattr(obj, "%s_id" % field) in ["", None]:
                #     dict_error[field] = _("This field is required.")

                # elif check_obj and getattr(obj, field) is None:
                #     dict_error.append({"name": field, "error": _("This field is required.")})

            elif isinstance(db_field, fields.related.ManyToManyField):
                if (field in save_data) and not save_data[field]:
                    dict_error[field] = "%s是必填项。" % db_field.verbose_name

                # elif check_obj and not list(getattr(obj, field).all().values_list("pk", flat=True)):
                #     dict_error[field] = _("This field is required.")
            else:
                if (field in save_data) and (save_data[field] is None):
                    dict_error[field] = "%s是必填项。" % db_field.verbose_name

                # elif check_obj and getattr(obj, field) is None:
                #     dict_error[field] = _("This field is required.")

        if isinstance(db_field, fields.DecimalField):
            if save_data.get(field, None):
                import decimal
                decimal_value = decimal.Decimal(str(save_data[field]))
                for validator in db_field.validators:
                    try:
                        o_validator = validator(decimal_value)
                    except ValidationError as e:
                        dict_error[field] = e.messages[0]

        elif save_data.get(field, None):
            for validator in db_field.validators:
                try:
                    o_validator = validator(save_data[field])
                except ValidationError as e:
                    dict_error[field] = "%s%s" % (db_field.verbose_name, e.messages[0])
                except (BaseException,):
                    pass

        # elif check_obj and getattr(obj, field) is not None:
        #     for validator in db_field.validators:
        #         try:
        #             o_validator = validator(getattr(obj, field))
        #         except ValidationError as e:
        #             dict_error[field] = e.messages[0]
        #         except (BaseException,):
        #             pass

    if obj:
        unique_checks, date_checks = obj._get_unique_checks(exclude=["id"])  # 使用django判断函数(主键重复）
        errors = obj._perform_unique_checks(unique_checks)
        for k, error in errors.items():
            # dict_error[field] = error[0].messages[0]
            for field in unique_checks[0][1]:
                db_field = model_admin.model._meta.get_field(field)
                field_name = db_field.get_attname()
                dict_error[field_name] = "%s%s" % (db_field.verbose_name, error[0].messages[0])


def save_check(fun, *args):
    try:
        fun(*args)
    except IntegrityError as e:
        if e.args[0] == 1062:
            msg = "唯一约束错误！%s" % e.args[1]
            field_name = re.findall("Duplicate entry .* for key '(.*)'", e.args[1], re.S | re.I)[0]
            return msg, field_name
        elif e.args[0] == 1048:
            msg = "字段不能为空错误！%s" % e.args[1]
            field_name = re.findall("Column '(.*)' cannot be null", e.args[1], re.S | re.I)[0]
            # db_field = obj._meta.model._meta.get_field(field_name)
            # dict_error[field_name] = "%s字段不能为空!" % db_field.verbose_name
            return msg, field_name

    return None, None


def submit_data_compare(db_field, field_name, value, old_obj=None):
    """
    界面提交的数据格式化再和字段数据比较
    :param db_field:
    :param field_name:
    :param value:
    :param old_obj:
    :return:is_equal:是否修改 new_value:格式化后的值
    """
    is_equal = True
    new_value = value
    if old_obj is None:
        field_value = None
    else:
        field_value = getattr(old_obj, field_name)  # 默认值

    if isinstance(db_field, (fields.DateTimeField, fields.DateField, fields.TimeField)):
        new_value = None if value in ["", None] else str(value)
        if new_value is None:
            pass
        elif isinstance(db_field, fields.DateTimeField):
            lst_time = new_value.split(":")
            if len(lst_time) == 2:
                new_value = "%s:00" % lst_time

            lst_time = new_value.split(".") # '2021-06-25 22:27:52.486818'
            if len(lst_time) >= 2:
                new_value = lst_time[0]

            new_value = datetime.datetime.strptime(new_value, '%Y-%m-%d %H:%M:%S')

        elif isinstance(db_field, fields.DateField):
            lst_date = new_value.split("-")
            if len(lst_date) == 1:
                new_value = "%s-01-01" % new_value
            elif len(lst_date) == 2:
                new_value = "%s-01" % new_value
            new_value = datetime.datetime.strptime(new_value, '%Y-%m-%d')

        elif isinstance(db_field, fields.TimeField):
            new_value = datetime.datetime.strptime(new_value, '%H:%M:%S')

        if (field_value is None) or (new_value is None):
            if field_value != new_value:
                is_equal = False
        else:
            # if isinstance(db_field, fields.DateTimeField):
            #     new_value = datetime.datetime.strptime(new_value, '%Y-%m-%d %H:%M:%S')
            # elif isinstance(db_field, fields.DateField):
            #     year, month, day = new_value.split("-")
            #     new_value = datetime.date(int(year), int(month), int(day))
            # else:
            #     hour, minute, second = new_value.split(":")
            #     new_value = datetime.time(int(hour), int(minute), int(second))

            if field_value != new_value:
                is_equal = False

    elif isinstance(db_field, fields.related.ManyToManyField):
        new_value = [] if value is None else value
        if field_value is None:
            old_value = []
            if old_value != new_value:
                is_equal = False
        else:
            old_value = list(field_value.all().values_list("pk", flat=True))
            if old_value != new_value:
                is_equal = False

    elif isinstance(db_field, (admin_fields.FileForeignKey, admin_fields.ImageForeignKey)):
        from urllib import parse
        from django.conf import settings
        from file_manager.models import File
        if value:
            path = parse.unquote(value)
            path = path[len(settings.MEDIA_URL):]
            path = os.path.normpath(path)
            o_file = File.objects.filter(path=path).first()
            if o_file:
                new_value = o_file.pk
            else:
                new_value = None

            if old_obj is None:
                is_equal = False
            else:
                obj_sub = getattr(old_obj, db_field.name)
                if obj_sub:
                    old_value = getattr(obj_sub, db_field.to_fields[0])
                    if old_value != new_value:
                        is_equal = False
                else:
                    is_equal = False

    elif isinstance(db_field, (fields.related.ForeignKey, admin_fields.ForeignKey)):
        if old_obj is None:
            is_equal = False
        else:
            try:
                obj_sub = getattr(old_obj, db_field.name)
                old_value = getattr(obj_sub, db_field.to_fields[0])
                if old_value != new_value:
                    is_equal = False
            except (BaseException,):
                old_value = getattr(old_obj, field_name)
                if old_value != new_value:
                    is_equal = False

    # elif isinstance(db_field, (fields.BooleanField,)):
    #     new_value = False if value is ["", None] else bool(value)
    #     if (old_obj.pk is None) or (field_value != new_value):
    #         is_equal = False

    elif isinstance(db_field, (fields.NullBooleanField,)):
        new_value = None if value in ["", None] else bool(value)
        if (old_obj is None) or (field_value != new_value):
            is_equal = False

    # elif isinstance(db_field, admin_fields.ImageManagerField):
    #     is_save = False

    elif isinstance(db_field, (fields.IntegerField, fields.SmallIntegerField, fields.PositiveIntegerField)):
        new_value = None if value in ["", None] else int(value)
        if (old_obj is None) or (field_value != new_value):
            is_equal = False

    elif isinstance(db_field, (fields.FloatField, fields.DecimalField)):
        new_value = None if value in ["", None] else float(value)
        if (old_obj is None) or (field_value != new_value):
            is_equal = False

    elif isinstance(db_field, (admin_fields.UEditorField, admin_fields.HtmlField)):
        if value is None:
            pass
        elif not isinstance(value, str):
            new_value = str(value)

        if field_value != new_value:
            is_equal = False

    elif isinstance(db_field, (fields.TextField, fields.CharField)):
        import re
        # import jinja2
        from urllib import parse
        from django.utils.html import escape
        if isinstance(value, str) and re.search("<(.*)>", value.strip()):
            new_value = escape(value)  # xss注入转换
            # new_value = jinja2.escape(value)

        if value is None:
            pass
        elif not isinstance(value, str):
            new_value = str(value)

        if field_value != new_value:
            is_equal = False

    elif isinstance(db_field, (admin_fields.ImageField, admin_fields.FileField)):
        if db_field.multiple:
            new_value = []
            for path in value:
                new_value.append(path)
            if field_value is None:
                old_value = "[]"
            else:
                old_value = field_value.name if field_value.name else str([])
            new_value = str(new_value)
            if (old_obj is None) or (old_value != new_value):
                is_equal = False
        else:
            if value is None:
                new_value = None
            else:
                new_value = value
            if field_value is None:
                old_value = None
            else:
                old_value = field_value.name if field_value.name else None
            if (old_obj is None) or (old_value != new_value):
                is_equal = False

    elif (old_obj is None) or (field_value != new_value):
        is_equal = False

    return is_equal, new_value


def imitate_m2m_save(lst_save_id, sub_model, sub_field, dict_filter):
    """
    模拟ManyToMany保存
    """
    lst_save_id = lst_save_id or []
    lst_obj = []
    # dict_filter = {filter_field:obj,pk}
    lst_id = list(sub_model.objects.filter(**dict_filter).values_list(sub_field, flat=True))

    for obj_id in lst_save_id:
        dict_filter[sub_field] = obj_id
        obj = sub_model.objects.filter(**dict_filter).first()
        if obj is None:
            lst_obj.append(sub_model(**dict_filter))

        if obj_id in lst_id:
            lst_id.remove(obj_id)

    if lst_obj:
        sub_model.objects.bulk_create(lst_obj)

    if lst_id:
        dict_filter = {"%s__in" % sub_field: lst_id}
        sub_model.objects.filter(**dict_filter).delete()


def make_multilevel_data(queryset, name_field, parent_field, parent_field_value, data):
    for obj in queryset.filter(**{parent_field: parent_field_value}):
        children = []
        make_multilevel_data(queryset, name_field, parent_field, obj.pk, children)
        if children:
            data.append({"id": obj.pk, "label": getattr(obj, name_field), "expand": True, "children": children})
        else:
            data.append({"id": obj.pk, "label": getattr(obj, name_field)})


def change_list_update(request, app_label, model_name, display_mode=None):
    related_app_label = request.GET[const.UPN_RELATED_APP]
    related_model_name = request.GET[const.UPN_RELATED_MODEL]
    model_admin = admin_api.get_model_admin(app_label, model_name)
    # p_name = const.WN_PAGINATION % model_name
    # page_index = int(request.GET.get(p_name, 1))
    if display_mode is None:
        display_mode = request.GET.get(const.UPN_DISPLAY_MODE, None)

    o_theme = theme.get_theme(request.user.id)
    o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
    o_change_list = o_module.ChangeList(request, app_label, model_name, o_theme)

    related_model_admin = admin_api.get_model_admin(related_app_label, related_model_name)
    related_id = request.GET[const.UPN_RELATED_ID]
    related_field_name = request.GET[const.UPN_RELATED_FIELD]
    queryset = model_admin.get_queryset(request)
    queryset = admin_api.get_filter_queryset(request, model_admin, queryset)

    obj = None
    if related_model_admin and related_id:
        # queryset = queryset.filter(**{related_field_name: related_id})
        obj = related_model_admin.model.objects.filter(pk=related_id).first()
        # if related_model_admin:
        #     queryset = related_model_admin.get_inline_results(request, model_admin, queryset, obj)
        #     o_change_list.lst_display = related_model_admin.get_inline_list_display(request, model_admin, obj)

    if display_mode in [const.DM_FORM_POPUP, const.DM_LIST_CHILD]:  # 子表过滤
        if related_model_admin and obj:
            queryset = queryset.filter(**{related_field_name: related_id})
            queryset = related_model_admin.get_inline_results(request, model_admin, queryset, obj)
            o_change_list.lst_display = related_model_admin.get_inline_list_display(request, model_admin, obj)
        else:
            queryset = queryset.none()
        # o_change_list.display_mode = const.DM_LIST_CHILD

    # elif display_mode == const.DM_LIST_CHILD:
    #     if related_model_admin and obj:
    #         queryset = queryset.filter(**{related_field_name: related_id})
    #         queryset = related_model_admin.get_inline_results(request, model_admin, queryset, obj)
    #         o_change_list.lst_display = related_model_admin.get_inline_list_display(request, model_admin, obj)
    #     # o_change_list.display_mode = const.DM_LIST_CHILD

    else:  # 弹出过滤
        # db_field = related_model_admin.model._meta.get_field(related_field_name)
        if related_model_admin:
            db_field = admin_api.get_field(related_model_admin, related_field_name.split("|")[-1])
            queryset = related_model_admin.foreign_key_filter(request, queryset, db_field, obj)

    if display_mode:
        # o_change_list.display_mode = const.DM_LIST_CHILD
        o_change_list.display_mode = display_mode

    o_panel = o_change_list.make_list_view_child(queryset)
    result = step.WidgetUpdate(data=o_panel, mode="all")
    return result


def change_list_inline_update(request, parent_app_label, parent_app_model,
                              app_label, model_name, field_name, obj):
    """
    parent_app_label:父类app_label
    parent_app_model:父类model_name
    app_label:
    model_name:
    field_name:关联的字段名称
    obj:父类对象
    """
    # 更新页面的数据
    model_admin = admin_api.get_model_admin(parent_app_label, parent_app_model)
    obj_inline = admin_api.get_model_admin(app_label, model_name)
    o_theme = theme.get_theme(request.user.id)
    o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
    o_change_list = o_module.ChangeList(request, app_label, model_name, o_theme)
    # db_field = admin_api.get_field(obj_inline, fk_field_name)
    # field_name = "train_class_id"

    # obj = TrainClass.objects.filter(pk=train_class_id).first()
    if obj:
        queryset = obj_inline.model.objects.filter(**{field_name: obj.pk})
        queryset = model_admin.get_inline_results(request, obj_inline, queryset, obj)
        o_change_list.related_object_id = obj.pk
    else:
        queryset = obj_inline.model.objects.none()

    o_change_list.related_app_label = parent_app_label.lower()
    o_change_list.related_model_name = parent_app_model.lower()
    o_change_list.related_field_name = field_name
    o_change_list.display_mode = const.DM_LIST_CHILD
    o_change_list.lst_display = model_admin.get_inline_list_display(request, obj_inline, obj)
    return o_change_list.make_list_view_child(queryset)


def change_form(request, app_label, model_name, display_mode=None, object_id=None):
    object_id = object_id or request.GET.get('id', None)
    obj = None
    model_admin = admin_api.get_model_admin(app_label, model_name)
    if object_id:
        obj = model_admin.model.objects.filter(pk=object_id).first()

    o_theme = theme.get_theme(request.user.id)
    o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
    o_change_form = o_module.ChangeForm(request, model_admin, o_theme, obj)
    o_change_form.display_mode = display_mode
    o_grid = o_change_form.make_form_view()
    # if display_mode:
    #     o_grid.height = "100%" # 显示100%，超出部分没有滚动条
    return o_grid


def tree_node_add(request, model_admin, field_name, opera_data):
    value = request.GET.get(field_name, None)
    object_id = request.GET.get("id", None)
    db_field = admin_api.get_field(model_admin, field_name)

    model = model_admin.model
    dict_data = opera_data["data"]
    label = dict_data["label"]
    parent_id = dict_data["parent"]
    level = dict_data["level"]

    result = None
    if hasattr(db_field, "data"):  # 外键子表
        # 非同级
        if isinstance(db_field.data, (list, tuple)):
            pass

        else:
            model = db_field.data["model"]
            label_field = db_field.data["label_field"]
            dict_field = {label_field: label}
            if parent_id is not None:
                parent_field = db_field.data["parent_field"]
                dict_field[parent_field] = parent_id

            dict_field[db_field.data["level_field"]] = level

        obj_sub = model.objects.create(**dict_field)
        if level == 0:
            if value:
                lst_value = value.split(",")  # 多个一级
                lst_value.append(str(obj_sub.pk))
                value = ",".join(lst_value)
            else:
                value = "%s" % obj_sub.pk

            obj = None
            if object_id not in ["", None]:
                obj = model_admin.get_object(request, object_id)

            if obj:
                setattr(obj, field_name, value)
                obj.save()

            result = [step.WidgetUpdate(data={"name": field_name, "bind_value": value}),
                      step.OperaSuccess(data={"id": obj_sub.pk})]
        else:
            result = step.OperaSuccess(data={"id": obj_sub.pk})
    else:
        # dict_field = {field_name: label}
        #
        # if parent_id is not None:
        #     dict_field[parent_field] = parent_id
        #
        # obj_sub = model.objects.create(**dict_field)
        # result = step.OperaSuccess(data={"id": obj_sub.pk}),
        pass

    return result


def tree_node_del(request, model_admin, field_name, opera_data):
    value = request.GET.get(field_name, None)
    object_id = request.GET.get("id", None)
    db_field = admin_api.get_field(model_admin, field_name)
    dict_data = opera_data["data"]

    obj_id = dict_data["id"]
    level = dict_data["level"]
    model = db_field.data["model"]
    parent_field = db_field.data["parent_field"]
    lst_child_id = [[obj_id, ], ]
    while True:
        dict_filter = {"%s__in" % parent_field: lst_child_id[-1]}
        child_id = list(model.objects.filter(**dict_filter).values_list("pk", flat=True))
        if child_id:
            lst_child_id.append(child_id)
        else:
            break

    child_num = len(lst_child_id)
    for i in range(child_num - 1, -1, -1):
        model.objects.filter(pk__in=lst_child_id[i]).delete()

    result = None
    if level == 0:
        lst_value = value.split(",")  # 多个一级
        s_id = str(obj_id)
        if s_id in lst_value:
            lst_value.remove(s_id)
        value = ",".join(lst_value)

        obj = None
        if object_id not in ["", None]:
            obj = model_admin.get_object(request, object_id)

        if obj:
            setattr(obj, field_name, value)
            obj.save()

        result = [step.WidgetUpdate(data={"name": field_name, "bind_value": value})]

    return result


def tree_node_update(request, model_admin, field_name, opera_data):
    dict_data = opera_data["data"]
    obj_id = dict_data["id"]
    label = dict_data["label"]
    db_field = admin_api.get_field(model_admin, field_name)

    if hasattr(db_field, "data"):
        model = db_field.data["model"]
        label_field = db_field.data["label_field"]
        dict_field = {label_field: label}
    else:
        model = model_admin.model
        dict_field = {field_name: label}

    model.objects.filter(pk=obj_id).update(**dict_field)


def tree_node_order(rqeuest, model_admin, field_name, opera_data):
    pass
