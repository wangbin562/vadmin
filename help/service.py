from vadmin import widgets
from vadmin import step
from vadmin import const
from vadmin import event
from vadmin import animation
from vadmin import common
from vadmin import theme
from vadmin import step_ex
from help.models import HelpMenuLeft
from help.models import HelpContent
from help.models import HelpWidgetParam
from help.models import HelpWidgetEvent


def v_help_left(request, top_menu_id=None):
    top_menu_id = request.GET.get("top_menu_id", top_menu_id)
    o_menu, left_menu_id = help_left(request, top_menu_id)

    return step.WidgetUpdate(mode="all", data=o_menu)


def help_left(request, top_menu_id):
    o_theme = theme.get_theme(request.user.pk)
    # hover_bg_color = common.calc_hover_color(o_theme.theme_color)
    o_menu = widgets.Menu(name="left_menu", width="100%", height="100vh-70",
                          font={"color": "#444444"},
                          bg={"color": "transparent"},
                          focus={"bg_color": o_theme.theme_color, "font_color": "#FFFFFF"},
                          hover={"font_color": o_theme.theme_color})
    left_menu_id = None
    queryset = HelpMenuLeft.objects.filter(help_menu_id=top_menu_id).order_by("label")
    for obj in queryset:
        if left_menu_id is None:
            left_menu_id = obj.pk

        url = const.URL_RUN_SCRIPT % "help.views.v_help_view" + \
              ("/?top_menu_id=%s&left_menu_id=%s" % (top_menu_id, obj.pk))
        o_menu.add_item({"label": obj.label, "id": obj.pk, "step": step.Post(url=url, jump=True)})
    o_menu.value = left_menu_id

    return o_menu, left_menu_id


def v_help_content(request, left_menu_id=None):
    left_menu_id = request.GET.get("left_menu_id", left_menu_id)
    o_content = help_content(left_menu_id)
    return step.WidgetUpdate(mode="all", data=o_content)


