# !/usr/bin/python
# -*- coding=utf-8 -*-
# pylint: disable=C0111

import os
import json
from django.conf import settings
from django.contrib import admin
from django.forms.models import ModelForm

from case import filter
from case.models import Address
from case.models import Area
from case.models import City
from case.models import CollapseExample
from case.models import DateExample
from case.models import FileExample
from case.models import Province
from case.models import Rich
from case.models import TemplateExample
from case.models import TreeExample
from case.models import TreeTable
from case.models import Unit
from case.models import Widget
from vadmin import admin_api
from vadmin import const
# from vadmin import event
from vadmin import step
from vadmin import theme
from vadmin import widgets
from vadmin import common
from vadmin import field_translate
# from vadmin.models import VModel
from vadmin.admin import VModelAdmin
from utils import word_2_vadmin

@admin.register(Unit)
class UnitAdmin(VModelAdmin):
    """
    区
    """
    list_display = ['name', 'age_float', 'age_int', 'age_chart']
    list_filter = ['age_int', 'age_chart']  # 过滤字段
    # list_editable = []  # 列表编辑字段
    # readonly_fields = []  # 只读字段

    # v_change_list = "/unit_change_list/"
    v_export = True

    def get_list_display(self, request):
        menu_id = request.GET.get(const.UPN_MENU_ID, "")
        dict_param = common.parse_url_param(menu_id)
        if "m" in dict_param and dict_param["m"] == "3":
            return ['name', 'age_float', ]

        return super(UnitAdmin, self).get_list_display(request)

    def get_fieldsets(self, request, obj=None):
        menu_id = request.GET.get(const.UPN_MENU_ID, "")
        dict_param = common.parse_url_param(menu_id)
        if "m" in dict_param and dict_param["m"] == "3":
            fieldsets = (
                (None, {'fields': ('name', 'age_float')}),
            )
            return fieldsets

        return super(UnitAdmin, self).get_fieldsets(request, obj)

    def get_v_list_filter(self, request):
        menu_id = request.GET.get(const.UPN_MENU_ID, "")
        dict_param = common.parse_url_param(menu_id)
        if "m" in dict_param and dict_param["m"] == "3":
            return []

        return self.list_filter


@admin.register(City)
class CityAdmin(VModelAdmin):
    # model = City
    list_v_display = ("id", "name", "del_flag", 'order')
    # verbose_name_plural = "城市配置"
    readonly_fields = ['order', ]
    # v_sortable = True

    # change_list定义
    # v_change_list_config = {"col_width": {"field": 100, "field2": 200},
    # "col_name":{"field":"aa", "field2":"bb"}}
    change_list_config = {"col_width": {"name": 250, }, "col_name": {"name": "市名称（自定义名称）"}}

    def customize(self, request, obj=None):
        o_select = widgets.Select(name="name", data=[['1', 'a'], ['2', 'b'], ['3', 'c']])
        if obj:
            o_select.value = obj.name

        return o_select

    customize.short_description = "自定义字段"

    # v_sortable = True


