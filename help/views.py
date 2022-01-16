# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
views
"""
import json
import logging
import traceback

from django.http import HttpResponse

from help import service as help_service
from help.models import HelpMenu
from vadmin import const
from vadmin import event
from vadmin import step
from vadmin import theme
from vadmin import widgets
from vadmin.json_encoder import Encoder

logger = logging.getLogger(__name__)


def v_help_view(request):
    try:
        top_menu_id = request.GET.get("top_menu_id", None)
        left_menu_id = request.GET.get("left_menu_id", None)
        content = request.POST.get(const.SUBMIT_HIDE, "{}")
        dict_hide = json.loads(content)
        if left_menu_id and dict_hide:
            return [
                step.WidgetUpdate(
                    data=[{"name": "top_menu", "value": top_menu_id}, {"name": "left_menu", "value": left_menu_id}]),
                help_service.v_help_content(request, left_menu_id)
            ]

        o_theme = theme.get_theme(request.user.pk)
        o_panel = widgets.Panel(width="80%", height="100%")
        o_top = widgets.Panel(height=70, width="100%",
                              float={"top": 0}, border={"color": "#DDDFE6", "width": "0,0,1,0"})

        font_size = o_theme.font["size"] + 2
        font = {"color": o_theme.theme_color, "size": font_size}

        focus = {"line_color": o_theme.theme_color, "line_width": 3, "font_color": o_theme.theme_color}
        border = {"radius": 0}
        o_menu = widgets.Menu(name="top_menu", height=68, direction="horizontal",
                              font=font,
                              bg={"color": "transparent"},
                              border=border,
                              focus=focus)

        queryset = HelpMenu.objects.filter(del_flag=False)
        for obj in queryset:
            if top_menu_id is None:
                top_menu_id = obj.pk
            url = const.URL_RUN_SCRIPT % "help.views.v_help_view" + ("/?top_menu_id=%s" % obj.pk)
            o_menu.add_item({"label": obj.label, "id": obj.pk, "step": step.Post(url=url, submit_type="no", jump=True)})
        o_menu.value = top_menu_id

        o_top.append(widgets.Col(260))

        url = const.URL_RUN_SCRIPT % "help.service.v_help_search"
        o_step = step.Get(url=url, splice="search", loading=False)
        # o_icon = widgets.Icon(icon="el-icon-search", font={"size": 24, "color": "#64B1F0"}, step=o_step)
        o_input = widgets.Input(name="search", width=260, placeholder="搜索文档",
                                height=40, bg_color="#FFFFFF")
        # o_input.add_event(event.Event(type="keydown", param=[13, 108], step=o_step))
        o_input.add_event(event.Event(type="input", step=o_step))
        o_input.add_event(event.Event(type="focus", step=o_step))

        o_top.append(o_input)
        o_top.append(widgets.Col(100))
        o_top.append(o_menu)

        o_panel.append(o_top)

        # o_search = widgets.Panel(name="search_content", width=500, max_height=600,
        #                          float={"top": 70, "left": "{{window.innerWidth * 0.1 + 260}}"})
        # o_panel.append(o_search)

        o_grid = widgets.Grid(width="100%", col_num=2, height="100%-70", vertical="top", scroll={"y": "auto"})
        o_grid.set_col_attr(col=0, width=260)
        o_left_menu, menu_id = help_service.help_left(request, top_menu_id)
        o_left_menu.value = left_menu_id or menu_id
        o_grid.add_widget(o_left_menu, col=0)
        o_right_panel = help_service.help_content(left_menu_id or menu_id)
        o_grid.add_widget(o_right_panel, col=1)
        o_panel.append(widgets.Row(70))
        o_panel.append(o_grid)

        o_page = widgets.Page(horizontal="center", children=o_panel)
        result = [step.WidgetLoad(data=o_page), step.AddHide(data={const.WN_CONTENT_HIDE: 1})]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        result = {}
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')