def help_content(left_menu_id):
    o_content = widgets.Panel(name="right_content", width="100%", height="100vh-70", vertical="top",
                              padding=[20, 20, 20, 20], scroll={"y": "auto"})

    for obj in HelpContent.objects.filter(help_menu_left_id=left_menu_id, del_flag=False):
        if obj.title:
            o_widget1 = widgets.Text(text=obj.title, font={"size": 21, "color": "#1F2F3D"})
            o_content.append(o_widget1)
            o_content.append(widgets.Row(10))

        if obj.sub_title:
            o_widget2 = widgets.Text(text=obj.sub_title, font={"size": 18})
            o_content.append(o_widget2)
            o_content.append(widgets.Row(10))

        if obj.content:
            o_widget3 = widgets.Html(data=obj.content)
            o_content.append(o_widget3)
            o_content.append(widgets.Row())

        if obj.code:
            global o_panel
            c = compile(obj.code.strip(), '', 'exec')
            exec(c, globals())

            o_content.append(o_panel)
            o_content.append(widgets.Row())

            name = "code-%s" % obj.pk
            text = obj.code.replace(" ", "&nbsp;").replace("\n", '<div style="display:block;"></div>')
            o_text = widgets.Text(name=name, text=text, height=0, format_script=0, auto_warp=False)
            o_content.append(o_text)
            o_content.append(widgets.Row(10))

            # keyframes = [["0%", {"height": "0"}], ["100%", {"height": "{{js.getChildrenHeight('%s')}}" % name}]]
            show_animation = animation.Animation(type="fold",
                                                 change_style={"height": "auto"},
                                                 duration="0.3s")

            # keyframes = [["0%", {"height": "{{js.getChildrenHeight('%s')}}" % name}], ["100%", {"height": "0"}]]
            hide_animation = animation.Animation(type="fold",
                                                 change_style={"height": 0}, duration="0.3s")
            o_widget = widgets.ButtonMutex(text="显示代码", active_text="隐藏代码",
                                           width="100%", border={"color": "#EAEEFB"},
                                           prefix=widgets.Icon(icon="el-icon-caret-bottom"),
                                           active_prefix=widgets.Icon(icon="el-icon-caret-top"),
                                           # font={"color": font_color},
                                           bg={"color": "transparent"},
                                           focus={"bg_color": "transparent", "font_color": "#409EFF"},
                                           font={"color": "#409EFF"},
                                           margin_top=-5, value=0,

                                           # event={"click": step.WidgetShow(name=name, animation=show_animation)},
                                           # active_event={"click": step.WidgetHide(name=name,
                                           #                                        animation=hide_animation, )}
                                           event={
                                               "click": step.RunAnimation(name=name, animation=show_animation)},
                                           active_event={
                                               "click": step.RunAnimation(name=name, animation=hide_animation)}
                                           )
            o_content.append(o_widget)
            o_content.append(widgets.Row())

        o_content.append(widgets.Row(40))

    # 参数
    data = []
    for obj in HelpWidgetParam.objects.filter(help_menu_left_id=left_menu_id):
        if obj.desc:
            desc = obj.desc.replace(" ", "&nbsp;").replace("\n", '<div style="display:block;"></div>')
        else:
            desc = ""

        if obj.value:
            value = obj.value.replace(" ", "&nbsp;").replace("\n", '<div style="display:block;"></div>')
        else:
            value = ""

        data.append([obj.name,
                     widgets.Text(text=desc, format_script=0, auto_warp=False),
                     obj.type,
                     widgets.Text(text=value, format_script=0, auto_warp=False),
                     obj.default,
                     const.BOOL_CHINESE.get(obj.required, ""),
                     const.BOOL_CHINESE.get(obj.pc, "是"),
                     const.BOOL_CHINESE.get(obj.phone, "是")])

    if data:
        o_content.append(widgets.Text(text="参数{{row.10}}", font={"size": 21, "color": "#1F2F3D"}))
        data.insert(0, ["参数名称", "说明", "类型", "参数值说明", "默认值", "必填", "支持PC", "支持手机"])
        col_width = {0: 120, 2: 100, 4: 120, 5: 60, 6: 60, 7: 60}
        o_table = widgets.LiteTable(data=data, width="100%", row_border={"color": "#DDDFE6"},
                                    col_width=col_width, min_row_height=40, auto_wrap=True)
        o_content.append(o_table)

    # 事件
    data = []
    for obj in HelpWidgetEvent.objects.filter(help_menu_left_id=left_menu_id):
        data.append([obj.name, obj.desc, obj.param])

    if data:
        o_content.append(widgets.Row(40))
        o_content.append(widgets.Text(text="事件{{row.10}}", font={"size": 21, "color": "#1F2F3D"}))
        data.insert(0, ["事件名称", "事件说明", "提交参数说明"])
        o_table = widgets.LiteTable(data=data, width="100%", row_border={"color": "#DDDFE6"},
                                    min_row_height=40, auto_wrap=True)
        o_content.append(o_table)

    o_content.append(widgets.Row(10))
    return o_content


def v_help_search(request):
    key = request.GET['search']
    data = []
    if key:
        data = []
        for obj in HelpMenuLeft.objects.filter(label__icontains=key, del_flag=False):
            url = const.URL_RUN_SCRIPT % "help.views.v_help_view" + \
                  ("/?top_menu_id=%s&left_menu_id=%s" % (obj.help_menu_id, obj.pk))

            data.append([widgets.Text(text=obj.label, keyword=key,
                                      step=[step.Post(url=url, jump=True), step.LayerClose()])])

    if data:
        o_table = widgets.LiteTable(data=data, width="100%", min_row_height=60, space_left=6,
                                    row_border={"color": "#EEEEEE"}, )
        o_panel = widgets.Panel(name="search_content_panel", width=500, max_height=600, bg={"color": "#FFFFFF"},
                                border={"color": "#EEEEEE", "width": 2}, scroll={"y": "auto"})
        o_panel.append(o_table)
        return step.LayerPopup(name="search_content", related="search", top=40,
                               data=o_panel, modal=0, esc_close=True,
                               click_close=True)
    else:
        return step.LayerClose(name="search_content")