@admin.register(Province)
class ProvinceAdmin(VModelAdmin):
    """
    省
    """
    # v_inlines = (CityInline,)
    list_display = ['id', 'name', 'order_link', 'opera_link']
    # list_filter = []  # 过滤字段
    # list_editable = []  # 列表编辑字段
    # readonly_fields = []  # 只读字段
    # v_sortable = True
    exclude = ('order',)
    ordering = ('order', "pk")
    v_export = True
    list_v_sort = ["id", ]
    list_editable = ["name"]
    fieldsets = (
        ("城市", {'fields': (CityAdmin,)}),
        (None, {'fields': ('name',)}),
    )
    change_list_config = {"order": True}

    def opera_link(self, request, obj):
        o_theme = theme.get_theme(request.user.pk)
        table_name = const.WN_TABLE % ("case", "province")
        if obj:
            url = const.URL_LIST_SAVE % ("case", "province")
            # o_step = step.WidgetOpera(name=table_name, opera=const.TABLE_ROW_SAVE,
            #                           data={"id": obj.pk}, url=url)
            o_step = None
        else:
            o_step = None
        return widgets.Button(icon="fa-save", font_size=20, font_color=o_theme.theme_color,
                              bg_color="transparent", focus_color="transparent",
                              step=o_step)

    opera_link.short_description = "操作"

    def order_link(self, request, obj):
        return obj.order

    order_link.short_description = "排序"

    def make_inline_custom(self, request, obj_inline, row_data=None, obj=None):
        app_label, model_name = obj_inline.opts.app_label, obj_inline.opts.model_name
        name = const.WN_TABLE % (app_label, model_name)
        return [
            widgets.Button(text="增加行（第一行）", margin_right=5,
                           step=step.WidgetOpera(name=name,
                                                 opera=const.OPERA_TABLE_ROW_ADD,
                                                 data={"mode": "first", "row_data": row_data})),

            widgets.Button(text="增加行（前面插入）", margin_right=5,
                           step=step.WidgetOpera(name=name,
                                                 opera=const.OPERA_TABLE_ROW_ADD,
                                                 data={"mode": "before", "related_id": 50, "row_data": row_data})),

            widgets.Button(text="增加行（后面插入）", margin_right=5,
                           step=step.WidgetOpera(name=name,
                                                 opera=const.OPERA_TABLE_ROW_ADD,
                                                 data={"mode": "after", "related_id": 50, "row_data": row_data}))
        ]


class AreaInline(VModelAdmin):
    model = Area
    list_v_display = ("name", "del_flag", 'no')
    # readonly_fields = ("del_flag",)
    verbose_name_plural = "区配置"


#
# class CityForm(ModelForm):
#     v_widgets = {
#         'province': widgets.Select(search_field="name"),
#         'name': widgets.Input(type="textarea", style={"height": "100px", "width": "300px"}),
#         # 'del_flag': widgets.Select(data=[[0, "否"], [1, "是"]]),
#     }
#
#
# class CityAdmin(VModelAdmin):
#     """
#     市
#     """
#     form = CityForm
#     list_v_display = ['id', 'province', 'province__name', 'name']
#     list_display_links = ['province', 'name']
#     list_v_filter = ['province', ]  # 过滤字段
#     # list_editable = []  # 列表编辑字段
#     # readonly_fields = []  # 只读字段
#     search_fields = ['province__name']
#     v_sortable = True
#     v_export = True
#     exclude = ("order",)
#     # ordering = ("order",)
#     v_inlines = (AreaInline,)
#
#     fieldsets = (
#         (None, {'fields': ('province', 'province__order', 'name', 'del_flag', 'order')}),
#         ("区配置", {'fields': (AreaInline,)}),
#     )
#
#     def get_inline_default(self, request, inline, obj=None):
#         lst_sub_obj = []
#         if obj is None:
#             lst_sub_obj.append(inline.model(name="A"))
#             lst_sub_obj.append(inline.model(name="B"))
#             lst_sub_obj.append(inline.model(name="C"))
#         return lst_sub_obj


# admin.site.register(City, CityAdmin)
#
#
# class UnitInline(VModelAdmin):
#     model = Unit
#     fields = ("name", "age_float", "age_int", "age_chart")
#     # readonly_fields = ("del_flag",)
#     verbose_name_plural = "工作单位"


@admin.register(Address)
class AddressAdmin(VModelAdmin):
    list_display = ("area", "name", "image", "date_example")


@admin.register(Area)
class AreaAdmin(VModelAdmin):
    """
    区
    """
    list_display = ['name']
    # list_filter = []  # 过滤字段
    # list_editable = []  # 列表编辑字段
    # readonly_fields = []  # 只读字段
    exclude = ("order",)
    # v_inlines = (AddressInline,)
    v_foreign_key_select_field = ["city"]
    fieldsets = (
        (None, {'fields': ('city', AddressAdmin, 'name', 'no', 'del_flag')}),
    )
    foreign_key_link_field = ["city", ]


class WidgetForm(ModelForm):
    upload_url = const.URL_UPLOAD_UEDITOR % ("case", "widget", "input")
    v_widgets = {
        # 'input_rich': widgets.Rich(width=900, height=400, upload_url=upload_url),
        'checkbox': widgets.Checkbox(),
        'switch': widgets.Switch(),
        'color': widgets.ColorPicker(),
        'multiple': widgets.Select(multiple=True),
        'slider': widgets.Slider(),
        'province': widgets.Select(),
        'city': widgets.Select(),
        'rate': widgets.Rate(),
        'radio_button': widgets.Radio(theme="button"),
        'checkbox_button': widgets.Checkbox(theme="button"),
    }


