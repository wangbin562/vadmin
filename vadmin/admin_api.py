# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
admin_api
"""
import base64
import collections
import copy
import json
import re
import datetime

from django.apps import apps as django_apps
from django.contrib import admin
from django.db.models import fields
from django.db import models
from django.core.exceptions import FieldError

from vadmin import const
from vadmin import admin_fields
from vadmin import step


def get_default_ordering(model_admin):
    try:
        # first try with the model admin ordering
        none, prefix, field_name = model_admin.ordering[0].rpartition('-')
        return '{}1'.format(prefix), field_name
    except (BaseException,):
        # then try with the model ordering
        try:
            none, prefix, field_name = model_admin.model._meta.ordering[0].rpartition('-')
            return '{}1'.format(prefix), field_name
        except (BaseException,):
            return "", ""


def parse_sort_para(request, model_admin, table_param=False):
    """
    解析排序参数（给排序使用）
    例如：
    o.table_name=-0+2 # 0列降序，2列升序
    """
    app_label = model_admin.opts.app_label
    model_name = model_admin.opts.model_name
    table_name = const.WN_TABLE % (app_label, model_name)
    key = "o.%s" % table_name  # 表格排序关键字

    related_app_label = request.GET.get(const.UPN_RELATED_APP, None)
    related_model_name = request.GET.get(const.UPN_RELATED_MODEL, None)
    if related_model_name:
        related_model_admin = get_model_admin(related_app_label, related_model_name)
        related_id = request.GET.get(const.UPN_RELATED_ID, None)
        if related_id:
            obj = related_model_admin.model.objects.filter(pk=related_id).first()
        else:
            obj = None
        lst_display = related_model_admin.get_inline_list_display(request, model_admin, obj)
    else:
        lst_display = model_admin.get_list_display(request)

    dict_sort = collections.OrderedDict()
    if key in request.GET:
        v = request.GET[key]
        s = v.replace(" ", "+")
        lst_sort_col = re.split(' *([+-]) *', s)
        del lst_sort_col[0]
        i = 0
        num = len(lst_sort_col)
        while i < num:
            col_idx = int(lst_sort_col[i + 1])
            # if model_admin.v_sortable:
            #     dict_sort[lst_display[col_idx - 1]] = lst_sort_col[i]
            # else:
            field_name = lst_display[col_idx]
            if table_param:
                dict_sort[field_name] = lst_sort_col[i]
            else:
                try:
                    db_field = get_field(model_admin, field_name)
                    dict_sort[field_name] = lst_sort_col[i]
                except (BaseException,):
                    fun = getattr(model_admin, field_name, None)
                    if fun and fun.field_name:
                        dict_sort[fun.field_name] = lst_sort_col[i]

            i += 2
    return dict_sort


def get_foreign_key_field(obj_inline, parent_model):
    """
    获取model和子表关联的字段
    :param obj_inline: 子表admin对象
    :param parent_model: 父表model
    :return: 子段名称
    """
    field_name = None
    for db_field in obj_inline.model._meta.fields:
        if hasattr(db_field, "to") and (db_field.to == parent_model):
            field_name = db_field.name
            break

        elif isinstance(db_field, (fields.related.ForeignKey, admin_fields.ForeignKey)) and \
                (db_field.target_field.model == parent_model):
            field_name = db_field.name  # 找到关联的外键(此处要优化)
            break

    return field_name


def get_deleted_objects(lst_obj, request, admin_site):
    from django.db import router
    # from django.db.models.deletion import Collector
    from django.contrib.admin.utils import NestedObjects

    try:
        obj = lst_obj[0]
    except IndexError:
        return [], set(), []
    else:
        using = router.db_for_write(obj._meta.model)
    collector = NestedObjects(using=using)
    collector.collect(lst_obj)
    perms_needed = set()

    def format_callback(obj):
        model = obj.__class__
        has_admin = model in admin_site._registry
        opts = obj._meta

        try:
            item = {"label": '%s: %s' % (opts.verbose_name, str(obj)), "expand": True}
        except (BaseException,):
            item = {}

        if has_admin:
            if not admin_site._registry[model].has_delete_permission(request, obj):
                perms_needed.add(opts.verbose_name)
                item = {}
            else:
                # url = const.URL_FORM_SHOW % (opts.app_label, opts.model_name, obj.pk)
                # o_step = step.Get(url=url)
                item = {"label": '%s: %s' % (opts.verbose_name, obj), "expand": True}
        return item

    deleted_objects = collector.nested(format_callback)
    protected = [format_callback(obj) for obj in collector.protected]
    # model_count = {model._meta.verbose_name_plural: len(objs) for model, objs in collector.model_objs.items()}

    return deleted_objects, perms_needed, protected


def get_field_value(obj, field_name, is_filter=False):
    value = None
    try:
        if is_filter:  # 过滤器不能等于默认值，必须为空
            value = None
        elif hasattr(obj, "%s_id" % field_name):
            value = getattr(obj, "%s_id" % field_name)
        elif hasattr(obj, field_name):  # m2m时，如果obj没有保存，此处会异常,
            value = getattr(obj, field_name)
    except (BaseException,):
        pass

    if value == fields.NOT_PROVIDED:
        value = None

    return value


def get_inline(request, model_admin, inline_name):
    fieldsets = model_admin.get_fieldsets(request)
    for fieldset in fieldsets:
        name, dict_field = fieldset

        for key, lst_field in dict_field.items():
            for field in lst_field:
                if isinstance(field, str):
                    continue

                if isinstance(field, (tuple, list)):
                    for sub_field in field:
                        if isinstance(sub_field, str):
                            continue

                        obj_inline = get_admin(sub_field)
                        if obj_inline.model._meta.model_name == inline_name:
                            return obj_inline
                else:
                    obj_inline = get_admin(field)
                    if obj_inline.model._meta.model_name == inline_name:
                        return obj_inline

    return get_model_admin(model_name=inline_name)


def get_model_admin(app_label=None, model_name=None):
    model_name = model_name.lower()
    model_admin = None
    if app_label is None:
        for model in django_apps.get_models():
            if model.__name__.lower() == model_name:
                model_admin = admin.site._registry.get(model)
                break
    else:
        model_name = model_name.lower()
        try:
            model = django_apps.get_model(app_label, model_name)
            model_admin = admin.site._registry.get(model)
        except (BaseException,):
            pass

    return model_admin


def get_model(app_label=None, model_name=None):
    model_name = model_name.lower()
    if "?" in model_name:
        model_name = model_name.split("?")[0].rstrip("/\\")

    model = None
    if app_label is None:
        for model in django_apps.get_models():
            if model.__name__.lower() == model_name:
                break
    else:
        model = django_apps.get_model(app_label, model_name)

    return model


def get_admin(admin_class):
    for k, v in admin.site._registry.items():
        if v.__class__ == admin_class:
            return v


def get_verbose_name(app_label=None, model_name=None):
    try:
        model = get_model(app_label, model_name)
        return model._meta.verbose_name
    except (BaseException,):
        return model_name


def get_field(model_admin, field_name):
    try:
        if "__" in field_name:
            field, field_sub = field_name.split("__")[0:2]
            db_field1 = model_admin.model._meta.get_field(field)
            # db_field1 = model_admin.opts.get_field(field)
            try:
                db_field = db_field1.related_model._meta.get_field(field_sub)
            except (BaseException,):
                db_field = db_field1.related_model._meta.get_field(field_sub + "_id")
        else:
            try:
                db_field = model_admin.model._meta.get_field(field_name)
                # db_field = model_admin.opts.get_field(field_name)
            except (BaseException,):
                db_field = model_admin.model._meta.get_field(field_name + "_id")
    except (BaseException,):
        try:
            db_field = model_admin.add_form.base_fields[field_name]
        except (BaseException,):
            raise ValueError(u'%s 错误的字段名称:%s' % (model_admin, field_name))

    return db_field


def get_field_name(model_admin, field_name):
    db_field = get_field(model_admin, field_name)
    return get_attname(db_field, field_name)


def get_field_and_name(model_admin, field_name):
    try:
        if "__" in field_name:
            field, field_sub = field_name.split("__")[0:2]
            db_field1 = model_admin.model._meta.get_field(field)
            # db_field1 = model_admin.opts.get_field(field)
            try:
                db_field = db_field1.related_model._meta.get_field(field_sub)
            except (BaseException,):
                db_field = db_field1.related_model._meta.get_field(field_sub + "_id")

            return db_field, "%s__%s" % (field, db_field.get_attname())
        else:
            try:
                db_field = model_admin.model._meta.get_field(field_name)
                # db_field = model_admin.opts.get_field(field_name)
            except (BaseException,):
                db_field = model_admin.model._meta.get_field(field_name + "_id")
    except (BaseException,):
        try:
            db_field = model_admin.add_form.base_fields[field_name]
        except (BaseException,):
            raise ValueError(u'错误的字段名称:%s！' % field_name)

    return db_field, db_field.get_attname()


def get_attname(db_field, field_name):
    """获取字段名称（外键加上_id）"""
    try:
        field_name = db_field.get_attname()
    except(BaseException,):
        pass

    return field_name


def get_field_by_model(model, field_name):
    db_field = model._meta.get_field(field_name)
    return db_field


def get_filter_queryset(request, model_admin, queryset=None):
    if queryset is None:
        queryset = model_admin.get_queryset(request)

    dict_para = {}
    for k, v in request.GET.items():
        if k.find(const.WN_FILTER_KEY) == 0:
            k = k.replace(const.WN_FILTER_KEY, "", 1)
        dict_para[k] = v

    app_label = model_admin.opts.app_label
    model_name = model_admin.opts.model_name
    search_name = const.WN_SEARCH % (app_label, model_name)
    if search_name in dict_para:
        search_term = dict_para.get(search_name, "")
        del dict_para[search_name]
    else:
        search_term = ""

    dict_sort = parse_sort_para(request, model_admin)

    lst_order = []
    for k, v in dict_sort.items():
        if v == "+":
            lst_order.append(k)
        else:
            lst_order.append("-%s" % k)

    lst_filter = model_admin.get_list_filter(request)

    lst_customize = []
    from vadmin import widgets
    for field in lst_filter:  # 处理自定义过滤器
        if callable(field):
            o_widget_filter = field()
            if isinstance(o_widget_filter, widgets.Panel):
                queryset = o_widget_filter.queryset(request, queryset, None, dict_para)
            elif o_widget_filter.get("name"):
                lst_customize.append(o_widget_filter.name)
                # 回调自定义过滤器
                if (o_widget_filter.name in dict_para) and (dict_para[o_widget_filter.name] is not None):
                    queryset = o_widget_filter.queryset(request, queryset, dict_para[o_widget_filter.name], dict_para)
            elif hasattr(field, "name") and field.name:
                lst_customize.append(field.name)
                # 回调自定义过滤器
                if (field.name in dict_para) and (dict_para[field.name] is not None):
                    queryset = o_widget_filter.queryset(request, queryset, dict_para[field.name], dict_para)

            elif hasattr(field, "parameter_name") and field.parameter_name:
                lst_customize.append(field.parameter_name)
                # 回调自定义过滤器
                if (field.parameter_name in dict_para) and (dict_para[field.parameter_name] is not None):
                    queryset = o_widget_filter.queryset(request, queryset, dict_para[field.parameter_name], dict_para)
            else:
                queryset = o_widget_filter.queryset(request, queryset, None, dict_para)

        elif isinstance(field, widgets.Widget):
            if field.name:
                lst_customize.append(field.name)
                # 回调自定义过滤器
                if (field.name in dict_para) and (dict_para[field.name] is not None):
                    queryset = field.queryset(request, queryset, dict_para[field.name], dict_para)
            else:
                queryset = field.queryset(request, queryset, None, dict_para)

    queryset_filter = {}
    for field_name, value in dict_para.items():
        if value in ["", None]:
            continue

        if field_name in lst_customize:
            continue

        if field_name in ["id"]:
            continue

        try:
            db_field, field_name = get_field_and_name(model_admin, field_name)
        except (BaseException,):
            continue

        if isinstance(db_field, models.CharField):
            import operator
            from functools import reduce
            or_queries = [models.Q(**{"%s__icontains" % field_name: value})]
            select = reduce(operator.or_, or_queries)
            queryset = queryset.filter(select)

        else:
            queryset_filter[field_name] = value

    if queryset_filter:
        queryset = queryset.filter(**queryset_filter)

    if lst_order:
        queryset = queryset.order_by(*lst_order)  # 界面控制排序
    elif model_admin.ordering:
        queryset = queryset.order_by(*model_admin.ordering)  # 使用model_admin配置排序
    elif model_admin.model._meta.ordering:
        queryset = queryset.order_by(*model_admin.model._meta.ordering)  # 使用model配置排序

    try:
        queryset, use_distinct = model_admin.get_search_results(request, queryset, search_term)
    except FieldError as e:
        pass

    return queryset


def get_submit_widget_data(request, widget_name=None):
    content = request.POST["content"]
    dict_contend = json.loads(content)
    if widget_name is None:
        return dict_contend[const.SUBMIT_WIDGET]

    return dict_contend[const.SUBMIT_WIDGET][widget_name]


def get_form_widgets(model_admin):
    v_widgets = {}
    if hasattr(model_admin, "form"):
        if hasattr(model_admin.form, "v_widgets"):
            for k, v in model_admin.form.v_widgets.items():
                if hasattr(model_admin.model, "%s_id" % k):
                    v_widgets["%s_id" % k] = v
                else:
                    try:
                        v_widgets[k] = v
                    except:
                        pass

    return v_widgets


def has_change_permission(request, model_admin, field_name, obj=None):
    """
    判断字段是否可以编辑
    """
    return model_admin.has_change_permission(request, obj) and (
            field_name not in model_admin.get_readonly_fields(request, obj))


def check_required(db_field, required_fields=None):
    required_fields = required_fields or []
    if hasattr(db_field, 'name') and db_field.name in required_fields:
        return True

    if hasattr(db_field, 'required'):
        if db_field.required:
            return True

    elif db_field.null or db_field.blank:
        return False

    return True


def format_date(obj, format=None):
    """格式化时间"""
    value = obj
    if isinstance(obj, datetime.datetime):
        value = obj.strftime('%Y-%m-%d %H:%M:%S')
    elif isinstance(obj, datetime.date):
        value = obj.strftime('%Y-%m-%d')
    elif isinstance(obj, datetime.time):
        value = obj.strftime('%H:%M:%S')

    return value


def calc_row_max_field_num(request, model_admin, obj, fieldsets):
    max_num = 1
    exclude_fields = model_admin.get_exclude(request, obj) or []
    for fieldset in fieldsets:
        name, dict_field = fieldset
        for key, lst_field in dict_field.items():
            if key == "classes":
                continue

            for field in lst_field:
                if isinstance(field, (tuple, list)):  # 多个(不支持inline)
                    lst_sub_field = []
                    for (i, sub_field) in enumerate(field):
                        if sub_field in exclude_fields:
                            continue

                        # if (sub_field == self.fk_field_name) or ("%s_id" % sub_field == self.fk_field_name):
                        #     continue

                        if hasattr(sub_field, "model"):
                            continue

                        lst_sub_field.append(sub_field)

                    field_num = len(lst_sub_field)
                    if field_num > max_num:
                        max_num = field_num
    return max_num


def get_queryset_total(request, model_admin, queryset, page_index=None, page_size=None):
    import math
    if isinstance(queryset, (list, tuple)):
        total = len(queryset)
    elif isinstance(queryset, int):
        total = queryset
    else:
        total = queryset.count()

    if not page_index:
        app_label = model_admin.opts.app_label
        model_name = model_admin.opts.model_name
        p_name = const.WN_PAGINATION % model_name
        page_index = int(request.GET.get(p_name, 1))

    if page_size is None:
        page_size = int(request.GET.get(const.UPN_PAGE_SIZE, model_admin.get_list_per_page(request)))
    page_total = math.ceil(total / page_size)
    begin = (int(page_index) - 1) * page_size
    end = begin + page_size
    # if begin > total:
    #     begin = total

    if end > total:
        end = total

    return total, page_total, begin, end


def get_opera_col_width(data):
    opera_icon_number = 0
    for row_data in data:
        if isinstance(row_data[-1], (list, tuple)):
            number = len(row_data[-1])

            if number > opera_icon_number:
                opera_icon_number = number

    width = opera_icon_number * 36
    if width < 60:
        width = 60

    return width


def get_widget_width(request, o_widget, default_width=220):
    width = o_widget.get("width")
    if isinstance(width, (float, int)):
        pass

    else:
        width = 0
        if o_widget.type in ["panel"]:
            if o_widget.get("width"):
                width = o_widget.width
            else:
                for item in o_widget.get_children():
                    if item.type == "text":
                        width += (len(item.text) * 8)
                    else:
                        width += default_width

        elif o_widget.type in ["button"]:
            if o_widget.get("width"):
                width = o_widget.width
            else:
                from utils import word_api
                from vadmin import theme
                o_theme = theme.get_theme(request.user.id)

                font_size = 14
                if "font" in o_theme.button and "size" in o_theme.button["font"] and \
                        isinstance(o_theme.button["font"]["size"], int):
                    font_size = o_theme.button["font"]["size"]
                elif "size" in o_theme.font and isinstance(o_theme.font["size"], int):
                    font_size = o_theme.font["size"]

                width = word_api.get_text_width(o_widget.text, font_size) + 20
                if o_widget.get("prefix"):
                    width += 10

                if o_widget.get("suffix"):
                    width += 10

                width = 80 if width < 80 else width

        else:
            width = default_width

    return width
