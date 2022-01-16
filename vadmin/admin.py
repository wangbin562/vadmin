# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
vadmin admin
"""
# import pickle
import json

from django.apps import apps as django_apps
from django.contrib import admin
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType
from django.db import transaction
from django.forms.models import ModelForm
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache
from django.conf import settings

site = admin.site

from vadmin import service
from vadmin import const
from vadmin import widgets
from vadmin import step
from vadmin import menu
from vadmin import event
from vadmin import common
from vadmin.models import GroupEx
from vadmin.models import PermissionEx


class VModelAdmin(admin.ModelAdmin):
    """

    """
    # 自定义列表显示，可以显示外键数据，用"__"双下划线分割，最多支持二级，此字段不支持链接，不支持编辑
    list_v_display = []
    # 自定义列表中显示的字段不要和model中field name重名，如果重名，会导致form中字段也认为自定义

    list_v_filter = []  # vadmin定义的过滤字段，整个过滤字段等于list_filter + list_v_filter
    readonly_v_fields = []
    list_v_editable = []

    # 使用导出excel功能，须pip install openpyxl
    export = True  # has_export接口返回
    # 导出配置, 在v_export = True 时生效
    # 导出excel, {"title": {"field":"name"}, "field": [], "width": {1:100, "field_2":200}, "file_path":"导出文件存储路径",
    # "file_url":"导出文件url路径", "file_name":"导出文件名称"}
    # title:字段名称，为空时使用model verbose_name
    # fields:导出字段, model中字段名称，为空时导出所有字段
    # width:导出列宽，单位px，为空时宽度自适应,同时支持字段名称或列号为key,列号从1开始
    # file_path:导出文件存储路径，配置了file_path关键字，必须配置file_url
    # file_name:导出文件名称
    # title、field、width、file_path、file_name可以单个或全部为空
    # async:导出是否异步，默认False，在大数据量是可以配置异步
    export_config = {"async": True}  # get_export_config接口返回

    search_placeholder = None  # 搜索窗口中默认显示的提示信息，默认显示最后一个字段

    # 自定义组件（在list"Add"按钮前面增加）
    change_list_custom = []  # 组件列表

    # 自定义组件 (在list"导出"按钮后面增加）
    change_list_batch_custom = []  # 组件列表

    # 自定义组件（在form"Save"按钮前面增加）
    change_form_custom = []  # 组件列表

    # 自定义列表页面行操作组件
    row_opera_custom = []

    # 自定义组件（在"导出"按钮后面增加）
    list_change_list_batch_add = []

    # 自定义组件（在弹出选择界面过滤后面显示，如果自定义就没有vadmin的确定）
    # list_v_button_popup = []

    # change_from界面接口（可以自定义）
    change_form_url = const.URL_FORM

    # 自定义单条记录增加界面(只有在增加和编辑界面不一样的情况下，才会用到，比如user表）
    change_form_add_url = const.URL_FORM_ADD

    # change_list界面接口（可以自定义）
    change_list_url = const.URL_LIST

    # 列表表格配置
    # "col_width": {"field": 100, "field2": 200} # 列宽
    # "col_fixed":{"left":0, "right":-1} # 列固定（支持负数）
    # "col_horizontal":{"field":"left", "field2":"right"} # 列水平对其方式 "left":左 "center":中 "right":右
    # "col_name":{"field":"aa", "field2":"bb"}} # 自定义字段名称
    # "row_opera":True # 是否行操作列
    # "order":True # 是否可以拖动排序，如果为True时，必须有"order"， "create_time"字段，且ordering第一个须等于order字段
    # "tree_table":False 是否用树表格显示
    # "parent_field":父类字段，tree等于True时生效
    # "parent_value":父类值，tree等于True时生效
    # "foreign_key_field": 父类外键字段，tree等于True时生效
    # "tree_level":tree显示到的级别(从1开始), tree等于True时生效, 如果有显示级别则支持懒加载
    change_list_config = {}

    # 列表过滤配置
    # fold: 过滤区域是否折叠
    # width: 单个过滤控件的宽度
    change_list_filter_config = {"fold": True}

    # 表单配置
    # "change_fields": 支持change事件回调的的字段（支持的select、radio组件)
    # "foreign_key_link": 显示外键链接字段，默认全部显示, 等于None全部显示，等于[]全部不显示
    # "foreign_key_select":  显示外键选择字段，默认全部显示, 等于None全部显示，等于[]全部不显示
    change_form_config = {}

    tabs = []
    # 支持loading_method、tab_position、tab_width
    tabs_config = {}

    # 步骤配置
    steps = []
    steps_config = {}

    collapses = []  # 折叠

    list_per_page = 20  # 显示的最大行数

    # 子表配置
    # v_inlines = []  # 没有外键时，使用inlines会报错，所以用v_inlines替换，v_inlines和inlines都兼容
    # inline_collapse = False  # 子表显示form是否折叠
    # inline_collapse_label_field = None  # 子表折叠时label上显示内容对应字段的名称
    # 子表是否叠放显示（默认列表显示）
    # 列表显示时，使用的是list_v_display配置
    # 叠放form表单显示时，使用的是fieldsets配置
    # inline_stacked = False
    # inline_change_list = False  # 子表是否使用change_list方式显示（此时有过滤和弹出增加）

    # 子表配置
    # Admin:子表Admin
    # fields:子表显示的字段
    # col_width:子表列宽
    # order：子表是否排序
    # display:stacked:叠放显示 tabular:表格显示 list:admin表格显示 field col_width在stacked状态生效
    # {Admin:{"fields":[], "col_width":""}}
    inline_config = {}

    # 自定义字段
    # 表单字段 form_v_xxxx
    # 列表字段 list_v_xxxx
    # 导出字段 export_v_xxxx

    def __init__(self, model, admin_site):
        super(VModelAdmin, self).__init__(model, admin_site)
        self.dict_filter = {}
        self.lst_order = []
        self.workflow_param = {}

    def set_workflow_param(self, **kwargs):
        """
        设置工作流参数
        """
        self.workflow_param = kwargs

    def has_add_permission(self, request):
        if settings.V_SUPPORT_MENU_PERMISSIONS:
            if self.opts.label in settings.V_SUPPORT_MENU_PERMISSIONS:
                return True

        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        if settings.V_SUPPORT_MENU_PERMISSIONS:
            if self.opts.label in settings.V_SUPPORT_MENU_PERMISSIONS:
                return True

        return super().has_delete_permission(request, obj)

    def has_change_permission(self, request, obj=None):
        if settings.V_SUPPORT_MENU_PERMISSIONS:
            if self.opts.label in settings.V_SUPPORT_MENU_PERMISSIONS:
                return True

        return super().has_change_permission(request, obj)

    def has_readonly_text(self, request, obj=None):
        """
        所以字段是否显示文字
        """
        return False

    def has_order(self, request):
        """列表是否可以上下拖动排序"""
        return self.change_list_config.get("order", False)

    def has_export(self, request):
        """列表是否支持导出"""
        return self.export

    def has_row_opera(self, request):
        """列表是否有默认操作列"""
        return self.change_list_config.get("row_opera", True)

    def has_change_form_opera(self, request):
        """表单是否有操作区域"""
        return True

    def get_list_per_page(self, request):
        """获取页面显示条数"""
        return self.list_per_page

    def get_list_display(self, request):
        """获取列表显示列"""
        return self.list_v_display or self.list_display

    def get_list_filter(self, request):
        """获取过滤字段"""
        return self.list_v_filter or self.list_filter

    def get_list_editable(self, request, obj=None):
        """获取列表编辑字段字段"""
        return self.list_v_editable or self.list_editable

    def get_readonly_fields(self, request, obj=None):
        """获取只读字段"""
        return self.readonly_v_fields or self.readonly_fields

    def get_fieldsets(self, request, obj=None):
        """
        获取form页面布局配置
        如果obj=None,使用add_fieldsets
        """
        fieldsets = super(VModelAdmin, self).get_fieldsets(request, obj)
        return fieldsets

    def get_required_fields(self, request, obj=None):
        """获取必填字段, 如果model中设置成必填项"""
        required_fields = []
        fields = super().get_fields(request, obj)
        for field in fields:
            try:
                db_field = self.model._meta.get_field(field)
            except (BaseException,):
                continue

            if not (db_field.null or db_field.blank):
                required_fields.append(field)
        return required_fields

    def get_change_form_fields(self, request, obj):
        return service.get_change_form_fields(self, request, obj)

    # def get_search_results(self, request, queryset, search_term=""):
    #     """
    #     列表过滤
    #     :param request:
    #     :param queryset:
    #     :param search_term: 搜索关键字
    #     :return:
    #     """
    #     queryset, use_distinct = super(VModelAdmin, self).get_search_results(request, queryset, search_term)
    #     return queryset, user_distinct

    def get_exclude(self, request, obj=None):
        """
        Hook for specifying exclude.
        """
        return self.exclude

    def get_tabs(self, request, obj=None):
        """获取tab显示数据"""
        return self.tabs

    def get_tabs_config(self, request, obj=None):
        """获取tab显示方向"""
        return self.tabs_config

    def get_steps(self, request, obj=None):
        return self.steps

    def get_steps_config(self, request, obj=None):
        return self.steps_config

    def get_collapses(self, request, obj=None):
        """获取折叠显示数据"""
        return self.collapses

    def get_export_config(self, request):
        """获取导出配置"""
        return self.export_config

    def get_menu_value(self, request, obj=None):
        """获取菜单值，如果是非标准，比如一个model定义多个菜单时，要重写此函数"""
        menu_value = self.opts.label_lower
        return menu_value

    def get_default_object(self, request):
        """
        获取默认对象，obj.pk等于None
        """
        obj = self.model._meta.model()
        return obj

    # def get_default_value(self, request, obj=None):
    #     """
    #     获取默认值 {"字段名称":"value"}
    #     """
    #     return {}

    def get_object(self, request, object_id, from_field=None):
        """根据ID获取对象"""
        obj = super().get_object(request, object_id, from_field)
        return obj

    def get_change_list_url(self, request, page_index=None, obj=None):
        """获取列表页面URL"""
        if self.change_list_url == const.URL_LIST:
            app_label, model_name = self.opts.label_lower.split(".")
            p_name = const.WN_PAGINATION % model_name
            if page_index is None:
                page_index = int(request.GET.get(p_name, 1))

            if page_index != 1:
                url = self.change_list_url % (app_label, model_name) + "?%s=%s" % (p_name, page_index)
            else:
                url = self.change_list_url % (app_label, model_name)
        else:
            url = self.change_list_url
        url = common.make_url(url, request, filter=["id", const.UPN_STEPS_IDX])
        return url

    def get_change_form_url(self, request, obj=None):
        """获取表单页面URL"""
        if self.change_form_url == const.URL_FORM:
            app_label, model_name = self.opts.label_lower.split(".")
            if obj and obj.pk:
                url = self.change_form_url % (app_label, model_name)
                url = common.make_url(url, param={"id": obj.pk})
            else:
                url = self.change_form_url % (app_label, model_name)
        else:
            url = self.change_form_url

        url = common.make_url(url, request)
        return url

    def get_change_form_add_url(self, request):
        """获取表单增加页面URL"""
        if self.change_form_add_url == const.URL_FORM_ADD:
            app_label, model_name = self.opts.label_lower.split(".")
            url = self.change_form_add_url % (app_label, model_name)
        else:
            url = self.change_form_add_url
        url = common.make_url(url, request)
        return url

    def get_change_list_config(self, request):
        return self.change_list_config

    def get_change_list_filter_config(self, request):
        return self.change_list_filter_config

    # def get_col_sort_field(self, request):
    #     """获取表头列排序字段"""
    #     return self.change_list_config.get("sort_fields", [])

    def get_row_opera_custom(self, request, obj):
        """获取自定义行操作组件"""
        return self.row_opera_custom

    def get_change_list_custom(self, request):
        """
        获取list页面自定义组件（在搜索和增加按钮中间）
        """
        return self.change_list_custom

    def get_change_list_batch_custom(self, request, o_template=None):
        """
        返回增加的自定义批量操作组件（在"导出"后面）
        """
        return self.change_list_batch_custom

    def get_change_form_config(self, request, obj=None):
        """获取表单配置"""
        return self.change_form_config

    def get_change_form_change_fields(self, request, obj=None):
        """获取表单配置"""
        change_fields = self.change_form_config.get("change_fields", [])
        if not isinstance(change_fields, (tuple, list)):
            change_fields = [change_fields, ]
        return change_fields

    def get_foreign_key_link_fields(self, request, obj=None):
        """获取外键快捷切换配置"""
        return self.change_form_config.get("foreign_key_link", None)

    def get_foreign_key_select_fields(self, request, obj=None):
        """获取外键链接配置"""
        return self.change_form_config.get("foreign_key_select", None)

    def get_change_form_custom(self, request, obj=None):
        """
        获取form页面自定义功能按钮（在"保存"前面）
        """
        return self.change_form_custom

    # def get_actions(self, request):
    #     """获取批量操作"""
    #     return self.actions

    ############################## 过滤数据 #######################################
    def get_search_results(self, request, queryset, search_term):
        """搜索过滤"""
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct

    def foreign_key_filter(self, request, queryset, db_field, obj=None):
        """
        过滤外键
        :param request:
        :param queryset: 外键queryset
        :param db_field:外键字段
        :param obj:当前对象（非外键）
        :return:
        """
        return queryset

    def m2m_filter(self, request, queryset, db_field, obj=None):
        """m2m字段过滤"""
        return queryset

    def export_filter(self, request, queryset):
        """导出过滤"""
        return queryset

    ##################################### 事件 #######################################
    def select_change(self, request, db_field, value, obj=None, is_change=True):
        """数据切换后回调（要先配置支持）
        is_change:初始化时等于False
        """
        pass

    # def check(self, request, old_obj, obj, save_data, update_data,
    #             m2m_data, dict_error, inline_data=None, change=True):
    #     """
    #     :param request:
    #     :param old_obj: 老对象（如果change=False, 则old_obj等于None)
    #     :param obj:新对象（没保存前，obj.pk等于None)
    #     :param save_data:界面提交数据 格式：{"field_1":"value_1","field_2":"value_2"} ForeignKey类型字段名称有"_id",
    #     ManyToManyField类型值等数组
    #     :param update_data:界面提交和数据库中不一样的数据 格式：{"field_1":"value_1","field_2":"value_2"}
    #     :param m2m_data:ManyToManyField字段数据
    #     :param dict_error:错误数据，格式：{field_name: _("This field is required.")}
    #     :param inline_data:子表数据 格式：{"city":{"delete":[1,2], "add":[{}, {}], "edit":[{}, {}]}}
    #     :param change:是否修改，为True时为新增
    #     :return:界面弹出提示信息
    #     """
    #     # 检查界面提交的数据
    #     service.fields_check(request, self, save_data, dict_error, obj)
    #     # if inline_data:
    #     #     service.inline_check(request, self, inline_data, dict_error, obj)
    #     return None

    def save_before(self, request, old_obj, data, dict_error, inline_data=None):
        """
        保存前调用,数据没有格式化和检查之前调用，一般使用场景是在检查前赋值使用
        :param request:
        :param old_obj: 老对象（如果等于None，则为新建)
        :param data:界面提交数据 格式：{"field_1":"value_1","field_2":"value_2"} ForeignKey类型字段名称有"_id",没有格式化处理
        :param dict_error:错误数据，格式：{field_name: _("This field is required.")}
        :param inline_data:子表数据 格式：{"city":{"delete":[1,2], "add":[{}, {}], "edit":[{}, {}]}}
        :return:界面弹出提示信息，可以不返回
        """
        return None

    def save_after(self, request, old_obj, obj, save_data, update_data,
                   m2m_data, dict_error, inline_data=None, change=True):
        """
        保存(在保存后会调用）,保存使用save_model函数
        :param request:
        :param old_obj: 老对象（如果change=False, 则old_obj等于None)
        :param obj:新对象（已保存，obj.pk不等于None)
        :param save_data:界面提交的数据，已格式化处理 格式：{"field_1":"value_1","field_2":"value_2"} ForeignKey类型字段名称有"_id",
        ManyToManyField类型值等数组
        :param update_data:界面提交和数据库中不一样的数据，已格式化处理 格式：{"field_1":"value_1","field_2":"value_2"}
        :param m2m_data:ManyToManyField字段数据
        :param dict_error:错误数据，格式：{field_name: _("This field is required.")}
        :param inline_data:子表数据
        :param change:是否修改，为True时为新增
        :return:界面弹出提示信息
        """
        return None

    # def create_model(self, request, dict_data):
    #     return self.model.objects.create(**dict_data)

    def delete_model(self, request, obj):
        from vadmin_standard.models import LogicallyDelete
        o_delete = LogicallyDelete.objects.filter(app_label=self.opts.app_label, model_name=self.opts.model_name,
                                                  enable=True).first()
        if o_delete:
            setattr(obj, o_delete.field_name, True)
            obj.save()
        else:
            super().delete_model(request, obj)

    ################################## 子表配置 #############################
    def delete_inline(self, request, obj_inline, lst_object_id):
        """
        子表删除接口
        :param request:
        :param obj_inline:
        :param lst_object_id:
        :return:
        """
        obj_inline.model.objects.filter(pk__in=lst_object_id).delete()

    def get_inline_results(self, request, obj_inline, queryset, obj=None):
        """
        子表过滤接口
        :param request:
        :param obj_inline:子表InlineModelAdmin对象
        :param queryset:子表queryset
        :param obj:父对象，新建时为空
        :return:
        """
        queryset, use_distinct = obj_inline.get_search_results(request, queryset, None)
        return queryset

    def get_inline_default(self, request, obj_inline, obj=None):
        """
        获取子表默认值（增加默认值）
        :param request:
        :param obj_inline:子表InlineModelAdmin对象
        :param obj:父对象，新建时为空
        :return: 默认的子对象
        例：
        lst_sub_obj = []
        # inline.model生成对象，数据库没有创建，不能用创建inline.model.create()
        # name="A"赋值给界面默认显示值
        lst_sub_obj.append(inline.model(name="A", del_flag=False))
        lst_sub_obj.append(inline.model(name="B", del_flag=False))
        lst_sub_obj.append(inline.model(name="C", del_flag=False))
        """
        lst_sub_obj = []
        return lst_sub_obj

    def get_inline_list_display(self, request, obj_inline, obj=None):
        """获取inline显示的字段名"""
        inline = type(obj_inline)
        if inline in self.inline_config:
            if "fields" in self.inline_config[inline]:
                return self.inline_config[inline]["fields"]

        return obj_inline.fields or obj_inline.get_list_display(request)

    def get_inline_fieldsets(self, request, obj_inline, obj=None):
        inline = type(obj_inline)
        if inline in self.inline_config:
            if "fieldsets" in self.inline_config[inline]:
                return self.inline_config[inline]["fieldsets"]

        return obj_inline.get_fieldsets(request, obj)

    def get_inline_config(self, request, obj_inline, obj=None):
        """获取子表配置"""
        inline = type(obj_inline)
        if inline in self.inline_config:
            return self.inline_config[inline]

        return obj_inline.change_list_config

    def get_inline_col_width(self, request, obj_inline, obj=None):
        """获取子表配置的列宽"""
        inline = type(obj_inline)
        if inline in self.inline_config:
            if "col_width" in self.inline_config[inline]:
                return self.inline_config[inline]["col_width"]

        change_list_config = obj_inline.get_change_list_config(request)
        return change_list_config.get("col_width", {})

    def get_inline_display_effect(self, request, obj_inline, obj=None):
        """获取inline显示效果
        # 子表配置
        # Admin:子表Admin
        # fields:子表显示的字段
        # col_width:子表列宽
        # order：子表是否排序
        # display:stacked:叠放显示 tabular:表格显示 list:admin表格显示 field col_width在stacked状态生效
        # {Admin:{"field":[], "col_width":""}}
        inline_config = {}
        """
        inline = type(obj_inline)
        if inline in self.inline_config:
            if "display" in self.inline_config[inline]:
                return self.inline_config[inline]["display"] or const.INLINE_DISPLAY_TABULAR

        return const.INLINE_DISPLAY_TABULAR

    ################################## end #################################

    ################################## 界面重写 #############################
    def make_list_select_all(self, request, o_template, filter_name=None):
        app_label = self.opts.app_label
        model_name = self.opts.model_name
        table_name = const.WN_TABLE % (app_label, model_name)
        o_step = step.WidgetOpera(
            name=table_name,
            opera=const.OPERA_TABLE_SELECT_ALL,
            data={"value": "{{js.getCurrentValue()}}"})
        o_widget1 = widgets.CheckboxBool(name=const.WN_SELECT_ALL, margin_left=10, margin_right=8,
                                         value=request.GET.get(const.WN_SELECT_ALL, False),
                                         event={"change": o_step})

        o_widget2 = widgets.Text(text="选择全部", margin_right=10)
        return o_widget1, o_widget2

    def make_list_delete(self, request, o_template, filter_name):
        """批量删除按钮"""
        app_label = self.opts.app_label
        model_name = self.opts.model_name
        url = common.make_url(const.URL_LIST_DEL_VIEW % (app_label, model_name), request)
        table_name = const.WN_TABLE % (app_label, model_name)
        o_step = step.Get(url=url,
                          splice=filter_name + [table_name, const.WN_SELECT_ALL])
        o_button = widgets.Button(icon="el-icon-delete", text="删除", step=o_step, margin_right=10)
        return o_button

    def make_list_search(self, request, o_template, filter_name, url=None):
        """列表页搜索按钮"""
        if url is None:
            model_name = self.opts.model_name
            p_name = const.WN_PAGINATION % model_name
            change_list = self.get_change_list_url(request)
            url = common.make_url(change_list, request, filter=["id", p_name, const.UPN_STEPS_IDX])

        o_step = step.Post(url=url, jump=True, submit_type="hide", splice=filter_name)
        o_icon = widgets.Icon(icon="el-icon-search")
        o_button = widgets.Button(prefix=o_icon, text="搜索", step=o_step)
        return o_button

    def make_list_add(self, request, o_template, filter_name):
        """列表页增加按钮"""
        url = self.get_change_form_add_url(request)
        o_step = step.Post(url=url, submit_type="hide", jump=True, splice=filter_name)
        prefix = widgets.Icon(icon="el-icon-circle-plus-outline")
        o_button = widgets.Button(prefix=prefix, text="增加", step=o_step)
        return o_button

    def make_list_export(self, request, o_template):
        """列表页面导出按钮"""
        app_label = self.opts.app_label
        model_name = self.opts.model_name
        url = const.URL_LIST_EXPORT % (app_label, model_name)
        url = common.make_url(url, request)

        table_name = const.WN_TABLE % (app_label, model_name)
        o_step = step.Post(url=url, submit_type="section", section=[table_name, const.WN_SELECT_ALL])
        prefix = widgets.Icon(icon="el-icon-download")
        o_button = widgets.Button(prefix=prefix, text=u"导出", step=o_step, margin_right=10)
        return o_button

    # def make_list_close(self, request, related_model_admin, related_field_name, related_object_id):
    #     """列表页面关闭按钮（弹出时）"""
    #     o_button = widgets.Button(text="确定")
    #     url = const.URL_LIST_POPUP_SELECT % (related_model_admin.opts.app_label,
    #                                          related_model_admin.opts.model_name,
    #                                          related_field_name,
    #                                          related_object_id)
    #     url = common.make_url(url, request)
    #     o_event = event.Event(type="click", step=step.Post(url=url, submit_type="layer"))
    #     o_button.add_event(o_event)
    #     return o_button

    def make_list_save(self, request, o_template):
        """列表页面保存按钮"""
        app_label = self.opts.app_label
        model_name = self.opts.model_name
        url = const.URL_LIST_SAVE % (app_label, model_name)
        url = common.make_url(url, request)

        table_name = const.WN_TABLE % (app_label, model_name)
        o_step = step.Post(url=url, submit_type="section", section=[table_name, ])
        # prefix = widgets.Icon(icon="el-icon-coin")
        o_button = widgets.Button(prefix="v-save", text=u"保存", step=o_step, margin_right=10)
        return o_button

    def make_list_row_delete(self, request, obj):
        """列表页面行删除按钮"""
        return const.USE_TEMPLATE

    def make_list_row_save(self, request, obj):
        """列表页面行保存按钮"""
        return const.USE_TEMPLATE

    def make_list_row_edit(self, request, obj, filter_name):
        """列表页面行编辑按钮"""
        return const.USE_TEMPLATE

    def make_list_title(self, request, o_template):
        """
        构造头部标题区域，默认使用模板
        """
        return None

    def make_list_filter(self, request, o_template):
        """
        构造过滤器区域，默认使用模板
        """
        return None

    def make_list_table(self, request, o_template, queryset):
        """
        构造表格区域，默认使用模板
        """
        return None

    def make_list_top_area(self, request, o_template):
        """
        构造列表页面头部区域
        """
        return None

    def make_list_pagination(self, request, o_template, queryset):
        """构造分页"""
        return const.USE_TEMPLATE

    def make_list_bottom_area(self, request, o_template):
        """
        构造列表页面底部区域，默认使用模板
        """
        return None

    def make_list_hover(self, request, o_template):
        """
        构造列表页面悬浮区
        """
        return None

    def make_form_title(self, request, o_template, obj=None):
        """
        构造头部标题区域，默认使用模板
        """
        return None

    def make_form_next(self, request, o_template, obj=None):
        """表单页面下一步按钮"""
        return const.USE_TEMPLATE

    def make_form_prev(self, request, o_template, obj=None):
        """表单页面上一步按钮"""
        return const.USE_TEMPLATE

    def make_form_save(self, request, o_template, obj=None):
        """表单页面保存按钮"""
        return const.USE_TEMPLATE

    def make_form_save_edit(self, request, o_template, obj=None):
        """表单页面保存编辑按钮"""
        return const.USE_TEMPLATE

    def make_form_save_add(self, request, o_template, obj=None):
        """表单页面保存增加按钮"""
        return const.USE_TEMPLATE

    def make_form_save_copy_add(self, request, o_template, obj=None):
        """表单页面保存复制增加按钮"""
        return const.USE_TEMPLATE  # 默认使用模板，同时单个admin也可以自定义

    def make_form_delete(self, request, o_template, obj=None):
        """表单页面删除按钮"""
        return const.USE_TEMPLATE

    def make_form_close(self, request, o_template):
        """表单页面关闭按钮"""
        return const.USE_TEMPLATE

    def make_form_save_close(self, request, o_template, obj=None):
        """表单页面保存并关闭按钮(弹出层）"""
        return const.USE_TEMPLATE

    def make_form_top_area(self, request, o_template):
        return None

    def make_form_hover(self, request, o_template):
        """
        构造表单页面悬浮区
        """
        return None

    def make_form_save_area(self, request, o_template):
        """构造表单页面保存区域"""
        return None

    ###################################### begin 子表界面 ##################################################
    def make_inline_delete(self, request, obj_inline, obj_sub=None, obj=None):
        """构造子表删除按钮"""
        return const.USE_TEMPLATE

    def make_inline_add(self, request, obj_inline, row_data, obj=None):
        """构造子表增加按钮"""
        return const.USE_TEMPLATE

    def make_inline_custom(self, request, obj_inline, row_data=None, obj=None):
        """构造子表自定义按钮"""
        return None

    ###################################### end 子表 ######################################################