#
# def device_activation_off(self, request, queryset):
#     # rows = queryset.update(activation=False)
#     # if rows == 1:
#     #     ms = 1
#     # else:
#     #     ms = rows
#     lst_device = list(queryset)
#     return "%s个设备去激活成功." % len(lst_device)
#
#
# device_activation_off.short_description = "去激活所选的设备"
#
#
# def device_activation_on(self, request, queryset):
#     # rows = queryset.update(activation=True)
#     # if rows == 1:
#     #     ms = 1
#     # else:
#     #     ms = rows
#     lst_device = list(queryset)
#     return "%s个设备激活完成." % len(lst_device)
#
#
# device_activation_on.short_description = "激活所选的设备"
#
#
# def update_province(self, request, queryset):
#     o_grid = admin_api.make_change_field_widget(request, self, "province")
#     o_grid.width = 400
#     o_grid.add_widget(widgets.RowSpacing(20))
#     lst_object_id = list(queryset.all().values_list("pk", flat=True))
#     # o_step = step.Get(url="/test_update_province/?object_id=%s" % object_id, widget_url_para=["province_id", ])
#     url = admin_api.make_url("/test_update_province/?id=%s" % str(lst_object_id).replace(" ", ""), request)
#     o_step = step.Post(url=url, submit_type="assign", widget_assign=["province_id", ],
#                        widget_url_para=["province_id", ])
#     o_button = widgets.Button(text="确定", step=o_step)
#     o_grid.add_widget(o_button)
#     o_step = step.GridPopup(grid=o_grid)
#     return o_step
#
#
# update_province.short_description = "修改省份"


