# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
admin_api
"""
import os
import jinja2

from django.contrib import admin
from django.db.models import fields
from django.forms import fields as forms_fields
from django.forms import widgets as forms_widgets
from django.db.models.query import QuerySet
from vadmin import admin_api
from vadmin import admin_fields
from vadmin import common
from vadmin import const
from vadmin import event
from vadmin import step
from vadmin import widgets


def make_field_widget(request, obj, model_admin, field_name,
                      required_fields=None, readonly_fields=None,
                      readonly=False, is_popup=False):
    """
    form中一个字段对应组件数据(一般三个，字段说明、字段输入、字段帮助，字段检查提示由前台填加）
    :param request:
    :param obj:对象，如果是增加情况使用get_default_object方法，获取默认对象
    :param model_admin:
    :param field_name:字段名称
    :param required_fields:是否为必填字段 (前端检查是否为空）
    :param readonly_fields:是否为只读只读（前端disabled)
    # :param add_pk:name中是否要增加id
    # :param help_icon:是否用icon显示帮助
    :param readonly:只读字段是否用readonly_text显示
    :param is_popup:是否为弹出框
    :return:
    """
    lst_widget1 = []
    lst_widget2 = []
    change = True
    if (field_name in readonly_fields) or ("%s_id" % field_name in readonly_fields):
        change = False
    else:
        if obj and obj.pk:
            if not model_admin.has_change_permission(request, obj):
                change = False
        else:
            if not model_admin.has_change_permission(request):
                change = False

    fun = getattr(model_admin, field_name, None) or getattr(model_admin, "form_v_%s" % field_name, None)
    if callable(fun):
        if obj and obj.pk:
            result = make_customize_field_widget(request, model_admin, fun.__name__, obj, readonly=readonly)
        else:
            result = make_customize_field_widget(request, model_admin, fun.__name__, readonly=readonly)

        if result != const.USE_TEMPLATE:
            return result

    # 二级
    if "__" in field_name:
        field1, field2 = field_name.split("__")[0:2]
        db_field1 = admin_api.get_field(model_admin, field1)
        db_field = admin_api.get_field_by_model(db_field1.related_model, field2)
        try:
            obj_sub = getattr(obj, field1)
        except (BaseException,):
            obj_sub = None

        related_model_admin = admin.site._registry.get(db_field1.related_model)
        fun = getattr(related_model_admin, field2, None) or getattr(related_model_admin, "form_v_%s" % field2, None)

        if callable(fun):
            result = make_customize_field_widget(request, related_model_admin, fun.__name__, obj_sub, readonly=readonly)
            if result != const.USE_TEMPLATE:
                return result

    else:
        db_field = admin_api.get_field(model_admin, field_name)

    if admin_api.check_required(db_field, required_fields):
        try:
            text = str(db_field.verbose_name)
        except (BaseException,):
            text = str(db_field.label)
        o_text = widgets.Text(text="%s:  *  " % text, keyword="*", keyword_color="#FF0000")
    else:
        o_text = widgets.Text(text="%s:     " % db_field.verbose_name)
    lst_widget1.append(o_text)

    lst_expand = []
    o_widget = field_2_widget(request, model_admin, field_name, obj, lst_expand=lst_expand)

    if o_widget:
        if readonly:
            o_widget.readonly = True
        else:
            o_widget.disabled = not change

        lst_widget2.append(o_widget)

    if change and (not is_popup) and (not readonly):
        lst_widget2.extend(lst_expand)

    if db_field.help_text:
        o_icon = widgets.Icon(icon="el-icon-info", color="#ff0000",
                              tooltip=str(db_field.help_text),
                              tooltip_interval_time=100,
                              padding=[0, 5, 0, 5])
        lst_widget2.append(o_icon)

    return lst_widget1, lst_widget2


def make_customize_field_widget(request, model_admin, field_name, obj=None, readonly=False):
    """构造自定义字段"""
    required_fields = model_admin.get_required_fields(request, obj)
    if not readonly:
        readonly = model_admin.has_readonly_text(request, obj)
    change = model_admin.has_change_permission(request, obj) and \
             (field_name not in model_admin.get_readonly_fields(request, obj))

    if obj and obj.pk:
        dict_customize = getattr(model_admin, field_name)(request, obj)
    else:
        dict_customize = getattr(model_admin, field_name)(request, None)

    if dict_customize == const.USE_TEMPLATE:
        return dict_customize

    if (not isinstance(dict_customize, (dict, tuple, list, widgets.Widget))) and (dict_customize is not None):
        return const.USE_TEMPLATE

    lst_widget1 = []
    lst_widget2 = []
    if isinstance(dict_customize, dict):
        if "name" in dict_customize:
            if not dict_customize["name"]:
                o_text = None
            elif field_name in required_fields:
                o_text = widgets.Text(text="%s:  *  " % dict_customize["name"], keyword="*", keyword_color="#FF0000")
            else:
                o_text = widgets.Text(text="%s:     " % dict_customize["name"])
            lst_widget1.append(o_text)

        lst_widget = dict_customize.get("widget", [])
        if not isinstance(lst_widget, (tuple, list)):
            lst_widget = [lst_widget, ]

        for o_widget in lst_widget:
            if o_widget is None:
                pass

            elif isinstance(o_widget, dict):
                if readonly:
                    o_widget["readonly"] = readonly
                else:
                    o_widget["disabled"] = not change

                if field_name in required_fields:
                    o_widget["required"] = True
            else:
                if readonly:
                    o_widget.readonly = readonly
                elif o_widget.get("disabled") is None:
                    o_widget.disabled = not change

                if field_name in required_fields:
                    o_widget.required = True

            lst_widget2.append(o_widget)

    elif dict_customize:
        if not isinstance(dict_customize, (tuple, list)):
            lst_widget = [dict_customize, ]
        else:
            lst_widget = dict_customize

        for o_widget in lst_widget:
            if o_widget is None:
                continue

            if isinstance(o_widget, dict):
                if readonly:
                    o_widget["readonly"] = readonly
                else:
                    o_widget["disabled"] = not change

            elif isinstance(o_widget, widgets.Widget):
                # o_widget.round = 3
                if readonly:
                    o_widget.readonly = readonly
                elif o_widget.get_attr_value("disabled") is None:
                    o_widget.disabled = not change

            lst_widget1.append(o_widget)

    return lst_widget1, lst_widget2


def field_2_widget(request, model_admin, field_name, obj=None, value=None,
                   is_filter=False, is_edit=False, lst_expand=None, is_list=None):
    """
    :param request:
    :param model_admin:
    :param field_name: 字段名称
    :param obj:
    :param is_filter: 是否为过滤器上组件
    :param is_edit: 是否列表编辑（列表中编辑字段，不能有radio和checkbox, 全部用select)
    :param value: 已有值，不用获取默认值
    :param lst_expand: 需要在后面显示的操作组件
    :param is_list:是否再change_list界面
    :return:
    """
    if lst_expand is None:
        lst_expand = []

    change = True
    if obj is None:
        change = False
        obj = model_admin.get_default_object(request)
    elif obj.pk is None:
        change = False

    related_model_admin = None
    if "__" in field_name:
        name = field_name
        field1, field2 = field_name.split("__")[0:2]
        try:
            value = getattr(getattr(obj, field1), field2)
        except (BaseException,):
            pass
        db_field1 = admin_api.get_field(model_admin, field1)
        related_model_admin = admin.site._registry.get(db_field1.related_model)
        db_field = admin_api.get_field_by_model(db_field1.related_model, field2)
    else:
        db_field = admin_api.get_field(model_admin, field_name)
        field_name = admin_api.get_attname(db_field, field_name)  # 获取带ID的字段名称
        name = field_name
        if value is None:
            value = admin_api.get_field_value(obj, field_name, is_filter)

    app_label = model_admin.opts.app_label
    model_name = model_admin.opts.model_name
    o_widget = None
    if isinstance(db_field, (admin_fields.ImageField, fields.files.ImageField,
                             fields.files.FileField, admin_fields.FileField)):
        """要重写控件"""
        data = []
        if related_model_admin:
            url = const.URL_UPLOAD_FILE_MODEL % (related_model_admin.opts.app_label,
                                                 related_model_admin.opts.model_name, field_name)
        else:
            url = const.URL_UPLOAD_FILE_MODEL % (app_label, model_name, field_name)
        o_widget = widgets.Upload(text="点击上传", upload_url=url)

        if isinstance(db_field, (admin_fields.ImageField, fields.files.ImageField)):
            o_widget.theme = "image"
            o_widget.width = getattr(db_field, "width", 120)
            o_widget.height = getattr(db_field, "height", 120)
        else:
            o_widget.theme = "file"

        o_widget.multiple = getattr(db_field, "multiple", False)
        if value:
            if o_widget.multiple:
                try:
                    lst_path = eval(value.name)
                except (BaseException,):
                    lst_path = [value.name]

                for path in lst_path:
                    if path in ["", None]:
                        continue
                    file_name = os.path.split(path)[-1]
                    data.append({"name": file_name, "url": path})
            else:
                path = value.name
                file_name = os.path.split(path)[-1]
                data = {"name": file_name, "url": path}
            o_widget.data = data

    elif isinstance(db_field, admin_fields.ImageManagerField):
        """图片管理字段"""
        pass

    elif isinstance(db_field, admin_fields.TreeField):
        url = const.URL_TREE_OPERA % (app_label, model_name, field_name)
        url = common.make_url(url, request,
                              param={field_name: "{{js.getAttrValue('%s', 'bind_value')}}" % field_name},
                              only=["id", field_name])
        o_widget = widgets.Tree(select=db_field.select and "multiple" or "single",
                                opera_url=url,
                                min_height=200, width=600, edit=1, bind_value=value)
        o_widget.data = make_tree_widget_data(request, model_admin, db_field, o_widget, value)

    elif isinstance(db_field, admin_fields.UEditorField):
        if db_field.upload_url:
            upload_url = db_field.upload_url
        else:
            upload_url = const.URL_UPLOAD_UEDITOR % (app_label, model_name, field_name)
        o_widget = widgets.Rich(value=value, upload_url=upload_url, width=db_field.width, height=db_field.height)

    elif isinstance(db_field, admin_fields.ColorField):
        o_widget = widgets.ColorPicker(value=value)

    elif isinstance(db_field, admin_fields.VideoField):
        o_widget = widgets.Video(href=value, width=db_field.width, height=db_field.height)

    elif isinstance(db_field, admin_fields.CheckboxField):
        value = common.get_choices_value(db_field.choices, value)
        o_widget = widgets.Checkbox(data=list(db_field.choices), value=value)

    elif isinstance(db_field, (fields.BooleanField, fields.NullBooleanField)):
        if is_filter:
            value = int(value) if value else value
            o_widget = widgets.Select(data=[[1, u"是"], [0, u"否"]], value=value)
        else:
            o_widget = widgets.Switch(value=value)

    elif isinstance(db_field, admin_fields.SelectFilterField):
        # 要重写处理
        if db_field.choices:
            value = common.get_choices_value(db_field.choices, value)
            o_widget = widgets.Select(value=value, data=list(db_field.choices))
            # if change:
            #     select_change_url = const.URL_SELECT_CHANGE % (app_label, model_name, field_name) + \
            #                         "%s/" % obj.pk
            # else:
            #     select_change_url = const.URL_SELECT_CHANGE % (app_label, model_name, field_name)
            # o_step = step.Post(url=select_change_url, submit_type="event")
            # o_widget.event = {"type": "change", "step": o_step}

        else:
            o_widget = widgets.Input(value=value)

    elif isinstance(db_field, fields.CharField):
        if value:
            value = jinja2.utils.Markup(value).unescape()  # xss注入回转显示

        if db_field.choices:
            o_widget = widgets.Select(value=value, data=list(db_field.choices))
        else:
            o_widget = widgets.Input(value=value)

    elif isinstance(db_field, forms_fields.CharField):  # 自定义的字段类型，不支持choices
        if value:
            value = jinja2.utils.Markup(value).unescape()

        if isinstance(db_field.widget, forms_widgets.PasswordInput):  # 加密
            from django.conf import settings
            o_widget = widgets.Input(input_type="password", value=value, max_length=db_field.max_length,
                                     encrypt=settings.V_PWD_ENCRYPT_KEY)
        elif getattr(db_field, "choices", []):
            o_widget = widgets.Select(value=value, data=list(db_field.choices))

        else:
            o_widget = widgets.Input(value=value, max_length=db_field.max_length)

    elif isinstance(db_field, fields.TextField):
        if value:
            # value = parse.unquote(value)
            value = jinja2.utils.Markup(value).unescape()
        o_widget = widgets.Input(input_type="textarea", value=value)

    elif isinstance(db_field, fields.DateTimeField):
        if value:
            try:
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            except (BaseException,):
                pass
        o_widget = widgets.DateTimePicker(value=value)

    elif isinstance(db_field, fields.DateField):
        if value:
            try:
                value = value.strftime("%Y-%m-%d")
            except (BaseException,):
                pass
        o_widget = widgets.DatePicker(value=value, format=getattr(db_field, "format", "YYYY-mm-dd"))

    elif isinstance(db_field, fields.TimeField):
        if value:
            try:
                value = value.strftime("%H:%M:%S")
            except (BaseException,):
                pass
        o_widget = widgets.TimePicker(value=value)

    elif isinstance(db_field, (fields.IntegerField, fields.PositiveIntegerField, fields.AutoField,
                               fields.PositiveSmallIntegerField, fields.SmallIntegerField,
                               fields.BigIntegerField, fields.BigAutoField)):

        if value not in [None, "", "None"]:
            value = int(value)

        if db_field.choices:
            o_widget = widgets.Select(value=value, data=list(db_field.choices))

        else:
            o_widget = widgets.Input(input_type="number", value=value)

    elif isinstance(db_field, (fields.FloatField, fields.DecimalField)):
        if value not in [None, "", "None"]:
            value = float(value)

        if db_field.choices:
            o_widget = widgets.Select(value=value, data=list(db_field.choices))
        else:
            o_widget = widgets.Input(input_type="number", value=value)

    elif isinstance(db_field, fields.related.OneToOneField):
        pass

    elif isinstance(db_field, fields.related.ManyToManyField):
        if is_filter or is_edit:
            data = []
            for obj_related in db_field.remote_field.model.objects.select_related():
                data.append([obj_related.pk, str(obj_related)])

            if value not in ["", None] and data:
                if isinstance(data[0][0], int):
                    value = int(value)
                else:
                    value = str(value)

            o_widget = widgets.Select(data=data, value=value)
        else:
            data = []
            queryset = db_field.remote_field.model.objects.select_related()
            queryset = model_admin.m2m_filter(request, queryset, db_field, obj)
            for obj_related in queryset:
                data.append([obj_related.pk, str(obj_related)])

            if change and obj.pk:
                value = list(getattr(obj, field_name).all().values_list("pk", flat=True))
            else:
                value = []

            o_widget = widgets.Transfer(data=data, value=value, width=300, height=300)
        pass

    elif isinstance(db_field, admin_fields.CascadeFilterForeignKey):
        pass

    elif isinstance(db_field, admin_fields.FileForeignKey):
        try:
            path = getattr(obj, db_field.name).get_url()
        except (BaseException,):
            path = None

        o_widget = widgets.Upload(value=path, resume_url=const.URL_UPLOAD_FILE_RESUME % "/")

    elif isinstance(db_field, admin_fields.ImageForeignKey):
        try:
            path = getattr(obj, db_field.name).get_url()
        except (BaseException,):
            path = None

        o_widget = widgets.Upload(value=path, theme="image")

    elif isinstance(db_field, fields.related.ForeignKey):
        if value not in ["", None]:
            if isinstance(db_field.foreign_related_fields[0], (fields.AutoField,)):
                value = int(value)
            else:
                value = str(value)

        o_widget = widgets.Select(value=value)
        make_foreign_key_widget(request, model_admin, db_field, o_widget, value, obj, change,
                                is_filter=is_filter)
        if not is_filter:
            change_form_config = model_admin.get_change_form_config(request, obj)
            if not is_edit:
                lst_field = change_form_config.get("foreign_key_link", None)
                if (lst_field is None) or (field_name in lst_field):
                    o_icon = make_foreign_key_link(request, model_admin, field_name, obj, value)
                    lst_expand.append(o_icon)

            lst_field = change_form_config.get("foreign_key_select", None)
            if (lst_field is None) or (field_name in lst_field):
                o_icon = make_foreign_key_select(request, model_admin, field_name, obj, value, is_edit)
                lst_expand.append(o_icon)

    else:
        # o_widget = widgets.Input(value=value)
        raise ValueError(u'未支持的widget类型！')

    if o_widget is not None:
        # if isinstance(o_widget, (widgets.Select, widgets.Checkbox, widgets.Radio, widgets.Switch)):
        try:
            o_event = make_select_change(request, model_admin, db_field, obj)
            if o_event:
                o_widget.add_event(o_event)
        except (BaseException,):
            pass

        required_fields = model_admin.get_required_fields(request, obj)
        if admin_api.check_required(db_field, required_fields):
            if o_widget.type not in ["checkbox_bool", "slider", "switch"]:
                o_widget.required = True

        if not is_filter:
            v_widgets = admin_api.get_form_widgets(model_admin)
            # 自定义字段(如用户表password1）没有name属性
            if (field_name in v_widgets or (getattr(db_field, "name", None)) in v_widgets) \
                    and not is_filter:  # 过滤器不能用自定义的
                # if field_name in v_widgets:
                o_widget_form = v_widgets[field_name]
                # try:
                o_widget = field_2_form_widget(o_widget, o_widget_form)
                # except:
                #     pass

        if is_filter:
            o_widget.required = False

        o_widget.name = name

        # if hasattr(o_widget, "cascade_filter") and o_widget.cascade_filter:
        #     o_widget.model_name = model_name

    return o_widget


def field_2_form_widget(o_widget, o_widget_form):
    for k, v in o_widget_form.__dict__.items():
        if k == "type" and v == "widget":
            continue

        elif v is None:
            continue

        setattr(o_widget, k, v)

    return o_widget


def field_2_list_widget(request, model_admin, field_name, obj=None):
    """
    字段转换成change_list上显示组件
    :param request:
    :param model_admin:
    :param field_name: 字段名称
    :param obj:
    :return:
    """

    o_widget = None
    if obj is None:
        obj = model_admin.get_default_object(request)

    db_field = admin_api.get_field(model_admin, field_name)
    value = admin_api.get_field_value(obj, field_name)
    if value is None:
        return None

    if isinstance(db_field, (fields.BooleanField, fields.NullBooleanField)):
        if value:
            o_widget = widgets.Icon(icon="el-icon-success", font={"color": const.COLOR_SUCCESS, "size": 14})
        else:
            o_widget = widgets.Icon(icon="el-icon-error", font={"color": const.COLOR_ERROR, "size": 14})

    elif isinstance(db_field, admin_fields.ColorField):
        o_widget = widgets.ColorPicker(value=value, disabled=True)

    elif isinstance(db_field, admin_fields.ImageField):
        if (not db_field.multiple) and (value and value.name):
            o_widget = widgets.Image(href=value.name, height=40)
        else:
            o_widget = value

    elif isinstance(db_field, admin_fields.FileField):
        if value and value.name:
            o_widget = widgets.Upload(theme="default", value=value.name,
                                      multiple=db_field.multiple, disabled=True)
        else:
            o_widget = None

    # elif isinstance(db_field, admin_fields.ImageManagerField):
    #     to_obj = db_field.to.objects.filter(pk=value).first()
    #     if to_obj:
    #         if to_obj.image_thumb:
    #             o_widget = widgets.Image(href=to_obj.image_thumb.url, height=40, text_horizontal="left")
    #         elif to_obj.image:
    #             o_widget = widgets.Image(href=to_obj.image.url, height=40, text_horizontal="left")
    #         else:
    #             o_widget = widgets.Text(text=value, text_horizontal="left")
    #     else:
    #         o_widget = widgets.Text(text=value, text_horizontal="left")

    elif isinstance(db_field, admin_fields.DateField):
        if db_field.format == "YYYY-mm-dd":
            value = value.strftime("%Y-%m-%d")
        elif db_field.format == "YYYY-mm":
            value = value.strftime("%Y-%m")
        elif db_field.format == "YYYY":
            value = value.strftime("%Y")
        elif db_field.format == "mm":
            value = value.strftime("%m")

        o_widget = value

    elif isinstance(db_field, fields.CharField):
        if db_field.choices:
            o_widget = common.transform_choices(db_field, value)
        else:
            o_widget = value

    elif isinstance(db_field, forms_fields.CharField):  # 自定义的字段类型，不支持choices
        if isinstance(db_field.widget, forms_widgets.PasswordInput):
            o_widget = "*" * 6
        else:
            o_widget = value

    elif isinstance(db_field, fields.TextField):
        o_widget = value

    elif isinstance(db_field, fields.DateTimeField):
        value = value.strftime("%Y-%m-%d %H:%M:%S")
        o_widget = value

    elif isinstance(db_field, fields.DateField):
        value = value.strftime("%Y-%m-%d")
        o_widget = value

    elif isinstance(db_field, fields.TimeField):
        value = value.strftime("%H:%M:%S")
        o_widget = value

    elif isinstance(db_field, (fields.IntegerField, fields.PositiveIntegerField, fields.AutoField,
                               fields.PositiveSmallIntegerField, fields.SmallIntegerField,
                               fields.BigIntegerField, fields.BigAutoField,
                               fields.FloatField, fields.DecimalField)):
        if db_field.choices:
            o_widget = common.transform_choices(db_field, value)
        else:
            o_widget = value

    elif isinstance(db_field, fields.related.OneToOneField):
        pass

    elif isinstance(db_field, fields.related.ManyToManyField):
        data = []
        for obj_related in getattr(obj, field_name).all()[0:5]:
            data.append(str(obj_related))

        o_widget = ",".join(data)

    elif isinstance(db_field, (fields.related.ForeignKey, admin_fields.ForeignKey)):  # 外键
        try:
            # 有可能数据库中保存了ID，但关联数据已删除，会报异常
            foreign_key_obj = getattr(obj, field_name, None)  # 穿过来的参数确保不带ID
            if foreign_key_obj:
                value = str(foreign_key_obj)
        except (BaseException,):
            pass

        o_widget = value

    elif isinstance(db_field, fields.files.ImageField):
        o_widget = value

    elif isinstance(db_field, fields.files.FileField):
        o_widget = value
    else:
        o_widget = str(value)

    return o_widget


def field_2_list_links(request, model_admin, field_name, obj, lst_filter_name):
    """
    字段转成列表链接字段
    """
    text = " "
    db_field = admin_api.get_field(model_admin, field_name)
    try:
        value = None
        if "__" in field_name:
            field1, field2 = field_name.split("__")[0:2]
            try:
                value = getattr(getattr(obj, field1), field2)
            except (BaseException,):
                pass
        else:
            value = getattr(obj, field_name)

        text = value or " "
        if isinstance(db_field, admin_fields.DateField):
            if value is not None:
                if db_field.format == "YYYY-mm-dd":
                    text = value.strftime("%Y-%m-%d")
                elif db_field.format == "YYYY-mm":
                    text = value.strftime("%Y-%m")
                elif db_field.format == "YYYY":
                    text = value.strftime("%Y")
                elif db_field.format == "mm":
                    text = value.strftime("%m")
        elif db_field.choices:
            text = common.transform_choices(db_field, value)
            text = text or " "
        else:
            text = str(text)
    except (BaseException,):
        pass

    url = model_admin.get_change_form_url(request, obj)
    url = common.make_url(url, request, filter=[const.UPN_TOP_ID, const.UPN_SCREEN_WIDTH,
                                                const.UPN_SCREEN_HEIGHT, const.UPN_STEPS_IDX])
    o_step = step.Post(url=url, jump=True, section=lst_filter_name)
    o_widget = widgets.Text(text=text, step=o_step, font={"decoration": "underline", "color": "#0088CC"}, tooltip=True)
    return o_widget


def make_foreign_key_widget(request, model_admin, db_field, o_widget, value, obj, change,
                            parent_model_admin=None, is_filter=False):
    """
    构造外键数据，同时要增加切换响应事件
    """
    field_name = db_field.name
    field = "pk"
    if db_field.to_fields and db_field.to_fields[0]:
        field = db_field.to_fields[0]
        if field is None:
            field = "pk"

    data = []
    queryset = db_field.formfield().queryset
    # if not is_filter:
    if change:
        queryset = model_admin.foreign_key_filter(request, queryset, db_field, obj)
    else:
        queryset = model_admin.foreign_key_filter(request, queryset, db_field)

    if value not in ["", None]:  # 默认值有可以不在前50条，先增加
        foreign_obj = queryset.filter(**{field: value}).first()
        if foreign_obj:
            data.append([getattr(foreign_obj, field), str(foreign_obj)])
            o_widget.value = value
        # else:
        #     o_widget.value = None
        s_value = str(value)
    else:
        s_value = None

    for foreign_obj in queryset[0:50]:  # 最多50条, 多了用搜索
        obj_value = getattr(foreign_obj, field)
        s_obj_value = str(obj_value)
        if s_obj_value == s_value:
            continue

        data.append([obj_value, str(foreign_obj)])

    o_widget.data = data
    count = len(data)

    if count >= 50:  # 大于50条增加远程搜索
        if parent_model_admin:
            parent_app_name = parent_model_admin.model._meta.app_label
            parent_model_name = parent_model_admin.model._meta.model_name
        else:
            parent_app_name = None
            parent_model_name = None

        app_label = model_admin.model._meta.app_label
        model_name = model_admin.model._meta.model_name
        search_field = None
        if hasattr(db_field, "search_field"):
            search_field = db_field.search_field

        if not search_field and hasattr(o_widget, "search_field"):
            search_field = o_widget.search_field

        if hasattr(db_field, "related_model"):  # related_model 和 rel 不同django版本匹配
            if not search_field:
                related_model_admin = admin.site._registry.get(db_field.related_model)
                if related_model_admin:
                    search_field = related_model_admin.get_search_fields(request)

            if search_field:
                o_widget.set_remote_method(parent_app_name, parent_model_name,
                                           app_label, model_name, field_name,
                                           db_field.related_model._meta.app_label,
                                           db_field.related_model._meta.model_name,
                                           search_field, obj.pk)

        elif hasattr(db_field, "rel"):  # 只有外键的情况下支持搜索
            if not search_field:
                related_model_admin = admin.site._registry.get(db_field.rel)
                if related_model_admin:
                    search_field = related_model_admin.get_search_fields(request)

            if search_field:
                o_widget.set_remote_method(parent_app_name, parent_model_name,
                                           app_label, model_name, field_name,
                                           db_field.rel._meta.app_label,
                                           db_field.rel._meta.model_name,
                                           search_field, obj.pk)

    # 增加切换响应事件
    script = "{{setAttrValue('%s_link','hide', getCurrentValue() == '' ? true : false)}}" % field_name
    o_event = event.Event(type="change", step=step.RunJs(script=script))
    o_widget.add_event(o_event)

    return queryset


def query_foreign_key_data(request, model_admin, db_field, obj, value):
    data = []

    field = "pk"
    if db_field.to_fields and db_field.to_fields[0]:
        field = db_field.to_fields[0]
        if field is None:
            field = "pk"

    queryset = db_field.formfield().queryset
    if value not in ["", None]:  # 默认值有可以不在前50条，先增加
        foreign_obj = queryset.filter(**{field: value}).first()
        if foreign_obj:
            data.append([getattr(foreign_obj, field), str(foreign_obj)])
        # else:
        #     o_widget.value = None

    queryset = model_admin.foreign_key_filter(request, db_field.formfield().queryset, db_field, obj)

    s_value = str(value)
    for foreign_obj in queryset[0:50]:  # 最多50条, 多了用搜索
        obj_value = getattr(foreign_obj, field)
        s_obj_value = str(obj_value)
        if s_obj_value == s_value:
            continue

        data.append([obj_value, str(foreign_obj)])

    return data


def make_foreign_key_select(request, model_admin, field_name, obj, value, is_edit):
    """构造外键选择链接图标按钮"""

    # model 没有注册不支持(上一个model_admin实际是inline）
    db_field = admin_api.get_field(model_admin, field_name)
    related_app_label = db_field.related_model._meta.app_label
    related_model_name = db_field.related_model._meta.model_name

    related_model_admin = admin_api.get_model_admin(related_app_label, related_model_name)
    from vadmin import admin
    if isinstance(related_model_admin, admin.VModelAdmin):
        o_icon = None
        foreign_key_select_fields = model_admin.get_foreign_key_select_fields(request, obj)
        if (foreign_key_select_fields is None) or (field_name in foreign_key_select_fields):
            db_field = admin_api.get_field(model_admin, field_name)
            if isinstance(db_field, (fields.related.ForeignKey, admin_fields.ForeignKey)):
                url = const.URL_LIST_POPUP % (db_field.related_model._meta.app_label,
                                              db_field.related_model._meta.model_name)
                if is_edit:  # 表格
                    url = common.make_url(url, param={
                        const.UPN_OBJECT_ID: "{{js.getBeforeValue('value')}}",
                        const.UPN_WIDGET_ID: "{{js.getBeforeValue('id')}}",
                        const.UPN_RELATED_FIELD: "{{js.getBeforeValue('name')}}",
                        const.UPN_RELATED_ID: obj.pk,
                        const.UPN_DISPLAY_MODE: const.DM_LIST_SELECT,
                        const.UPN_RELATED_APP: model_admin.model._meta.app_label,
                        const.UPN_RELATED_MODEL: model_admin.model._meta.model_name,
                    })
                else:  # 非表格
                    url = common.make_url(url, param={
                        const.UPN_OBJECT_ID: "{{js.getValue('%s')}}" % field_name,
                        const.UPN_RELATED_FIELD: field_name,
                        const.UPN_RELATED_ID: obj.pk,
                        const.UPN_DISPLAY_MODE: const.DM_LIST_SELECT,
                        const.UPN_RELATED_APP: model_admin.model._meta.app_label,
                        const.UPN_RELATED_MODEL: model_admin.model._meta.model_name,
                    })
                o_step = step.Get(url=url, jump=False)
                o_icon = widgets.Icon(icon="el-icon-sort", tooltip="切换", size=16, step=o_step, margin_left=10)

        return o_icon


def make_foreign_key_link(request, model_admin, field_name, obj, value):
    """构造外键选择链接图标按钮"""
    from vadmin import admin
    db_field = admin_api.get_field(model_admin, field_name)
    related_app_label = db_field.related_model._meta.app_label
    related_model_name = db_field.related_model._meta.model_name

    related_model_admin = admin_api.get_model_admin(related_app_label, related_model_name)
    try:
        obj_sub = getattr(obj, db_field.name, None)
    except (BaseException,):
        obj_sub = None

    if isinstance(related_model_admin, admin.VModelAdmin) and obj_sub and \
            related_model_admin.has_change_permission(request, obj_sub):

        name = "%s_link" % field_name
        url = const.URL_FORM_POPUP % (related_app_label, related_model_name)
        url = common.make_url(url, param={"object_id": "{{js.getValue('%s')}}" % field_name,
                                          const.UPN_RELATED_APP: model_admin.opts.app_label,
                                          const.UPN_RELATED_MODEL: model_admin.opts.model_name,
                                          const.UPN_RELATED_FIELD: field_name,
                                          const.UPN_RELATED_TO_FIELD: db_field.to_fields[0] or
                                                                      db_field.foreign_related_fields[0].name
                                          })
        o_step = step.Get(url=url, jump=False)
        o_icon = widgets.Icon(name=name, icon="el-icon-edit", tooltip="编辑", size=16, step=o_step, margin_left=10)
        if value is None:
            o_icon.hide = True
        return o_icon


def make_select_change(request, model_admin, db_field, obj, is_list=False):
    change_fields = model_admin.get_change_form_change_fields(request, obj)
    o_event = None
    # 适配有_id和没有_id的情况
    field_name1 = db_field.name
    field_name = db_field.get_attname()
    if (field_name1 in change_fields) or (field_name in change_fields):
        app_label = model_admin.opts.app_label
        model_name = model_admin.opts.model_name
        if obj and obj.pk:
            url = const.URL_FORM_FIELD_CHANGE % (app_label, model_name, field_name, obj.pk)
        else:
            url = const.URL_FORM_FIELD_CHANGE % (app_label, model_name, field_name, "")

        object_id = request.GET.get("id", "")
        if is_list:
            url = common.make_url(url, param={"value": "{{js.getCurrentValue()}}",
                                              "object_id": object_id,
                                              "row_id": obj.pk})
        else:
            url = common.make_url(url, param={"value": "{{js.getCurrentValue()}}",
                                              # "node_name": "{{js.getCurrentAttrValue('name')}}",
                                              # "node_id": "{{js.getCurrentAttrValue('id')}}",
                                              "object_id": object_id,
                                              "row_id": "{{js.getRowId('%s')}}" % field_name})  # object_id 父类ID，inline使用到
        o_event = {"change": step.Post(url=url, submit_type="no")}

    return o_event


def make_tree_widget_data(request, model_admin, db_field, o_widget, value):
    """
    # [{"model": TreeLevel1, "label_field": "name", "order_field": "order"},
        {"model": TreeLevel2, "label_field": "name", "order_field": "order", "parent_field": "tree_level_1_id"},
        {"model": TreeLevel3, "label_field": "name", "order_field": "order", "parent_field": "tree_level_2_id"}
    #  ]
    """

    # value = "1,"

    def make_tree_data(db_field, level, dict_field, dict_filter, tree_data):
        model_num = len(db_field.data)

        for obj_id, label in dict_field["model"].objects.filter(**dict_filter). \
                order_by(dict_field["order_field"]).values_list("pk", dict_field["label_field"]):
            node_data = {"id": obj_id, "label": label, "expand": True, }
            tree_data.append(node_data)

            if level + 1 == model_num:
                continue

            node_data["children"] = []
            dict_field_sub = db_field.data[level + 1]
            dict_filter_sub = {dict_field_sub["parent_field"]: obj_id}
            make_tree_data(db_field, level + 1, dict_field_sub, dict_filter_sub, node_data["children"])

    def make_tree_data_by_same(level, dict_field, dict_filter, tree_data):
        for obj_id, label in dict_field["model"].objects.filter(**dict_filter). \
                order_by(dict_field["order_field"]).values_list("pk", dict_field["label_field"]):
            node_data = {"id": obj_id, "label": label, "expand": True, "children": []}
            tree_data.append(node_data)
            dict_filter_sub = {dict_field["parent_field"]: obj_id}
            make_tree_data_by_same(level + 1, dict_field, dict_filter_sub, node_data["children"])

    data = []
    level = 0
    if isinstance(db_field.data, (list, tuple)):
        if value is not None:
            dict_filter = {"pk__in": eval("[%s]" % value)}
            make_tree_data(db_field, level, db_field.data[level], dict_filter, data)
    else:
        if value is not None:
            dict_filter = {"pk__in": eval("[%s]" % value), db_field.data["level_field"]: level}
            make_tree_data_by_same(level, db_field.data, dict_filter, data)

    return data
