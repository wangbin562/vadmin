# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
case业务模块
"""
import logging
import collections
import copy
import os
from django.conf import settings
from vadmin import widgets
from vadmin import report
from vadmin import step
from vadmin import theme
from utils import template_2_excel

logger = logging.getLogger(__name__)


def repair_date_filter_view(request, **kwargs):
    """
    时间过滤
    """
    is_day = int(request.GET["is_day"])
    begin_date = request.GET["begin_date"]
    end_date = request.GET["end_date"]
    i_type = request.GET["type"]
    i_tab = request.GET["tab"]

    o_panel = widgets.Panel(horizontal="center", background_color="#F8F8F8")
    focus_color = "#54CE47"
    title_height = 50

    o_grid = grid.Grid(col_num=2, width="100%", height=title_height + 20, background_color="#FFFFFF")
    o_grid.set_col_attr(col=0, horizontal="center", width="50%")
    o_grid.set_col_attr(col=1, horizontal="center")

    o_button = widgets.Button(background_color="#54CE47", text_color="#FFFFFF",
                              focus_color=theme.calc_gradient_color("#54CE47"),
                              round=100, width=100, height=40)
    o_button_click = widgets.Button(background_color="transparent", text_color=focus_color,
                                    border_color=focus_color,
                                    focus_color="transparent", focus_text_color=theme.calc_gradient_color(focus_color),
                                    round=100, width=100, height=40)
    from vadmin import js
    o_step = step.RunScript("hmi.service.repair_date_filter_view/?is_day=1&tab=%s&type=%s&begin_date=%s&end_date=%s" %
                            (i_tab, i_type, begin_date, end_date), js_code=js.python_2_js("hmi.service.repair_date_filter_view"))
    if is_day:
        o_button.text = "按天"
        o_button.step = o_step
        o_grid.add_widget(o_button.render(), col=0)
    else:
        o_button_click.text = "按天"
        o_button_click.step = o_step
        o_grid.add_widget(o_button_click.render(), col=0)

    o_step = step.RunScript("hmi.service.repair_date_filter_view/?is_day=0&tab=%s&type=%s&begin_date=%s&end_date=%s" %
                            (i_tab, i_type, begin_date, end_date))
    if not is_day:
        o_button.text = "按月"
        o_button.step = o_step
        o_grid.add_widget(o_button.render())
    else:
        # o_button_click = copy.copy(o_button_click)
        o_button_click.text = "按月"
        o_button_click.step = o_step
        o_grid.add_widget(o_button_click.render())

    o_panel.add_widget(o_grid)
    # o_table = widgets.Table(col_width={0: 100}, select=False, background_color="#FFFFFF")
    if is_day:
        format = "YYYY-mm-dd"
    else:
        format = "YYYY-mm"
    o_grid = grid.Grid(col_num=2, background_color="#FFFFFF", height=60)
    o_grid.set_col_attr(col=0, width=100)
    o_grid.add_widget(widgets.Text(text="开始日期", margin_left=10), col=0)
    o_grid.add_widget(widgets.DatePicker(name="begin_date", format=format, value=begin_date))
    o_panel.add_widget(o_grid)
    o_grid = grid.Grid(col_num=2, background_color="#FFFFFF", height=60)
    o_grid.set_col_attr(col=0, width=100)
    o_grid.add_widget(widgets.Text(text="结束日期", margin_left=10), col=0)
    o_grid.add_widget(widgets.DatePicker(name="end_date", format=format, value=end_date))
    o_panel.add_widget(o_grid)

    # o_table.data.append(["开始日期", widgets.DatePicker(name="begin_date", format=format, value=begin_date)])
    # o_table.data.append(["结束日期", widgets.DatePicker(name="end_date", format=format, value=end_date)])
    # o_panel.add_widget(o_table)
    o_step = step.Get(url="/repair_total_view/?tab=%s&type=%s&is_day=%s" % (i_tab, i_type, is_day),
                      widget_url_para=["begin_date", "end_date"], jump=True)
    o_panel.add_widget(widgets.Text(text="查询", text_size="18", text_color="#54CE47",
                                    width="100%", height=60, background_color="#FFFFFF", step=[o_step, step.GridClose()]))

    return step.GridPopup(o_panel, x=0, y=0, title=None, click_blank_close=True)


def repair_total_download(request, **kwargs):
    begin_date = request.GET["begin_date"]
    end_date = request.GET["end_date"]
    i_type = request.GET["type"]
    i_tab = request.GET["tab"]
    is_day = request.GET["is_day"]

    # 生成excel

    # 根据上面参数查询数据，生成excel表格，此外数据打桩
    repair_data = [
        ["胡颜斌", 100, 89, 300, '89%', 300 * 80],
        ["刘德华", 121, 64, 245, '64%', 245 * 80],
        ["张学友", 89, 89, 152, '89%', 152 * 80],
        ["黄渤", 121, 64, 245, '23%', 245 * 80],
        ["易烊千玺", 221, 64, 345, '56%', 345 * 80],
    ]
    type_name = ""
    if i_tab == 1:
        type_name = "姓名"
    elif i_tab == 2:
        type_name = "时间"
    elif i_tab == 3:
        type_name = "维修项"
    elif i_tab == 4:
        type_name = "科室"
    path = os.path.join(settings.MEDIA_ROOT, "files", "repair_total.xlsx")
    template_2_excel.generate("templates/repair_total.xlsx", path, begin_date=begin_date, end_date=end_date,
                              data=repair_data, type_name=type_name)

    return step.DownloadFile(os.path.join(settings.MEDIA_URL, "files", "repair_total.xlsx"))


def change_repair_auth(auth, username):
    if auth == 1:
        return "代分配"

    elif auth == 2:
        return "%s 代接单" % username

    elif auth == 3:
        return "%s 维修中" % username

    elif auth == 4:
        return "%s 审批中" % username

    return "已完成"