class WidgetAdmin(VModelAdmin):
    """
    图例类
    """
    form = WidgetForm
    # list_display = ['input', 'radio', 'checkbox', 'date', 'time', 'datetime', 'image_link', 'province',
    #                 'city', 'area', 'create_time', 'update_time', 'del_flag', 'order', ]
    list_v_display = ["id", 'input_link', "multiple", 'radio', 'checkbox', 'date', 'time', 'datetime', 'image_link',
                      'province__name',
                      'city', 'area', 'create_time', 'del_flag', ]
    list_display_links = ["checkbox"]
    list_filter = ['del_flag', ]  # 过滤字段
    # actions = [device_activation_off, device_activation_on, update_province]
    list_v_filter = [filter.MultipleFilter, filter.BeginDateFilter, filter.EndDateTimeFilter, filter.ProvinceFilter,
                     "province", "city", 'area', 'create_time',
                     'update_time', 'del_flag']  # 过滤字段
    list_v_sort = ["create_time", "order"]
    v_sortable = True
    v_export = True
    # v_export_config = {"width": {7: 100}}  # 第7列宽100
    # list_editable = ['radio', ]  # 列表编辑字段
    readonly_fields = ['del_flag', ]  # 只读字段
    search_fields = ["input", ]
    v_search_placeholder = "输入关键字"
    exclude = ("order",)
    ordering = ("order",)
    # v_change_list_config = {"col_width": {"input": 150}, "col_name": {"input": "test1"}}
    change_list_config = {"order": True, "sort_field": ["datetime", "create_time", "update_time"],
                          "col_width": {"create_time": 200}}
    list_per_page = 20  # 显示的最大行数

    # v_tabs_direction = "vertical"

    fieldsets = (
        (None, {'fields': ('radio', 'checkbox', 'switch', 'color', 'multiple', 'slider', "del_flag")}),
        ("时间", {'fields': (('date', 'time'), 'datetime',)}),
        ("多级过滤", {'fields': (('province', 'city', 'area'),)}),
        ("自定义", {'fields': ('widget_area', 'widget_date')}),
        ("文件", {'fields': ('image', 'file', 'video')}),
        ("测试5", {'fields': ('rate', 'radio_button', 'checkbox_button')}),
        ("输入", {'fields': ('input_rich', 'input', 'input_text')}),
    )

    # def opera_link(self, obj):
    #     table_name = const.WIDGET_TABLE_NAME % ("case", "widget")
    #     o_step = step.WidgetOpera(name=table_name, opera=const.TABLE_ROW_DEL,
    #                               data={"id": obj.pk}, url="/test_row_del/")
    #     o_step_msg = step.Dialog(title="删除", content="确定删除 %s 吗?" % obj)
    #     o_icon = widgets.Icon(class_name="el-icon-delete", tooltip="删除", step=[o_step_msg, o_step], size=16)
    #
    #     o_step_edit = step.WidgetOpera(name=table_name, opera=const.TABLE_ROW_EDIT,
    #                                    data={"id": obj.pk})
    #     o_icon_edit = widgets.Icon(class_name="el-icon-edit", tooltip="编辑", size=16, padding_left=10, step=o_step_edit)
    #
    #     o_step_save = step.WidgetOpera(name=table_name, opera=const.TABLE_ROW_SAVE,
    #                                    data={"id": obj.pk}, url="/test_row_save/")
    #     o_icon_save = widgets.Icon(class_name="fa-save", tooltip="保存", size=16, padding_left=10, step=o_step_save)
    #
    #     return [o_icon, o_icon_edit, o_icon_save]
    #
    # opera_link.short_description = "操作"

    def get_change_list_custom(self, request):
        return [
            widgets.Button(text="测试1", url="/test_button_list/"),
            widgets.ButtonMutex(text="全屏", event={"click": step.FullScreen()}, active_text="退出全屏",
                                active_event={"click": step.FullScreen()})
            # widgets.TimedRefresh(text="定时刷新({})", width=100, height=30, round=8, second=5,
            #                      text_color="#FFFF00",
            #                      step=step.RunScript("hmi.views.test_timed_refresh"),
            #                      background_color="#FF0000")
        ]

    def get_change_form_custom(self, request, obj=None):
        return [widgets.Button(text="测试1", url="/test_button_list/")]

    def form_v_file(self, request, obj=None):
        try:
            value = obj.file.url
        except (BaseException,):
            value = None

        resume_url = const.URL_UPLOAD_FILE_RESUME % ""
        return {
            "name": "文件",
            "widget": widgets.Upload(name="file", multiple=False, resume_url=resume_url,
                                     value=value)
        }

    # 自定义列表中显示的字段不要和model中field name重名，如果重名，会导致form中字段也认为自定义
    def input_link(self, request, obj):
        o_step = step.Get(href="https://www.baidu.com", new_window=True, cross_domain=True)
        return widgets.Text(text=obj.input_rich, step=o_step, color="#0088CC", under_line=True)

    input_link.short_description = "输入控件"

    def image_link(self, request, obj):
        if obj.image:  # 自定义显示图片字段，一个字段可以显示多个图片路径，根据是否为数组判断
            url = str(obj.image)
            if url[0] == "[":
                lst_url = eval(url)
                if lst_url:
                    return widgets.Image(url=lst_url[0], width=60)
            elif obj.image.url:
                return widgets.Image(url=obj.image.url)

        return None

    image_link.short_description = "图片"

    def widget_area(self, request, obj=None):  # 重新定义控件，可以多个组合在一起
        data = []
        for o_province in Province.objects.all():
            lst_city = []
            for o_city in City.objects.filter(province_id=o_province.pk):
                lst_city.append({"id": o_city.pk, "label": o_city.name, "children": []})
                for o_area in Area.objects.filter(city_id=o_city.id):
                    lst_city[-1]["children"].append({"id": o_area.id, "label": o_area.name})

            data.append({"id": o_province.pk, "label": o_province.name, "children": lst_city})

        if obj is None:
            value = None
        else:
            value = f"{obj.province_id}/{obj.city_id}/{obj.area_id}"

        return {"name": "省市区", "widget": widgets.Cascader(name="widget_area", data=data, value=value,
                                                          value_type="multiple")}

    def widget_date(self, request, obj=None):
        date_value = ""
        time_value = ""
        if obj:
            if obj.date:
                date_value = obj.date.strftime('%Y-%m-%d')
            if obj.time:
                time_value = obj.time.strftime('%H:%M:%S')

        o_date = widgets.DatePicker(name="date", value=date_value, margin_right=10)
        o_time = widgets.TimePicker(name="time", value=time_value)
        o_time.padding = [0, 0, 0, 10]

        return {"name": "时间", "widget": [o_date, o_time]}

    # def export_multiple(self, request, obj):  # 导出自定义， 名称固定为"export_字段名称"
    #     value = ""
    #     if obj.multiple:
    #         lst_val = obj.multiple.split(",")
    #         dict_choices = dict(obj._meta.get_field("multiple").choices)
    #         lst_value = []
    #         for val in lst_val:
    #             lst_value.append(dict_choices[val])
    #
    #         value = ",".join(lst_value)
    #     return value

    # def has_delete_permission(self, request, obj=None):
    #     if obj and obj.pk:
    #         return bool(obj.pk % 2)
    #
    #     return True
    #
    # def delete_model(self, request, obj):
    #     """删除调用接口，删除特殊处理重新些函数"""
    #     if obj.image.name is not None:
    #         try:
    #             lst_file = eval(obj.image.name)
    #             for name in lst_file:
    #                 file_path = os.path.normpath(settings.BASE_DIR + name)
    #                 os.remove(file_path)
    #         except (BaseException,):
    #             pass
    #
    #     if obj.file.name is not None:
    #         try:
    #             obj.file.delete()
    #         except (BaseException,):
    #             pass
    #
    #     super(WidgetAdmin, self).delete_model(request, obj)
    #
    # def make_form_delete(self, request, o_template, obj=None):
    #     return None
    #
    # def get_actions(self, request):
    #     name = const.WN_TABLE % ("case", "Widget")
    #     o_step = step.WidgetOpera(name=name, opera="table_row_update", data={"row_id": 6, "row_data": [6, "aaa"]})
    #     step_del = [step.MsgBox(text="是否删除！"),
    #                 step.WidgetOpera(name=name, opera="table_row_del", data={"row_id": 6})]
    #     return [widgets.Button(text="修改行", margin_right=10, step=o_step),
    #             widgets.Button(text="增加行", margin_right=10),
    #             widgets.Button(text="删除行", margin_right=10, step=step_del),
    #             ]


