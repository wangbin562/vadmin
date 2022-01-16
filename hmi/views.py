# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
views
"""
import importlib
import json
import logging
import math
import os
import random
import time
import traceback

from django.conf import settings
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from case.models import Widget
from hmi import service as hmi_service
from vadmin import admin_api
from vadmin import const
from vadmin import event
from vadmin import service
from vadmin import step
from vadmin import theme
from vadmin import widgets
from vadmin import widgets_ex
from vadmin.json_encoder import Encoder  # Encoder 函数将Step对象转换成json，提前转换也可以不使用

logger = logging.getLogger(__name__)


def v_upload_file(request):
    """
    上传文件
    """
    try:
        file_obj = request.FILES["file"]
        path = settings.MEDIA_ROOT

        if not os.path.exists(path):
            os.makedirs(path)

        name, suffix = os.path.splitext(file_obj.name)
        # file_name = "%s_%s%s" % (name, suffix)
        file_path = os.path.join(path, file_obj.name)
        f = open(file_path, 'wb')
        for chunk in file_obj.chunks():
            f.write(chunk)
        f.close()
        url = file_obj.name
        # 解压
        import zipfile
        unzip_path = os.path.join(path, name)
        z = zipfile.ZipFile(file_path, 'r')
        z.extractall(unzip_path)
        z.close()

        data = []

        def list_dir(path, lst_name):
            for file in os.listdir(path):
                file_path = os.path.join(path, file)
                if os.path.isdir(file_path):
                    sig = {"value": file_path, "label": file, "expand": True, "children": []}
                    lst_name.append(sig)
                    list_dir(file_path, sig["children"])
                else:
                    o_step = step.Get(url="/update_code_view/%s/" % file_path)
                    lst_name.append({"value": file_path, "label": file, "step": o_step})

        list_dir(unzip_path, data)
        # for root, dirs, files in os.walk(unzip_path):
        #     data.append({"label":})
        #     print(root)
        #     print(dirs)
        #     print(files)
        o_step = step.WidgetUpdate(widgets.Tree(name="file_tree", height={"calc": "100%-20px"}, select=True, data=data))
        # dict_resp = {"step": file_obj.name, "url": url}
        dict_resp = {"name": file_obj.name, "url": url, "step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")


def code_view(request):
    try:

        o_grid = grid.Grid(col_num=2, height="100%", padding_top=10, padding_left=10)
        o_grid.set_col_attr(col=0, width=400)
        o_grid.set_col_attr(col=1)
        o_grid.add_widget(widgets.Upload(type="file", upload_url="/v_upload_file/"), col=0)
        o_grid.add_widget(widgets.Row(), col=0)
        o_grid.add_widget(widgets.Tree(name="file_tree", height={"calc": "100%-20px"}, width="100%", select=True),
                          col=0)
        o_grid.add_widget(widgets.Input(name="code_view", type="textarea", width="100%", height="100%", select=True))
        dict_resp = service.refresh_page(request, o_grid, menu_value=const.HOME_VIEW)
        o_theme = theme.get_theme(request.user.id)
        dict_resp["step"].insert(0, step.ChangeTheme(theme_color=o_theme.theme_color, focus_color=o_theme.focus_color,
                                                     round=o_theme.round))

        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, theme="error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def update_code_view(request, file_path):
    try:
        # logger.error(file_path)
        buf = open(file_path, "rb").read()
        try:
            try:
                value = str(buf, encoding="utf8")
            except (BaseException,):
                value = str(buf)
            o_step = step.WidgetUpdate(widgets.Text(name="code_view", value=value))
            dict_resp = {"step": o_step}
        except (BaseException,):
            dict_resp = {"step": step.Msg(text="非文本数据，无法解析！", theme="error")}

        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, "error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def word_view(request):
    try:
        o_widget = widgets.Word()
        o_panel = widgets.Panel(name=const.WN_CONTENT_RIGHT, vertical="top", width="100%", height="100%")
        o_panel.append(o_widget)
        result = step.WidgetUpdate(mode="all", data=o_panel)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, "error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def custom(request):
    dict_resp = service.check_login(request)
    if dict_resp:
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False), content_type="application/json")

    try:
        o_page = page.Page()
        # o_step = step.WebViewOpera(go_back=1)
        top_height = 50
        # o_panel = widgets.Panel(width=50, background_color="#36A8FA")
        o_grid = grid.Grid(col_num=3, height=top_height, background_color="#36A8FA")
        o_grid.set_col_attr(col=0, width=200)
        o_grid.set_col_attr(col=1, percentage=0.6)
        o_grid.set_col_attr(col=2, horizontal="right")
        o_grid.add_widget(widgets.Text(text="长江航道检测平台", text_size=18, color="#FFFFFF"), col=0)
        o_step = step.Get(url="v_home_view/", jump=True)
        o_grid.add_widget(widgets.Button(text="首页", height=top_height, width=100, step=o_step, round=0), col=1)
        o_grid.add_widget(widgets.Button(text="航道图", height=top_height, width=100, round=0), col=1)
        o_page.add_widget(o_grid)
        o_page.add_widget(widgets.Row())

        o_panel = widgets.Panel(width=200, height="100%", background_color="#DFDFDF")
        o_panel.add_widget(
            widgets.Button(text="功能", width=199, border_color="#DFDFDF", background_color="#F5F5F5", color="#808080"))

        o_panel_sub = widgets.Panel(width=199, height=300, background_color="#FFFFFF", vertical="top")
        o_panel.add_widget(o_panel_sub)
        o_panel.add_widget(widgets.Button(text="功能", width=199, background_color="#F5F5F5", color="#808080"))

        o_panel_sub = widgets.Panel(width=199, height={"calc": "100%-400px"}, background_color="#FFFFFF",
                                    vertical="top")
        o_panel.add_widget(o_panel_sub)

        o_page.add_widget(o_panel)
        # o_page.add_widget(widgets.Button(text="aaaaaaaaaaaa"))
        # o_page.add_widget(widgets.Input(value="aaaaaaaaaaaa"))

        # o_page.add_widget(o_panel)
        dict_resp = {'step': step.PageUpdate(o_page)}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, theme="error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def custom_menu_template(request):
    pass


def test_row_del(request):
    content = request.POST.get(const.SUBMIT_WIDGET, "{}")
    widget_data = json.loads(content)
    content = request.POST.get(const.SUBMIT_OPERA, "[]")
    opera_data = json.loads(content)

    for data in opera_data:
        if const.TABLE_ROW_DEL in data:
            Widget.objects.filter(pk__in=data.get("data", [])).delete()
            break
    dict_resp = {"step": step.make_step(step.Msg("删除完成!", theme="success"), step.WidgetOperaSuccess())}
    return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")


def test_row_save(request):
    content = request.POST.get(const.SUBMIT_WIDGET, "{}")
    widget_data = json.loads(content)
    content = request.POST.get(const.SUBMIT_OPERA, "[]")
    opera_data = json.loads(content)
    for data in opera_data:
        if const.TABLE_ROW_DEL in data:
            Widget.objects.filter(pk__in=data.get("data", [])).delete()
            break
    dict_resp = {"step": step.make_step(step.Msg("删除完成!", theme="success"), step.WidgetOperaSuccess())}
    return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")


def test_button_list(request):
    try:
        result = step.Msg("测试功能!", msg_type="error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = step.Msg(s_err_info, "error")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_update_province(request):
    try:
        page_index = int(request.GET.get('p', 1))
        lst_object_id = eval(request.GET.get('id', '[]'))
        province_id = request.GET.get('province_id', None)
        if lst_object_id:
            Widget.objects.filter(pk__in=lst_object_id).update(province_id=province_id)
            url = admin_api.make_url(const.CHANGE_LIST % ("case", "widget", page_index), request, ["id", "province_id"])
            o_step = step.Get(url=url, jump=True)
            dict_resp = {"step": step.make_step(step.Msg("修改完成!", theme="success"), step.GridClose(), o_step)}
        else:
            dict_resp = {"step": step.make_step(
                step.Msg(_("Items must be selected in order to perform actions on them. No items have "
                           "been changed."), theme="warning"), step.GridClose())}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def unit_change_list(request):
    try:
        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.style)
        app_label = "case"
        model_name = "unit"
        page_index = request.GET.get('p', 1)
        page_index = int(page_index)

        model_admin = admin_api.get_model_admin(app_label, model_name)
        o_style = o_module.ChangeListStyle(request, model_admin, o_theme)
        o_breadcrumb = o_style.make_title()

        # 过滤器
        queryset = model_admin.get_queryset(request)
        queryset = admin_api.get_filter_queryset(request, queryset, model_admin, page_index)
        lst_filter_name = []
        # o_grid_filter = admin_widgets.make_list_filter(request, model_admin, queryset, count_all,
        #                                                       lst_filter_name)

        o_admin_config = admin_config.get_admin_list_config(request, model_admin, page_index)

        # 自定义内容部分
        lst_grid = []
        for obj in queryset:
            row = []
            for field in o_admin_config.lst_display:
                # 第一列默认是排序列
                if o_admin_config.sortable and field == "order":
                    continue

                if field in o_admin_config.lst_display_links:
                    text = getattr(obj, field)
                    href = model_admin.get_v_change_form(request, obj)
                    o_step_get = step.Post(href=href, jump=True, widget_url_para=lst_filter_name)
                    o_widget = widgets.Text(text=text, step=o_step_get, color="#0088CC", under_line=True)
                    db_field = model_admin.model._meta.get_field(field)
                    row.append({"data": [widgets.Text(text="%s:" % str(db_field.verbose_name)), o_widget]})

                # 回调自定义列
                elif hasattr(model_admin, field) and callable(getattr(model_admin, field)):
                    # row_data.append(getattr(model_admin, field)(obj))
                    pass

                else:
                    db_field = model_admin.model._meta.get_field(field)
                    if field in o_admin_config.lst_editable and model_admin.has_change_permission(request, obj):
                        is_edit = True
                    else:
                        is_edit = False

                    if is_edit:
                        o_widget = admin_api.field_2_widget(request, model_admin, field, obj, is_filter=True)
                    else:
                        o_widget = admin_api.field_2_list_widget(request, model_admin, field, obj)

                    row.append({"data": [widgets.Text(text="%s:" % str(db_field.verbose_name)), o_widget]})

            o_table = widgets.Table(head_show=False, row=row, select=False)
            lst_grid.append(o_table)
            lst_grid.append(widgets.Row(height=20))

        # 分页
        # o_pagination = o_module.make_change_list_pagination(request, model_admin, count_all, page_total, page_index, lst_filter_name,
        #                                                       pagination_url="/unit_change_list/?m=2")
        count_all = queryset.count()
        page_total = math.ceil(count_all / model_admin.list_per_page)
        o_pagination = o_style.make_change_list_pagination(page_total, count_all)

        o_grid = grid.Grid(col_num=1)
        o_grid.set_col_attr(col=0, vertical="top", background_color=o_theme.background_color)
        o_grid.add_widget(o_breadcrumb)
        o_grid.add_widget(widgets.Row(height=10))
        # o_grid.add_widget(o_grid_filter)
        o_grid.add_widget(widgets.Row(height=20))
        o_grid.add_widget(lst_grid)
        o_grid.add_widget(widgets.Row(height=20))
        o_grid.add_widget(o_pagination)
        o_grid.add_widget(widgets.Row(height=20))
        dict_resp = service.refresh_page(request, o_grid, app_label, model_name)
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def mark_dynamic_change_form(request, app_label, model_name):
    """
    表单请求
    """
    try:
        dict_resp = service.check_opera_auth(request, app_label, model_name)
        if dict_resp:
            return HttpResponse(json.dumps(dict_resp, ensure_ascii=False), content_type="application/json")

        object_id = int(request.GET.get('id', 0))
        model_admin = admin_api.get_model_admin(app_label, model_name)
        obj = model_admin.model.objects.filter(pk=object_id).first()

        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.style)

        if obj.mark_id is None:
            o_grid = o_module.make_change_form_view(request, model_admin, object_id)
        else:
            o_grid_left = make_mark_base_widget(obj.mark)
            o_grid = o_module.make_change_form_view_2(request, model_admin, object_id, o_grid_left=o_grid_left)

        dict_resp = service.refresh_page(request, o_grid, app_label, model_name)

        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, theme="error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def make_mark_base_widget(obj):
    o_grid = grid.Grid(background_color="#FFFFFF", width=360, horizontal="center")
    o_grid.add_widget(widgets.Image(width=340, url=""))
    o_grid.add_widget(widgets.RowSpacing(20))
    o_grid.add_widget(widgets.Text(text=obj.name))
    o_grid.add_widget(widgets.RowSpacing(5))
    o_grid.add_widget(widgets.Text(text=obj.num))
    return o_grid


def bing_mark(request):
    try:
        object_id = int(request.GET['id'])
        page_index = int(request.GET.get('p', 1))
        mark_id = int(admin_api.get_submit_widget_data(request, "mark_id"))

        from mark.models import MarkTerminal
        o_terminal = MarkTerminal.objects.filter(pk=object_id).first()
        if o_terminal:
            o_terminal.mark_id = mark_id
            o_terminal.save()
            model_admin = admin_api.get_model_admin("mark", "markterminal")
            url = admin_api.make_url(model_admin.get_v_change_list(request, page_index), request, ["id", ])
            o_step = step.Get(url=url, jump=True)
            lst_step = step.make_step(step.Msg("修改完成!", theme="success"), step.GridClose(), o_step)
        else:
            lst_step = step.make_step(step.Msg("修改完成!", theme="success"), step.GridClose())
        dict_resp = {"step": lst_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def unbing_mark(request):
    try:
        object_id = int(request.GET['id'])
        page_index = int(request.GET.get('p', 1))

        from mark.models import MarkTerminal
        o_terminal = MarkTerminal.objects.filter(pk=object_id).first()
        if o_terminal:
            o_terminal.mark_id = None
            o_terminal.save()
            model_admin = admin_api.get_model_admin("mark", "markterminal")
            url = admin_api.make_url(model_admin.get_v_change_list(request, page_index), request, ["id", ])
            o_step = step.Get(url=url, jump=True)
            lst_step = step.make_step(step.Msg("修改完成!", theme="success"), step.GridClose(), o_step)
        else:
            lst_step = step.make_step(step.Msg("修改完成!", theme="success"), step.GridClose())

        dict_resp = {"step": lst_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def v_app_index_view(request):
    try:
        height = 30
        data = [{"label": "告警", "image": widgets.Image(url=settings.STATIC_URL + "app/menu_warn_ic.png", height=height),
                 "image_select": settings.STATIC_URL + "app/menu_warn_ic.png"},
                {"label": "巡视",
                 "image": widgets.Image(url=settings.STATIC_URL + "app/menu_patrol_ic.png", height=height),
                 "image_select": settings.STATIC_URL + "app/menu_patrol_selected_ic.png"},
                {"label": "设备",
                 "image": widgets.Image(url=settings.STATIC_URL + "app/menu_device_ic.png", height=height),
                 "image_select": settings.STATIC_URL + "app/menu_device_selected_ic.png"},
                {"label": "报表",
                 "image": widgets.Image(url=settings.STATIC_URL + "app/menu_forms_ic.png", height=height),
                 "image_select": settings.STATIC_URL + "app/menu_forms_selected_ic.png"},
                ]
        o_tabs = widgets.Tabs(data=data, icon_direction="top", width="100%", height=50, theme="base", average=True)

        o_top = widgets.Panel(width="100%", height=50, background_color="#212121", horizontal="center",
                              suspension_x=0, suspension_y=0)
        o_top.add_widget(widgets.Image(url=settings.STATIC_URL + "app/project.png", height=20), x=5)
        o_top.add_widget(widgets.Text(text="告警", text_size=22, text_color="#FEFEFE"))

        o_panel = widgets.Panel(width="100%", min_height="100%", vertical="top")
        o_panel.add_widget(o_top)
        o_panel.add_widget(o_tabs, x=0, y=-0.1)
        o_page = page.Page(widget=o_panel, down_refresh=True)
        dict_resp = {'step': step.make_step(step.PageUpdate(o_page))}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def repair_total_view(request):
    """
    维修报修统计（报表案例）
    """
    try:

        begin_date = request.GET.get("begin_date", "2019-07-01")
        end_date = request.GET.get("end_date", "2019-07-31")
        is_day = int(request.GET.get("is_day", 1))

        i_type = int(request.GET.get("type", 1))  # 1:工单数量 2:工时 3:完单率
        i_tab = int(request.GET.get("tab", 1))  # 1:人员 2:总量 3:维修项 4：科室

        # 数据打桩 名称、维修单数、审核单数、完成率、工时、费用
        repair_data = [
            ["胡颜斌", 100, 89, 0.89, 300, 300 * 80],
            ["刘德华", 121, 64, 0.64, 245, 245 * 80],
            ["张学友", 89, 89, 1, 152, 152 * 80],
            ["黄渤", 121, 64, 0.23, 245, 245 * 80],
            ["易烊千玺", 221, 64, 0.56, 345, 345 * 80],
        ]

        o_page = page.Page(horizontal="center", background_color="#F8F8F8")
        focus_color = "#54CE47"
        title_height = 50
        # 标题（悬浮）
        # o_grid_title = grid.Grid(col_num=3, width="100%", height=title_height, suspension_x=0, suspension_y=0, background_color="#FFFFFF")
        # o_grid_title.set_col_attr(col=0, horizontal="left", width="20%")
        # o_grid_title.set_col_attr(col=1, horizontal="center")
        # o_grid_title.set_col_attr(col=2, horizontal="right", width="20%")
        #
        # o_step = step.WebViewOpera(go_back=1)
        # o_grid_title.add_widget(widgets.Icon(class_name="el-icon-back", size=24, color="#222222",
        #                                      step=o_step, margin_left=10), col=0)
        # o_grid_title.add_widget(widgets.Text(text="维修统计", text_size=18, bold=True, text_color="#222222"), col=1)
        o_grid_title = widgets_ex.TitleBar(title="维修报修")
        o_page.add_widget(o_grid_title)
        o_page.add_widget(widgets.RowSpacing(title_height))

        # 内容
        o_panel = widgets.Panel()
        o_grid = grid.Grid(col_num=2, width="100%", height=title_height, background_color="#FFFFFF")
        o_grid.set_col_attr(col=0, horizontal="left", width="50%")
        o_grid.set_col_attr(col=1, horizontal="right")
        if is_day:
            o_grid.add_widget(widgets.Text(text="%s -- %s" % (begin_date, end_date), text_size=13, margin_left=10),
                              col=0)
        else:
            o_grid.add_widget(
                widgets.Text(text="%s -- %s" % (begin_date[0:7], end_date[0:7]), text_size=13, margin_left=10), col=0)
        o_step = step.RunScript(
            "hmi.service.repair_date_filter_view/?tab=%s&type=%s&begin_date=%s&end_date=%s&is_day=%s" %
            (i_tab, i_type, begin_date, end_date, is_day))
        o_grid.add_widget(
            widgets.Button(prefix_icon=widgets.Image(url=settings.STATIC_URL + "app/detailCalendar@2x.png", width=24,
                                                     margin_right=5),
                           text="自定义查询", background_color="transparent", focus_color="transparent",
                           text_color=focus_color, step=o_step))
        o_panel.add_widget(o_grid)
        o_panel.add_widget(widgets.Divider(height=2, background_color="#F8F8F8"))

        o_panel.add_widget(widgets.Text(text="数据统计", text_size=16, margin_top=10, margin_bottom=10, margin_left=10))
        o_grid = grid.Grid(col_num=3, width="100%", height=title_height + 20)
        o_grid.set_col_attr(col=0, horizontal="center", width="33%")
        o_grid.set_col_attr(col=1, horizontal="center", width="33%")
        o_grid.set_col_attr(col=2, horizontal="center")
        o_button = widgets.Button(background_color="#54CE47", text_color="#FFFFFF",
                                  focus_color=theme.calc_gradient_color("#54CE47"),
                                  round=100, width=100, height=40, jump=True)
        o_button_click = widgets.Button(background_color="transparent", text_color=focus_color,
                                        border_color=focus_color,
                                        focus_color="transparent",
                                        focus_text_color=theme.calc_gradient_color(focus_color),
                                        round=100, width=100, height=40, jump=True)

        url = "/repair_total_view/?tab=%s&type=1&begin_date=%s&end_date=%s&is_day=%s" % (
            i_tab, begin_date, end_date, is_day)
        if i_type == 1:
            o_button.text = "工单数量"
            o_button.url = url
            o_grid.add_widget(o_button.render(), col=0)
        else:
            o_button_click.text = "工单数量"
            o_button_click.url = url
            o_grid.add_widget(o_button_click.render(), col=0)

        url = "/repair_total_view/?tab=%s&type=2&begin_date=%s&end_date=%s&is_day=%s" % (
            i_tab, begin_date, end_date, is_day)
        if i_type == 2:
            o_button.text = "工时"
            o_button.url = url
            o_grid.add_widget(o_button.render(), col=1)

        else:
            o_button_click.text = "工时"
            o_button_click.url = url
            o_grid.add_widget(o_button_click.render(), col=1)

        url = "/repair_total_view/?tab=%s&type=3&begin_date=%s&end_date=%s&is_day=%s" % (
            i_tab, begin_date, end_date, is_day)
        if i_type == 3:
            o_button.text = "完单率"
            o_button.url = url
            o_grid.add_widget(o_button.render())
        else:
            o_button_click.text = "完单率"
            o_button_click.url = url
            o_grid.add_widget(o_button_click.render())
        o_panel.add_widget(o_grid)

        o_table = widgets.Table(col_width={0: 80}, select=False, row_border=False)
        for item in repair_data:
            if i_type == 1:
                percentage = int(item[3] * 85)
                o_table.data.append([item[0], [widgets.Panel(height=5, width="%s%%" % percentage,
                                                             background_color=random.choice(const.COLOR_RANDOM),
                                                             margin_right=5),
                                               item[1]]
                                     ])
            elif i_type == 2:
                percentage = int(item[3] * 85)
                o_table.data.append([item[0], [widgets.Panel(height=5, width="%s%%" % percentage,
                                                             background_color=random.choice(const.COLOR_RANDOM),
                                                             margin_right=5),
                                               item[4]]
                                     ])
            else:
                percentage = int(item[3] * 85)
                o_table.data.append([item[0], [widgets.Panel(height=5, width="%s%%" % percentage,
                                                             background_color=random.choice(const.COLOR_RANDOM),
                                                             margin_right=5),
                                               "%s%%" % int(item[3] * 100)]
                                     ])

        o_panel.add_widget(o_table)
        o_panel.add_widget(widgets.RowSpacing(20))
        o_panel.add_widget(widgets.Divider(height=2, background_color="#F8F8F8"))

        o_grid = grid.Grid(col_num=2, width="100%", height=title_height, background_color="#FFFFFF")
        o_grid.set_col_attr(col=0, horizontal="left", width="50%")
        o_grid.set_col_attr(col=1, horizontal="right")
        o_grid.add_widget(widgets.Text(text="数据详情", text_size=16, margin_left=10), col=0)
        o_step = step.RunScript(
            "hmi.service.repair_total_download/?tab=%s&type=%s&begin_date=%s&end_date=%s&is_day=%s" %
            (i_tab, i_type, begin_date, end_date, is_day))
        o_grid.add_widget(
            widgets.Button(prefix_icon=widgets.Icon(class_name="el-icon-download", size=16, color=focus_color),
                           text="下载", text_color=focus_color, focus_color="transparent", background_color="transparent",
                           step=o_step), col=1)
        o_panel.add_widget(o_grid)
        o_panel.add_widget(widgets.Divider(height=2, background_color="#F8F8F8"))
        o_table = widgets.Table(col_width={0: 30, 1: 80, 2: 60, 3: 60, 4: 70}, select=False, focus_color="transparent",
                                head=["", "姓名", "维修单数", "审核单数", "完单率", "工作量(小时)", "费用"], head_show=True)
        for i, item in enumerate(repair_data):
            o_table.data.append([i + 1, item[0], item[1], item[2], "%s%%" % int(item[3] * 100), item[4], item[5]])

        o_panel.add_widget(o_table)
        o_panel.add_widget(widgets.RowSpacing(20))

        data = []
        o_step = step.Get(url="/repair_total_view/?tab=1&type=%s&begin_date=%s&end_date=%s&is_day=%s" %
                              (i_type, begin_date, end_date, is_day), jump=True)
        if i_tab == 1:
            data.append({"label": "人员", "grid": o_panel, "id": 1})
        else:
            data.append({"label": "人员", "step": o_step, "id": 1})

        o_step = step.Get(url="/repair_total_view/?tab=2&type=%s&begin_date=%s&end_date=%s&is_day=%s" %
                              (i_type, begin_date, end_date, is_day), jump=True)
        if i_tab == 2:
            data.append({"label": "总量", "grid": o_panel, "id": 2})
        else:
            data.append({"label": "总量", "step": o_step, "id": 2})

        o_step = step.Get(url="/repair_total_view/?tab=3&type=%s&begin_date=%s&end_date=%s&is_day=%s" %
                              (i_type, begin_date, end_date, is_day), jump=True)
        if i_tab == 3:
            data.append({"label": "维修项", "grid": o_panel, "id": 3})
        else:
            data.append({"label": "维修项", "step": o_step, "id": 3})

        o_step = step.Get(url="/repair_total_view/?tab=4&type=%s&begin_date=%s&end_date=%s&is_day=%s" %
                              (i_type, begin_date, end_date, is_day), jump=True)
        if i_tab == 4:
            data.append({"label": "科室", "grid": o_panel, "id": 4})
        else:
            data.append({"label": "科室", "step": o_step, "id": 4})

        o_tabs = widgets.Tabs(data=data, focus_color=focus_color, tab_width="25%", value=i_tab)

        o_page.add_widget(o_tabs)

        dict_resp = {"step": step.PageUpdate(o_page)}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def repair_view(request):
    """
    维修报修主界面
    """
    try:

        i_tab = int(request.GET.get("tab", 1))  # 1:全部 2:处理中 3:已完成

        # 数据打桩
        # 报修科室、报修电话、报修内容、状态、责任人、时间
        # 状态：1 报修（未指定维修人） 2 代接单（已指定维修人） 3 已接单维修中 4 维修完成提交审批 5 审批完成
        repair_data = [
            ["内科", [18627069211], "6号楼5楼门坏了", 1, "", "2019-7-25 10:10:10"],
            ["外科", [18627069211],
             "6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了",
             2, "刘德华", "2019-7-25 10:10:10"],
            ["体检科", [18627069211], "6号楼5楼门坏了", 3, "黄渤", "2019-7-25 10:10:10"],
            ["心脏科", [18627069211], "6号楼5楼门坏了", 4, "易烊千玺", "2019-7-25 10:10:10"],
            ["外科门诊", [18627069211], "6号楼5楼门坏了", 5, "刘德华", "2019-7-25 10:10:10"],
        ]

        o_page = page.Page(horizontal="center", background_color="#F8F8F8")
        focus_color = "#54CE47"
        title_height = 50
        # 标题（悬浮）
        o_grid_title = widgets_ex.TitleBar(title="维修报修")
        o_page.add_widget(o_grid_title)
        o_page.add_widget(widgets.RowSpacing(title_height))

        # 内容

        o_panel = widgets.Panel(background_color="transparent")
        for item in repair_data:
            auth = item[3]
            o_panel_item = widgets.Panel(vertical="top", background_color="#FFFFFF")
            o_grid = grid.Grid(col_num=2, width="100%", height=30, margin_top=10)
            o_grid.set_col_attr(col=0, horizontal="left", width="50%")
            o_grid.set_col_attr(col=1, horizontal="right")
            o_grid.add_widget(widgets.Text(text=item[-1], margin_left=10), col=0)
            o_grid.add_widget(widgets.Text(text=hmi_service.change_repair_auth(item[3], item[4]), margin_right=10))
            o_panel_item.add_widget(o_grid)
            o_panel_item.add_widget(widgets.RowSpacing(20))
            o_panel_item.add_widget(widgets.Text(text=item[0], margin_left=10))
            o_panel_item.add_widget(widgets.Text(text=item[1], margin_left=10))
            o_panel_item.add_widget(widgets.RowSpacing(20))
            o_panel_item.add_widget(widgets.Text(text=item[2], margin_left=10))
            o_panel_item.add_widget(widgets.RowSpacing(20))
            o_event = event.Event(url="/repair_order_desc_view/?id=1")  # 此处ID要变化
            o_panel_item.add_event(o_event)
            o_panel_auth = widgets.Panel(horizontal="right")

            text_color = random.choice(const.COLOR_RANDOM)
            o_button = widgets.Button(margin_right=10, height=32, width=100, round=80, background_color="transparent",
                                      border_color=text_color, text_color=text_color)
            if auth == 1:
                o_button.text = "派单"
                o_panel_auth.add_widget(o_button.render())
                text_color = random.choice(const.COLOR_RANDOM)
                o_button.border_color = text_color
                o_button.text_color = text_color
                o_button.text = "抢单"
                o_panel_auth.add_widget(o_button.render())
            elif auth == 2:
                o_button.text = "转单"
                o_panel_auth.add_widget(o_button.render())
                text_color = random.choice(const.COLOR_RANDOM)
                o_button.border_color = text_color
                o_button.text_color = text_color
                o_button.text = "接单"
                o_panel_auth.add_widget(o_button.render())
            elif auth == 3:
                pass
            elif auth == 4:
                o_button.text = "拒绝"
                o_panel_auth.add_widget(o_button.render())
                text_color = random.choice(const.COLOR_RANDOM)
                o_button.border_color = text_color
                o_button.text_color = text_color
                o_button.text = "审批"
                o_panel_auth.add_widget(o_button.render())
            o_panel_item.add_widget(o_panel_auth)
            o_panel_item.add_widget(widgets.RowSpacing(20))

            o_panel.add_widget(o_panel_item)
            o_panel.add_widget(widgets.RowSpacing(20, background_color="transparent"))

        data = []
        o_step = step.Get(url="/repair_view/?tab=1", jump=True)
        if i_tab == 1:
            data.append({"label": "全部", "grid": o_panel, "id": 1})
        else:
            data.append({"label": "全部", "step": o_step, "id": 1})

        o_step = step.Get(url="/repair_view/?tab=2", jump=True)
        if i_tab == 2:
            data.append({"label": "处理中", "grid": o_panel, "id": 2})
        else:
            data.append({"label": "处理中", "step": o_step, "id": 2})

        o_step = step.Get(url="/repair_view/?tab=3", jump=True)
        if i_tab == 3:
            data.append({"label": "已完成", "grid": o_panel, "id": 3})
        else:
            data.append({"label": "已完成", "step": o_step, "id": 3})

        o_tabs = widgets.Tabs(data=data, focus_color=focus_color, tab_width="33%", value=i_tab)
        o_page.add_widget(o_tabs)

        dict_resp = {"step": step.PageUpdate(o_page)}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def repair_order_desc_view(request):
    try:

        id = request.GET["id"]  # 定单ID

        # 数据打桩
        # 报修科室、报修电话、报修内容、状态、责任人、时间
        # 状态：1 报修（未指定维修人） 2 代接单（已指定维修人） 3 已接单维修中 4 维修完成提交审批 5 审批完成
        # repair_data = [
        #     ["内科", [18627069211], "6号楼5楼门坏了", 1, "", "2019-7-25 10:10:10"],
        #     ["外科", [18627069211], "6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了",
        #      2, "刘德华", "2019-7-25 10:10:10"],
        #     ["体检科", [18627069211], "6号楼5楼门坏了", 3, "黄渤", "2019-7-25 10:10:10"],
        #     ["心脏科", [18627069211], "6号楼5楼门坏了", 4, "易烊千玺", "2019-7-25 10:10:10"],
        #     ["外科门诊", [18627069211], "6号楼5楼门坏了", 5, "刘德华", "2019-7-25 10:10:10"],
        # ]
        auth = 1
        phone = "18627069211"
        username = "刘德华"
        employer = "内科"
        desc = "6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了 6号楼5楼门坏了"

        o_page = page.Page(horizontal="center", background_color="#F8F8F8")
        focus_color = "#54CE47"
        title_height = 50
        # 标题（悬浮）
        o_grid_title = grid.Grid(col_num=3, width="100%", height=title_height, suspension_x=0, suspension_y=0,
                                 background_color="#FFFFFF")
        o_grid_title.set_col_attr(col=0, horizontal="left", width="20%")
        o_grid_title.set_col_attr(col=1, horizontal="center")
        o_grid_title.set_col_attr(col=2, horizontal="right", width="20%")

        o_step = step.WebViewOpera(go_back=1)
        o_grid_title.add_widget(widgets.Icon(class_name="el-icon-back", size=24, color="#222222",
                                             step=o_step, margin_left=10), col=0)
        o_grid_title.add_widget(widgets.Text(text="工单详情", text_size=18, bold=True, text_color="#222222"), col=1)
        o_page.add_widget(o_grid_title)
        o_page.add_widget(widgets.RowSpacing(title_height))
        o_page.add_widget(widgets.RowSpacing(15))
        o_table = widgets.Table(select=False, background_color="#FFFFFF", col_horizontal={1: "right"})
        o_table.data.append(["报修电话", phone])
        o_table.data.append(["报修人", username])
        o_table.data.append(["报修科室", employer])
        o_page.add_widget(o_table)
        o_page.add_widget(widgets.RowSpacing(15))

        o_panel = widgets.Panel(background_color="#FFFFFF")
        o_panel.add_widget(widgets.RowSpacing(15))
        o_panel.add_widget(widgets.Text(text="问题描述", margin_left=5, margin_bottom=15))
        o_panel.add_widget(widgets.Text(text=desc, margin_left=5, margin_right=5))  # 此外要循环处理
        o_panel.add_widget(widgets.RowSpacing(15))
        o_page.add_widget(o_panel.render())
        o_page.add_widget(widgets.RowSpacing(15))

        o_panel = widgets.Panel(background_color="#FFFFFF")
        o_panel.add_widget(widgets.RowSpacing(15))
        o_panel.add_widget(widgets.Text(text="维修清单", margin_left=5, margin_bottom=15))
        o_grid = grid.Grid(col_num=2)
        o_grid.set_col_attr(col=0, width="50%")
        o_grid.set_col_attr(col=1, horizontal="right")
        o_grid.add_widget(widgets.Text(text="维修内容", margin_left=5), col=0)
        o_grid.add_widget(widgets.Image(url=settings.STATIC_URL + "app/detailAdd@2x.png", width=24,
                                        padding_top=5, margin_right=5, margin_bottom=15))
        o_panel.add_widget(widgets.RowSpacing(15))
        o_panel.add_widget(o_grid)

        # o_panel.add_widget(widgets.Text(text="维修清单", margin_left=5, margin_bottom=15))
        #
        # o_grid = grid.Grid(col_num=2)
        # o_grid.set_col_attr(col=0, width="50%")
        # o_grid.add_widget(widgets.Text(text="耗材（备件）", margin_left=5))
        # o_panel.add_widget(widgets.RowSpacing(15))
        o_page.add_widget(o_panel.render())
        o_page.add_widget(widgets.RowSpacing(15))

        o_grid = grid.Grid(col_num=3, suspension_x=0, suspension_y=-1, height=60, background_color="#FFFFFF")
        o_grid.set_col_attr(col=0, width="33%")
        o_grid.set_col_attr(col=1, width="33%")
        text_color = random.choice(const.COLOR_RANDOM)
        o_button = widgets.Button(margin_right=10, height=32, width=100, round=80, background_color="transparent",
                                  border_color=text_color, text_color=text_color)
        if auth == 1:
            o_button.text = "派单"
            o_grid.add_widget(o_button.render(), col=1)
            text_color = random.choice(const.COLOR_RANDOM)
            o_button.border_color = text_color
            o_button.text_color = text_color
            o_button.text = "抢单"
            o_grid.add_widget(o_button.render())
        elif auth == 2:
            o_button.text = "转单"
            o_grid.add_widget(o_button.render(), col=1)
            text_color = random.choice(const.COLOR_RANDOM)
            o_button.border_color = text_color
            o_button.text_color = text_color
            o_button.text = "接单"
            o_grid.add_widget(o_button.render())
        elif auth == 3:
            pass
        elif auth == 4:
            o_button.text = "拒绝"
            o_grid.add_widget(o_button.render(), col=1)
            text_color = random.choice(const.COLOR_RANDOM)
            o_button.border_color = text_color
            o_button.text_color = text_color
            o_button.text = "审批"
            o_grid.add_widget(o_button.render(), col=1)

        o_page.add_widget(o_grid)
        dict_resp = {"step": step.PageUpdate(o_page)}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_widget(request):
    """
    组件测试
    :param request:
    :return:
    """
    try:

        o_page = page.Page(horizontal="center", background_color="#F8F8F8")
        o_audio = widgets.Audio(prefix_icon=widgets.Image(url=settings.STATIC_URL + "vadmin/img/audio.png",
                                                          focus_url=settings.STATIC_URL + "vadmin/img/audio_play.gif"),
                                href=settings.MEDIA_URL + "files/repair.m4a")
        o_page.add_widget(o_audio)
        o_page.add_widget(widgets.RowSpacing(10))
        o_video = widgets.Video(width="100%", href="http://clips.vorwaerts-gmbh.de/big_buck_bunny.mp4")
        o_page.add_widget(o_video)
        o_page.add_widget(widgets.RowSpacing(10))

        o_side_bar = widgets.SideBar(data=[{"label": "热销"}, {"label": "推荐套餐"}], height="100%")
        o_page.add_widget(o_side_bar)
        o_page.add_widget(widgets.RowSpacing(10))

        dict_resp = {"step": step.PageUpdate(o_page)}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, "error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_file_manager(request):
    # dict_resp = service.check_login(request)
    # if dict_resp:
    #     return HttpResponse(json.dumps(dict_resp, ensure_ascii=False), content_type="application/json")

    try:
        o_page = widgets.Page()
        base_path = os.path.join(settings.MEDIA_ROOT, "files")

        def add_item(path, children):
            last_time = None
            for name in os.listdir(path):
                path_name = os.path.join(path, name)
                if os.path.isfile(path_name):
                    size = os.path.getsize(path_name)
                    mtime = os.stat(path_name).st_mtime
                    update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                    if last_time is None or update_time > last_time:
                        last_time = update_time
                    children.append({"name": name, "size": size, "date": update_time})
                else:
                    sub = []
                    last_time = add_item(path_name, sub)
                    children.append({"name": name, "children": sub, "date": last_time})
            return last_time

        data = []
        add_item(base_path, data)
        o_widget = widgets.FileManager(base_url="files", data=data)

        o_page.add_widget(o_widget)

        dict_resp = {'step': step.PageUpdate(o_page)}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, theme="error")
        dict_resp = {"step": o_step}
        return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_template_2_vadmin(request):
    try:
        # 测试template_2_vadmin
        from utils import template_2_vadmin
        o_panel = template_2_vadmin.generate("utils/1.xlsx", is_compile=True, max_row=7, aa=1, bb=2)
        o_page = page.Page(widget=o_panel)
        dict_resp = {"step": step.PageUpdate(o_page)}

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(s_err_info, theme="error")
        dict_resp = {"step": o_step}

    return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


# def test_word_2_vadmin(request):
#     try:
#         from utils import word_2_vadmin
#         obj = word_2_vadmin.generate("templates/docx/案件线索查处情况回复函.docx", is_compile=True)
#         from case.models import Rich
#         o_rich = Rich.objects.filter(pk=1).first()
#         if o_rich is None:
#             o_rich = Rich(id=1)
#
#         lst_input = []
#         lst_html = []
#         for o_widget in obj.lst_widget[2:-2]:
#             lst_input.append(o_widget.render_html(edit=True))
#             lst_html.append(o_widget.render_html())
#         o_rich.input = "".join(lst_input)
#         o_rich.html_output = "<body>%s</body>" % "".join(lst_html)
#         o_rich.save()
#
#         o_panel = widgets.Panel(width=obj.page_width, background_color="#FFFFFF", horizontal="center")
#         o_panel.add_widget(obj.lst_widget)
#
#         o_page = widgets.Page(background_color="#FFFF00", widget=o_panel)
#         result = step.WidgetLoad(o_page)
#
#     except (BaseException,):
#         s_err_info = traceback.format_exc()
#         logger.error(s_err_info)
#         result = step.Msg(s_err_info, msg_type="error")
#
#     return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_timed_refresh(request, **kwargs):
    dict_resp = {"step": [
        step.WidgetUpdate(widget=widgets.Button(name="test_1", text="aaaaaaaa")),
        step.Msg(text="bbbbbbbbbbb")
    ]}
    return HttpResponse(json.dumps(dict_resp, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_swipe(request):
    data = [
        {"content": widgets.Panel(bg_color="#FF0000", width=200, height=300), "label": "#1"},
        {"content": widgets.Panel(bg_color="#FF00FF", width=200, height=300), "label": "#2"},
    ]
    result = step.WidgetLoad(data=widgets.Swipe(width=200, fixed=True, data=data))
    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_carousel(request):
    data = [{"content": widgets.Panel(width=200, height=160, bg_color="#FF0000")},
            {"content": widgets.Panel(width=200, height=160, bg_color="#FFFF00")}]

    o_carousel = widgets.Carousel(width=200, height=160, auto=True, data=data)
    o_carousel_2 = widgets.Carousel(width=200, height=160, auto=True, data=data, direction="horizontal")
    o_carousel_3 = widgets.Carousel(width=200, height=160, auto=True, data=data, direction="horizontal", theme="center")
    result = step.WidgetLoad(data=[o_carousel, o_carousel_2, o_carousel_3])
    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_tabs(request):
    data = [
        {"content": widgets.Panel(bg_color="#FF0000"), "label": "#1"},
        {"content": widgets.Panel(bg_color="#FF00FF"), "label": "#2"},
    ]
    data2 = [
        {"content": widgets.Panel(bg_color="#FF0000"), "label": "#10"},
        {"content": widgets.Panel(bg_color="#FF00FF"), "label": "#20", "id": 2},
    ]
    data3 = [
        {"content": widgets.Panel(bg_color="#FF0000"), "label": "#100"},
        {"content": widgets.Panel(bg_color="#FF00FF"), "label": "#200", "id": 2},
    ]

    result = step.WidgetLoad(data=[widgets.Tabs(width=400, data=data),
                                   widgets.Row(),
                                   widgets.Tabs(width="100%", height=200, data=data2, value=2),
                                   widgets.Row(),
                                   widgets.Tabs(width="100%", height=200, data=data3, value=2,
                                                focus={"color": "#FF0000"}, active={"color": "#333333"}),
                                   widgets.Row(),
                                   widgets.Tabs(data=data, tab_position="left"),
                                   widgets.Tabs(data=data, tab_position="right"),
                                   widgets.Row(),
                                   widgets.Tabs(data=data, tab_position="bottom"),
                                   ])
    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_timeline(request):
    data = [
        {"content": widgets.Panel(bg_color="#FF0000", width=200, height=300),
         "node": widgets.Button(text="#1", border_radius=50, width=60)},
        {"content": widgets.Panel(bg_color="#FF00FF", width=200, height=300),
         "node": "#2"},
        {"content": widgets.Panel(bg_color="#FF0000", width=200, height=300),
         "node": widgets.Button(text="#3", width=120, height=100)}
    ]
    result = step.WidgetLoad(data=[widgets.Timeline(data=data),
                                   widgets.Timeline(align="left", data=data),
                                   widgets.Timeline(align="interval", data=data),
                                   ])
    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def test_collapse(request):
    data = [
        {"content": widgets.Panel(bg_color="#FF00FF", width="100%", height=300), "label": "#1", "expand": True},
        {"content": widgets.Panel(bg_color="#FFFF00", width="100%", height=300,
                                  children=[widgets.Button(text="aaaaaa"), widgets.DatePicker()]), "label": "#2"},
    ]

    data2 = [
        {"content": widgets.Panel(bg_color="#00ffFF", width="100%", height=300), "label": "#3", "expand": True},
        {"content": widgets.Panel(bg_color="#0000ff", width="100%", height=300,
                                  children=[widgets.Button(text="aaaaaa"), widgets.DatePicker()]), "label": "#4"},
    ]
    result = step.WidgetLoad(data=[widgets.Collapse(width="100%", data=data, height=100, bg_color="#FF0000"),
                                   widgets.Row(),
                                   widgets.Collapse(width="100%", data=data2, height=100,
                                                    align="left"),
                                   ])
    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')
