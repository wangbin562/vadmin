# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
change 数据处理
"""
import importlib
import json
import random

from django.conf import settings
# from django.contrib.admin.models import LogEntry
from vadmin import admin_api
from vadmin import common
from vadmin import const
from vadmin import event
from vadmin import step
from vadmin import step_ex
from vadmin import theme
from vadmin import widgets
from vadmin_standard.models import CommonLink


def make_index_view(request):
    theme_color = "#94C13D"
    focus_color = common.calc_focus_color(theme_color)
    right_width = 460
    radius = 2
    input_height = 40

    url = settings.STATIC_URL + "login.jpg"
    o_image = widgets.Image(href=url, width="100%%-%s" % right_width, height="100%")

    url = common.make_url("v_login/", request)
    o_step = step.Post(url=url)  # 提交数据，不改变url
    o_panel_right = widgets.Panel(width=right_width, height="100%", bg_color="#FFFFFF",
                                  horizontal="center")
    o_panel_right.render()
    o_text = widgets.Text(text=settings.V_TITLE + "登录", font_size=16, font_color="#878A90")
    o_input_username = widgets.Input(name="username", input_type="text",
                                     width=350, height=input_height, placeholder=u"请输入用户名",
                                     font_color="#878A90", border_color="#D8DBE3", bg_color="transparent",
                                     border_radius=radius, required=True)
    o_event = event.Event(type="keydown", param=[13, 108], step=o_step)
    o_input_username.add_event(o_event)
    o_input_pwd = widgets.Input(name="pwd", input_type="password",
                                width=350, height=input_height, placeholder=u"请输入密码",
                                font_color="#878A90", border_color="#D8DBE3", bg_color="transparent",
                                border_radius=radius, encrypt=settings.V_PWD_ENCRYPT_KEY, required=True)
    o_input_pwd.add_event(o_event)

    o_button = widgets.Button(width=350, height=input_height, text="登录", font_color="#ffffff",
                              bg_color=theme_color, focus_color=focus_color, step=o_step, border_radius=radius)

    o_panel_right.add_widget([o_text, widgets.Row(height=20), o_input_username, widgets.Row(height=20),
                              o_input_pwd, widgets.Row(height=20), o_button])

    user_agent = request.META["HTTP_USER_AGENT"].lower()
    if ("android" in user_agent) or ("iphone" in user_agent):
        o_page = widgets.Page(children=o_panel_right)
    else:
        o_page = widgets.Page(children=[o_image, o_panel_right])

    return step.WidgetLoad(data=o_page)


def common_link_add(request):
    content = request.POST[const.SUBMIT_WIDGET]
    widget_data = json.loads(content)
    name = widget_data["home_add_common_name"]
    link = widget_data["home_add_common_link"]
    if name in ["", None]:
        o_step_msg = step.Msg('名称不能为空！', "warning")
        return o_step_msg

    if link in ["", None]:
        o_step_msg = step.Msg('链接不能为空！', "warning")
        return o_step_msg

    r = lambda: random.randint(0, 255)
    color = '#%02X%02X%02X' % (r(), r(), r())
    CommonLink.objects.create(user_id=request.user.id, name=name, link=link, background_color=color)

    return [step.LayerClose(), step.ViewOpera()]


def common_link_delete(request):
    content = request.POST.get(const.SUBMIT_WIDGET, "{}")
    widget_data = json.loads(content)
    table_name = "common_edit_table"
    lst_id = widget_data.get(table_name, {}).get("value", [])
    if lst_id:
        CommonLink.objects.filter(pk__in=lst_id).delete()

    return [step.LayerClose(), step.ViewOpera()]


def make_update_pwd(request, o_theme, username=None):
    row_height = 30
    lst_row = []
    if username:
        lst_row.append([
            widgets.Text(text="用户名 * ", keyword="*", padding_right=5, height=row_height,
                         font_color=o_theme.font["color"]),
            widgets.Input(name="username", width=300, height=row_height, disabled=True, value=username)
        ])

    lst_row.append([
        widgets.Text(text="旧密码 * ", keyword="*", padding_right=5, height=row_height,
                     font_color=o_theme.font["color"]),
        widgets.Input(name="old_pwd", width=300, height=row_height, input_type="password",
                      encrypt=settings.V_PWD_ENCRYPT_KEY, required=True)
    ])

    lst_row.append([
        widgets.Text(text="新密码  * ", keyword="*", padding_right=5, height=row_height,
                     font_color=o_theme.font["color"]),
        widgets.Input(name="new_pwd", width=300, height=row_height, input_type="password",
                      encrypt=settings.V_PWD_ENCRYPT_KEY, required=True)
    ])
    lst_row.append([
        widgets.Text(text="确定新密码  * ", keyword="*", padding_right=5, height=row_height,
                     font_color=o_theme.font["color"]),
        widgets.Input(name="repeat_pwd", width=300, height=row_height, input_type="password",
                      encrypt=settings.V_PWD_ENCRYPT_KEY, required=True)
    ])

    o_step = step.Post(url=const.URL_UPDATE_PWD, check_required=True)

    o_table = widgets.LiteTable(data=lst_row, width=600, min_row_height=50,
                                col_width={0: "30%"},
                                col_horizontal={0: "right", 1: "left"},
                                bg_color=o_theme.right_bg_color)
    return step_ex.ConfirmBox(title="修改密码", width=600, data=o_table, step=o_step)


def make_update_pwd_other_user(request):
    o_theme = theme.get_theme(request.user.id)
    lst_row = []

    encrypt = settings.V_PWD_ENCRYPT_KEY
    lst_row.append([
        widgets.Text(text="新密码 * ", keyword="*"),
        widgets.Input(name="new_pwd", width=300,
                      input_type="password", encrypt=encrypt, required=True)
    ])
    lst_row.append([
        widgets.Text(text="确定新密码 * ", keyword="*"),
        widgets.Input(name="repeat_pwd", width=300,
                      input_type="password", encrypt=encrypt, required=True)
    ])

    o_step = step.Post(url=const.URL_UPDATE_PWD_OTHER_USER, splice=["username", ], submit_type="layer",
                       check_required=True)

    o_table = widgets.LiteTable(data=lst_row, width=600, min_row_height=50,
                                col_width={0: "30%"},
                                col_horizontal={0: "right", 1: "left"},
                                bg_color=o_theme.right_bg_color)
    return step_ex.ConfirmBox(title="修改密码", width=600, data=o_table, step=o_step)


def make_change_from(request, **kwargs):
    app_label = request.GET["app_label"]
    model_name = request.GET["model_name"]
    grid_name = request.GET.get("grid_name", None)
    object_id = request.GET.get('id', None)
    model_admin = admin_api.get_model_admin(app_label, model_name)
    obj = None
    if object_id is not None:
        obj = model_admin.model.objects.filter(pk=object_id).first()

    o_theme = theme.get_theme(request.user.id)
    o_module = importlib.import_module("vadmin.templates.%s" % o_theme.style)
    o_template = o_module.ChangeFormStyle(request, model_admin, o_theme, obj)
    o_template.v_lite_v = True
    o_grid = o_template.make_form_view(is_save=False)
    # o_grid.background_color = o_theme.right_color
    if grid_name:
        o_grid.name = grid_name
    return step.WidgetUpdate(widget=o_grid, update_method="full")


def make_change_from_inline(request, **kwargs):
    app_label = request.GET["app_label"]
    model_name = request.GET["model_name"]
    grid_name = request.GET.get("grid_name", None)
    object_id = request.GET.get('id', None)  # 外键id
    fk_app_name = request.GET["fk_app_name"]  # 外键app_name
    fk_model_name = request.GET["fk_model_name"]  # 外键model_name
    fk_field = request.GET["fk_field"]  # 外键字段

    o_theme = theme.get_theme(request.user.id)
    o_module = importlib.import_module("vadmin.templates.%s" % o_theme.style)
    model_admin = admin_api.get_model_admin(app_label, model_name)

    fk_model_admin = admin_api.get_model_admin(fk_app_name, fk_model_name)
    if object_id:
        obj = fk_model_admin.model.objects.filter(pk=object_id)
    else:
        obj = None

    fk_model_admin = o_module.ChangeFormStyle(request, model_admin, o_theme, obj)
    o_table = fk_model_admin.make_inline_stacked(model_admin, fk_field)

    o_panel = widgets.Panel(name=grid_name)
    o_panel.add_widget(o_table)
    if model_admin.has_add_permission(request):
        o_button = fk_model_admin.make_inline_add_button(request, model_admin)
        if o_button:
            o_panel.add_widget(widgets.Row(10))
            o_panel.add_widget(o_button)

    o_panel.add_widget(widgets.Input(width=0, height=0))
    return o_panel