admin.site.register(Widget, WidgetAdmin)


class RichForm(ModelForm):
    v_widgets = {
        'input': widgets.Widget(width=660, height=800),
    }


@admin.register(Rich)
class RichAdmin(VModelAdmin):
    """
    组织
    """
    form = RichForm
    list_display = ['input', 'create_time', 'del_flag']
    exclude = ["order", "create_time"]
    readonly_fields = ["output", ]

    v_tabs = [
        {"label": "编辑", "icon": "", "fieldsets": (
            (None, {'fields': ('input',)}),
        )},
        {"label": "html输出", "icon": "", "fieldsets": (
            (None, {'fields': ('html_output',)}),
        )},
        {"label": "vamdin输出", "icon": "", "fieldsets": (
            (None, {'fields': ('vadmin_output',)}),
        )},
    ]

    def vadmin_output(self, request, obj):
        if obj and obj.output:
            # o_grid = grid.Grid(col_num=2)
            # o_grid.set_col_attr(col=1, width=660)
            # o_grid.set_col_attr(col=2, width=120)
            o_panel = widgets.Panel(padding_left=8, padding_right=8, width=660)
            o_panel.add_widget(json.loads(obj.output))
            # o_grid.add_widget(json.loads(obj.output), col=1)
            return {"name": "vadmin输出", "widget": o_panel}
        return {"name": "vadmin输出"}

    def html_output(self, request, obj):
        if obj and obj.html_output:
            # o_grid = grid.Grid(col_num=2)
            # o_grid.set_col_attr(col=1, width=660)
            # o_grid.set_col_attr(col=2, width=120)
            o_panel = widgets.Panel(width=1000, border_color="#FF0000")
            o_panel.add_widget(widgets.Html(data=obj.html_output))
            # o_grid.add_widget(json.loads(obj.output), col=1)
            return {"name": "html输出", "widget": o_panel}
        return {"name": "html输出"}

    def has_readonly_text(self, request, obj=None):
        return True

    def get_v_button_form(self, request, obj):
        url = admin_api.make_url("case.service.test_html_2_word", request)
        return [widgets.Button(text="转word", step=step.RunScript(url)), ]