class GroupForm(ModelForm):
    v_widgets = {
        'name': widgets.Widget(width=690),
        'key': widgets.Widget(width=690),
        'desc': widgets.Input(input_type="textarea", width=690),
    }


@admin.register(GroupEx)
class GroupExAdmin(VModelAdmin):
    """
    权限组
    """
    form = GroupForm
    list_display = ["name", 'key', 'desc', 'del_flag']
    list_v_filter = ['del_flag', ]
    fieldsets = (
        (None, {'fields': ('name', 'key', 'desc', 'del_flag', 'permission', 'other_permission')}),
    )

    change_list_config = {"col_width": {'del_flag': 80}, "order": True}

    def permission(self, request, obj=None):
        """自定义permission组件"""
        from vadmin import menu
        o_group_ex = GroupEx.objects.filter(key="BASE_MENU").first()
        if (o_group_ex is None) or (o_group_ex.tree_data is None):
            o_group_ex = menu.MenuAuthManage(is_all=True).init_menu_permission()
        tree_data = json.loads(o_group_ex.tree_data)
        if obj and obj.tree_value:
            tree_value = json.loads(obj.tree_value)
        else:
            tree_value = []
        o_tree = widgets.Tree(name="permission", data=tree_data, value=tree_value,
                              select="multiple", height=700, width=690)
        return {"name": "菜单权限", "widget": o_tree}

    def other_permission(self, request, obj=None):
        o_group_ex = GroupEx.objects.filter(key="BASE_MENU").first()
        other_data = json.loads(o_group_ex.other_data)
        if obj and obj.other_value:
            other_value = json.loads(obj.other_value)
        else:
            other_value = []
        o_transfer = widgets.Transfer(name="other_permission", data=other_data, value=other_value,
                                      height=500, width=300)
        return {"name": "model权限", "widget": o_transfer}

    def has_delete_permission(self, request, obj=None):
        return bool(request.user.is_superuser)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(group_id__isnull=False)
        return queryset

    # def get_search_results(self, request, queryset, search_term=""):
    #     queryset, use_distinct = super(GroupExAdmin, self).get_search_results(request, queryset, search_term)
    #     return queryset, use_distinct

    def delete_model(self, request, obj):
        Group.objects.filter(pk=obj.group_id).delete()
        super(GroupExAdmin, self).delete_model(request, obj)

    def save_after(self, request, old_obj, obj, save_data, update_data,
                   m2m_data, dict_error, inline_data=None, change=True):
        """
        还要加上model已注册，但是在菜单中没有显示的权限
        """
        name = save_data["name"]
        v = save_data["permission"] or []
        lst_p = []
        for p in v:
            if isinstance(p, int):
                lst_p.append(p)
        other_v = save_data["other_permission"] or []
        lst_p.extend(other_v)
        if obj.group_id:
            o_group = Group.objects.filter(pk=obj.group_id).first()
            o_group.name = obj.name
            o_group.permissions.set(lst_p)
            o_group.save()
        else:
            o_group = Group.objects.create(name=name)
            if lst_p:
                o_group.permissions.set(lst_p)
            o_group.save()
            obj.group_id = o_group.pk
        # obj.menu_data = json.dumps(v, ensure_ascii=False)
        obj.tree_value = json.dumps(v, ensure_ascii=False)
        # obj.save()

        from vadmin import menu
        lst_menu, tree_value = menu.MenuAuthManage().get_menu_data_by_group(group_id=obj.group_id)
        obj.menu_data = json.dumps(lst_menu, ensure_ascii=False)
        obj.other_value = json.dumps(other_v, ensure_ascii=False)
        # tree_data = []
        # menu.parse_menu(lst_menu, tree_data)
        # obj.tree_value = json.dumps(tree_value, ensure_ascii=False)
        obj.save()

    def save_before(self, request, old_obj, data, dict_error, inline_data=None):
        try:
            cache.delete(const.CACHE_KEY_GROUP_ID)
            cache.delete(const.CACHE_KEY_GROUP_KEY)
            cache.delete(const.CACHE_KEY_GROUP_NAME)
        except (BaseException,):
            pass
        # dict_group = dict(GroupEx.objects.filter(del_flag=False).values_list("key", "group_id"))
        # cache.set(const.CACHE_KEY_GROUP_KEY, dict_group)

        # dict_group = dict(GroupEx.objects.filter(del_flag=False).values_list("group_id", "key"))
        # cache.set(const.CACHE_KEY_GROUP_ID, dict_group)


@admin.register(PermissionEx)
class PermissionExAdmin(VModelAdmin):
    """
    权限子项
    """
    list_display = ["name", "codename"]

    fieldsets = (
        (None, {'fields': ('name', 'codename', 'tree',)}),
    )

    def tree(self, request, obj=None):
        tree_data = []
        tree_value = []
        o_group_ex = GroupEx.objects.filter(key="BASE_MENU").first()
        if o_group_ex:
            o_menu_auth = menu.MenuAuthManage(is_all=True)
            if o_group_ex.menu:
                lst_menu = json.loads(o_group_ex.menu)
            else:
                no_menu_model = {}
                lst_menu = o_menu_auth.get_menu_data(no_menu_model=no_menu_model)
            o_menu_auth.menu_2_tree(lst_menu, tree_data, is_sub=False)

        if obj:
            dict_content_type = dict()
            for o_content_type in ContentType.objects.all():
                dict_content_type[o_content_type.pk] = o_content_type

            lst_permission = Permission.objects.filter(codename__contains="%s_" % obj.codename)
            for o_permission in lst_permission:
                auth, codename = o_permission.codename.split("_", 1)
                o_content_type = dict_content_type[o_permission.content_type_id]
                value = "%s.%s" % (o_content_type.app_label, codename)
                tree_value.append(value)

        return {"name": "菜单", "widget": widgets.Tree(name="tree_value", data=tree_data, value=tree_value,
                                                     select="multiple", height=700, width=690)}

    def save_after(self, request, old_obj, obj, save_data, update_data,
                   m2m_data, dict_error, inline_data=None, change=True):

        with transaction.atomic():
            dict_content_type = dict()
            for o_content_type in ContentType.objects.all():
                dict_content_type[o_content_type.pk] = o_content_type

            dict_value = {}
            lst_permission = Permission.objects.filter(codename__contains="%s_" % obj.codename)
            for o_permission in lst_permission:
                auth, codename = o_permission.codename.split("_", 1)
                o_content_type = dict_content_type[o_permission.content_type_id]
                value = "%s.%s" % (o_content_type.app_label, codename)
                dict_value[value] = o_content_type

            add_value = []
            if old_obj:
                for o_permission in Permission.objects.filter(codename__contains="%s_" % old_obj.codename):
                    if "name" in update_data:
                        auth, codename = o_permission.codename.split("_", 1)
                        o_permission.codename = "%s_%s" % (save_data["codename"], codename)

                    o_content_type = dict_content_type[o_permission.content_type_id]
                    try:
                        model = django_apps.get_model(o_content_type.app_label, o_content_type.model)
                        name = model._meta.verbose_name
                        value = "%s.%s" % (o_content_type.app_label, o_content_type.model)
                    except (BaseException,):
                        value = name = o_content_type.model

                    if "codename" in update_data:
                        o_permission.name = "%s %s" % (save_data["name"], name)

                    if ("name" in update_data) or ("codename" in update_data):
                        o_permission.save()

                    if value not in save_data["tree_value"]:
                        o_permission.delete()
                    else:
                        add_value.append(value)

            for value in save_data["tree_value"]:
                if value in add_value:
                    continue

                if value not in dict_value:
                    app_label, model = value.split(".", 1)
                    o_content_type = ContentType.objects.filter(app_label=app_label, model=model).first()
                    if o_content_type is None:
                        o_content_type = ContentType.objects.create(app_label=app_label, model=model).first()
                else:
                    o_content_type = dict_value[value]

                try:
                    name = "%s %s" % (save_data["name"], str(o_content_type))
                except (BaseException,):
                    name = "%s %s" % (save_data["name"], value)

                codename = "%s_%s" % (save_data["codename"], o_content_type.model)
                Permission.objects.create(name=name, content_type_id=o_content_type.pk, codename=codename)
                add_value.append(value)

            menu.MenuAuthManage().update_menu_data()

    def delete_model(self, request, obj):
        with transaction.atomic():
            Permission.objects.filter(codename__contains="%s_" % obj.codename).delete()
            super(PermissionExAdmin, self).delete_model(request, obj)

            # 重新整理缓存数据
            menu.MenuAuthManage().update_menu_data(obj)