@admin.register(TemplateExample)
class TemplateExampleAdmin(VModelAdmin):
    list_display = ["input", "output"]
    exclude = ["order"]

    def form_v_vadmin_output(self, request, obj):
        o_widget = None
        if obj and obj.vadmin_output:
            o_widget = json.loads(obj.vadmin_output)

        return {"name": "输出VAdmin", "widget": o_widget}

    def form_v_html_output(self, request, obj):
        o_widget = None
        if obj:
            o_widget = widgets.Html(obj.html_output)

        return {"name": "输出HTML", "widget": o_widget}

    def form_v_html_word(self, request, obj):
        if obj:
            # o_widget = widgets.Word(width="100%", height="100%")
            # # o_word = word_2_vadmin.generate(file_path)
            # o_widget.append(json.loads(obj.vadmin_output))
            # return o_widget

            path = common.get_file_path(obj.input.name)
            o_word = word_2_vadmin.generate_word(path)
            o_word.height = "100vh-160" # 必须固定高度，否则工具条不能悬浮
        else:
            o_word = widgets.Word(width="100%", height="100%")

        return o_word


    def get_fieldsets(self, request, obj=None):
        menu_id = request.GET.get(const.UPN_MENU_MODE, "")
        if menu_id == "2":
            fieldsets = (
                (None, {'fields': ('html_word',)}),
            )
            return fieldsets

        return super().get_fieldsets(request, obj)

    def get_change_form_custom(self, request, obj=None):
        if obj:
            script1 = "case.service.word_2_vadmin?object_id=%s&mode=1" % obj.pk
            script2 = "case.service.word_2_pdf?object_id=%s&mode=2" % obj.pk
            # script3 = "case.service.word_change?object_id=%s&mode=3" % obj.pk
            o_button1 = widgets.Button("WORD转VAdmin", step=step.RunScript(script1))
            o_button2 = widgets.Button("WORD转PDF", step=step.RunScript(script2))
            # o_button3 = widgets.Button("WORD装换HTML", step=step.RunScript(script3))
            return [o_button1, o_button2]

    def get_list_display(self, request):
        menu_id = request.GET.get(const.UPN_MENU_MODE, None)
        if menu_id == "2":
            return ["input"]
        return super().get_list_display(request)

    def has_change_form_opera(self, request):
        menu_id = request.GET.get(const.UPN_MENU_MODE, None)
        if menu_id == "2":
            return False
        return True


class CollapseExampleForm(ModelForm):
    v_widgets = {
        # 'province_id': widgets.Select(cascade_filter=True),
        # 'city_id': widgets.Select(cascade_filter=True),
    }


class CollapseExampleAdmin(VModelAdmin):
    """
    折叠
    """
    form = CollapseExampleForm
    list_display = ["first", "second", ]
    list_filter = ["province_id", "city_id", "area_id"]
    v_collapses = [
        {"label": "TAB1", "icon": "", "fieldsets": (
            (None, {'fields': ('first',)}),
        )},
        {"label": "TAB2", "icon": "", "fieldsets": (
            ("测试3", {'fields': ("second",)}),
        )},
        {"label": "TAB3", "icon": "", "fieldsets": (
            ("测试4", {'fields': ('province_id', 'city_id', 'area_id')}),
        )},
    ]

    # def v_select_change_filter(self, request, field_name, object_id=None):
    #     o_widget = None
    #     if field_name == "province_id":
    #         if object_id is None:
    #             data = list(City.objects.all().values_list("pk", "name"))
    #         else:
    #             data = list(City.objects.filter(province_id=object_id).values_list("pk", "name"))
    #         o_widget = widgets.Select(name="city_id", data=data, cascade_filter=True, model_name="CollapseExample")
    #
    #     elif field_name == "city_id":
    #         if object_id is None:
    #
    #             for obj in Area.objects.all():
    #                 data.append([obj.pk, str(obj)])
    #             # data = list(Area.objects.all().values_list("pk", "name"))
    #         else:
    #             for obj in Area.objects.filter(city_id=object_id):
    #                 data.append([obj.pk, str(obj)])
    #             data = list(Area.objects.filter(city_id=object_id).values_list("pk", "name"))
    #         o_widget = widgets.Select(name="area_id", data=data)
    #
    #     return o_widget

    # def v_select_change_filter_init(self, request, field_name, obj=None):
    #     """
    #     多级过滤初始化
    #     """
    #     data = []
    #     if field_name == "province_id":
    #         data = list(Province.objects.all().values_list("pk", "name"))
    #
    #     elif field_name == "city_id":
    #         if obj and obj.pk:
    #             data = list(City.objects.filter(province_id=obj.province_id).values_list("pk", "name"))
    #         else:
    #             data = list(City.objects.all().values_list("pk", "name"))
    #     elif field_name == "area_id":
    #         if obj and obj.pk:
    #             data = list(Area.objects.filter(city_id=obj.city_id).values_list("pk", "name"))
    #         else:
    #             data = list(Area.objects.all().values_list("pk", "name"))
    #
    #     return data


admin.site.register(CollapseExample, CollapseExampleAdmin)


@admin.register(TreeExample)
class TreeExampleAdmin(VModelAdmin):
    """
    树
    """
    list_display = ["desc", ]

    # def data_same(self, request, obj=None):
    #     """自定义字段，返回组件或者组件列表"""
    #     o_widget = widgets.Tree(name="data_same", select=True, add_del=True, edit=True, order=True, same_sort=False,
    #                             model_name="TreeExample",
    #                             field_name="data_save", width=300)
    #     return {"name": "同级排序", "widget": o_widget}
    #
    # def data_same_save(self, request, obj, k, v, update_data, dict_error):  # 保存时回调，可以没有
    #     """
    #     :param obj:老对象
    #     :param k:自定义的组件name，此处对应"widget_area"
    #     :param v:界面提交的值
    #     :param update_data: 修改后值, key为字段名称，value为修改后的值
    #     :param dict_error: 错误信息
    #     :return:
    #     """
    #     pass
    #
    # def data(self, request, obj=None):
    #     pass


# admin.site.register(TreeExample, TreeExampleAdmin)

@admin.register(DateExample)
class DateExampleAdmin(VModelAdmin):
    """
    时间组件案例
    """
    list_display = ["date1", "date2", "date3"]
    list_display_links = ["date2"]
    list_editable = ["date1", "date3"]


class FileExampleForm(ModelForm):
    v_widgets = {
        'image_multiple': widgets.Upload(type="image_card"),
        # 'city_id': widgets.Select(cascade_filter=True),
    }


@admin.register(FileExample)
class FileExampleAdmin(VModelAdmin):
    """
    时间组件案例
    """
    form = FileExampleForm
    list_display = ["id", "image", "image_multiple", "file", "file_multiple", ]


@admin.register(TreeTable)
class TreeTableAdmin(VModelAdmin):
    """
    树表格案例
    """
    list_display = ["id", "name", "parent"]

    # v_change_list = "tree_table_example/"

    def make_list_table(self, request, o_template, queryset):
        table_name = const.WN_TABLE % ("case", "treetable")
        head = ["ID", "名称", "父结点"]
        data = []

        def add_item(obj, dict_item):
            lst_item = TreeTable.objects.filter(parent_id=obj.pk)
            if lst_item:
                for o_item in lst_item:
                    o_widget = field_translate.field_2_list_links(request, self, "id", o_item,
                                                                  o_template.filter_name)
                    item = {"expand": True, "id": o_item.pk,
                            "row": [o_widget, o_item.name, str(o_item.parent)]}
                    add_item(o_item, item)
                    dict_item.setdefault("children", []).append(item)

        for o_tree_table in TreeTable.objects.filter(parent_id__isnull=True):
            o_widget = field_translate.field_2_list_links(request, self, "id", o_tree_table,
                                                          o_template.filter_name)
            item = {"expand": True, "row_id": o_tree_table.pk,
                    "row": [o_widget, o_tree_table.name, o_tree_table.parent]}
            add_item(o_tree_table, item)
            data.append(item)

        o_tree_table = widgets.Table(name=table_name, head={"data": head}, data=data, col_border=False,
                                     tree=True)
        return o_tree_table
