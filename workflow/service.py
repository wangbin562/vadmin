# !/usr/bin/python
# -*- coding=utf-8 -*-

import importlib
import json
import math
import random
import datetime
from urllib import parse
from vadmin import widgets
from vadmin import step
from vadmin import step_ex
from vadmin import const
from vadmin import admin_api
from vadmin import theme
from vadmin import event
from vadmin import common
from vadmin import service
from vadmin import const
from workflow import models
from workflow.models import Flow
from workflow.models import FlowNode
from workflow.models import FlowData
from workflow.models import FlowNodeData
from user.models import User

list_per_page = 10


def workflow_me_approve(request, loading=True):
    """待我审批的"""
    # user_id = request.user.pk
    dict_state = dict(((1, "待提交"), (2, "审批中"), (3, "审批通过"), (4, "已驳回"), (5, "已撤销")))
    data = []
    # flow_state = request.GET.get('flow_state', None)
    flow = request.GET.get('flow', "")
    submit_user = request.GET.get('submit_user', None)
    if isinstance(submit_user, str):
        submit_user = submit_user.strip()

    page_index = int(request.GET.get('p', 1))
    page_index = page_index or 1
    begin_idx = (page_index - 1) * list_per_page
    end_idx = page_index * list_per_page

    queryset = FlowData.objects.filter(flow_state=models.NODE_TYPE_SUBMIT,
                                       next_approval_user_id=request.user.pk).order_by("-begin_time")
    # if flow:
    #     queryset = queryset.filter(flow_id=flow)
    #
    # if submit_user:
    #     queryset = queryset.filter(user__name__icontains=submit_user)
    #
    # count = 0
    # for o_flow_data in queryset:
    #     flag = False
    #     if check_me_approve(request, o_flow_data):
    #         flag = True
    #
    #     if flag:
    #         if begin_idx <= count < end_idx:
    #             if submit_user:
    #                 url = "/workflow_approval_view/?flow=%s&flow_id=%s&flow_data_id=%s&submit_user=%s" % \
    #                       (flow, o_flow_data.flow_id, o_flow_data.pk, submit_user)
    #             else:
    #                 url = "/workflow_approval_view/?flow=%s&flow_id=%s&flow_data_id=%s" % \
    #                       (flow, o_flow_data.flow_id, o_flow_data.pk)
    #             o_text = widgets.Text(text="%s提交的%s(单号:%s)" % (o_flow_data.user, o_flow_data.flow, o_flow_data.pk),
    #                                   step=step.Get(url=url, jump=True),
    #                                   under_line=True)
    #
    #             o_flow_node = FlowNode.objects.get(flow_id=o_flow_data.flow_id, type="star")
    #             data.append(
    #                 [o_text, make_workflow_custom(request, o_flow_node, flow_data_id=o_flow_data.pk, change_list=True),
    #                  o_flow_data.begin_time,
    #                  o_flow_data.end_time, dict_state.get(o_flow_data.flow_state, None)])
    #         count += 1

    return workflow_filter(request, queryset[begin_idx:end_idx], "/workflow_me_approve/", loading)


def workflow_me_already_approve(request, loading=True):
    """我已审批的"""
    page_index = int(request.GET.get('p', 1))
    flow_state = request.GET.get('flow_state', None)
    flow = request.GET.get('flow', "")
    submit_user = request.GET.get('submit_user', None)
    if isinstance(submit_user, str):
        submit_user = submit_user.strip()

    page_index = page_index or 1
    begin_idx = (page_index - 1) * list_per_page
    end_idx = page_index * list_per_page

    if flow_state:
        queryset = FlowData.objects.filter(flow_state=flow_state).order_by("-begin_time")
    else:
        queryset = FlowData.objects.all().order_by("-begin_time")

    if flow:
        queryset = queryset.filter(flow_id=flow)

    if submit_user:
        queryset = queryset.filter(user__name__icontains=submit_user)

    data = []
    for obj in queryset:
        lst_flow_node_data = FlowNodeData.objects.filter(user_id=request.user.pk, flow_data_id=obj.pk,
                                                         node_type__in=[models.NODE_TYPE_APPROVAL,
                                                                        models.NODE_TYPE_TURN_DOWN])
        if lst_flow_node_data.exists():
            data.append(obj)

    return workflow_filter(request, data[begin_idx:end_idx], "/workflow_me_already_approve/", loading)


def workflow_me_star(request, loading=True):
    """我发起的"""
    page_index = int(request.GET.get('p', 1))
    flow_state = request.GET.get('flow_state', None)
    flow = request.GET.get('flow', "")
    # submit_user = request.GET.get('submit_user', None)
    # if isinstance(submit_user, str):
    #     submit_user = submit_user.strip()

    page_index = page_index or 1
    begin_idx = (page_index - 1) * list_per_page
    end_idx = page_index * list_per_page

    if flow_state:
        queryset = FlowData.objects.filter(user_id=request.user.pk, flow_state=flow_state).order_by("-begin_time")
    else:
        queryset = FlowData.objects.filter(user_id=request.user.pk).order_by("-begin_time")

    if flow:
        queryset = queryset.filter(flow_id=flow)

    return workflow_filter(request, queryset[begin_idx:end_idx], "/workflow_me_star/", loading)


def workflow_me_cc(request, loading=True):
    """抄送我的"""
    # user_id = request.user.pk
    # dict_state = dict(((1, "待提交"), (2, "审批中"), (3, "审批通过"), (4, "已驳回"), (5, "已撤销")))
    # data = []
    page_index = int(request.GET.get('p', 1))
    flow_state = request.GET.get('flow_state', None)
    flow = request.GET.get('flow', "")
    submit_user = request.GET.get('submit_user', None)
    if isinstance(submit_user, str):
        submit_user = submit_user.strip()

    page_index = page_index or 1
    begin_idx = (page_index - 1) * list_per_page
    end_idx = page_index * list_per_page

    if flow_state:
        queryset = FlowData.objects.filter(flow_state=flow_state).order_by("-begin_time")
    else:
        queryset = FlowData.objects.all().order_by("-begin_time")

    if flow:
        queryset = queryset.filter(flow_id=flow).order_by("-begin_time")

    if submit_user:
        queryset = queryset.filter(user__name__icontains=submit_user)

    return workflow_filter(request, [], "/workflow_me_cc/", loading)


def workflow_filter(request, queryset, url, loading=True):
    o_panel = widgets.Panel(width="100%", vertical="top")

    o_theme = theme.get_theme(request.user.pk)
    data = []
    for obj in queryset:
        url2 = common.make_url("/workflow_approval_view/", param={"flow_id": obj.flow_id, "flow_data_id": obj.pk,
                                                                  const.UPN_MENU_ID: "url:/workflow_me_view/",
                                                                  "app_label": obj.app_label,
                                                                  "model_name": obj.model_name,
                                                                  "id": obj.object_id
                                                                  })
        o_step = step.Get(url=url2, jump=True)
        o_row = widgets.Panel(width="100%", round=6, step=o_step, bg_color=o_theme.right_bg_color,
                              padding=10)
        title = "%s提交的%s" % (str(obj.user_create), str(obj.flow))
        o_row.append(widgets.Text(text=title, font={"size": 18, "weight": "bold"}))
        o_row.append(widgets.Row(16))
        o_row.append(widgets.Text(text=obj.desc or ""))
        o_row.append(widgets.Row(8))
        o_row.append(widgets.Text(text=obj.begin_time.strftime("%Y-%m-%d %H:%M:%S")))
        if obj.flow_state in [models.NODE_TYPE_SAVE, models.NODE_TYPE_SUBMIT]:
            o_row.append(widgets.Text(text=" %s " % models.FLOW_STATE.get(obj.flow_state, ""),
                                      font={"color": const.COLOR_PROCESS},
                                      border={"color": const.COLOR_PROCESS, "radius": 8},
                                      position="right"))
        elif obj.flow_state in [models.NODE_TYPE_APPROVAL]:
            o_row.append(widgets.Text(text=" %s " % models.FLOW_STATE.get(obj.flow_state, ""),
                                      font={"color": const.COLOR_SUCCESS},
                                      border={"color": const.COLOR_SUCCESS, "radius": 8},
                                      position="right"))

        elif obj.flow_state in [models.NODE_TYPE_TURN_DOWN]:
            o_row.append(widgets.Text(text=" %s " % models.FLOW_STATE.get(obj.flow_state, ""),
                                      font={"color": const.COLOR_ERROR},
                                      border={"color": const.COLOR_ERROR, "radius": 8},
                                      position="right"))

        elif obj.flow_state in [models.NODE_TYPE_CANCEL]:
            o_row.append(widgets.Text(text=" %s " % models.FLOW_STATE.get(obj.flow_state, ""),
                                      font={"color": const.COLOR_CANCEL},
                                      border={"color": const.COLOR_CANCEL, "radius": 8},
                                      position="right"))

        data.append([o_row, ])
        data.append([widgets.Row(10), ])

    if data:
        data.insert(0, [widgets.Row(10), ])

    if loading:
        return data

    loading_url = const.URL_RUN_SCRIPT % ("workflow.service.%s" % url)
    o_table = widgets.LiteTable(name="p", data=data, width="100%-20", bg={"color": o_theme.bg_color},
                                margin=[0, 10, 0, 10], loading_url=loading_url)
    o_panel.add_widget(o_table)

    # page_total = math.ceil(count / list_per_page)
    # if page_total > 1:
    #     url = common.make_url("/workflow_me_view/", param={const.UPN_MENU_ID: "url:/workflow_me_view/"})
    #     o_pagination = widgets.Pagination(name="p", total=page_total, value=page_index,
    #                                       step=step.Get(url=url, jump=True, splice=['p']))
    #     o_panel.add_widget(o_pagination)

    return o_panel


def make_workflow_head(request, o_node_star, flow_data_id=None):
    o_theme = theme.get_theme(request.user.pk)
    o_flow = o_node_star.flow
    o_panel = widgets.Panel(width="100%", height=70, padding_left=10, bg_color=o_theme.right_bg_color)
    if flow_data_id:
        obj = FlowData.objects.filter(pk=flow_data_id).first()
        title = "%s提交的%s" % (str(obj.user), o_flow.name)
        o_panel.append(widgets.Text(text=title, font={"size": 20}))
    else:
        o_panel.append(widgets.Text(text=o_flow.name, font={"size": 20}))

    return o_panel


def make_workflow_custom(request, o_node_star, flow_data_id=None, change_list=False):
    """
    获取自定义界面数据
    :param request:
    :param o_node_star: 开始结点
    :param flow_data_id: 工作量数据ID，对应FlowData表
    :param change_list: 列表显示(只读）
    :return:
    """
    if flow_data_id:
        o_flow_node_data = FlowNodeData.objects.filter(flow_data_id=flow_data_id, node_type__in=[1, 2, 7]).last()
        if o_flow_node_data and o_flow_node_data.data:
            dict_para = json.loads(o_flow_node_data.data) or {}
        else:
            dict_para = {}

        o_flow_node = o_node_star
        o_flow_data = o_flow_node_data.flow_data
        if o_flow_data.next_node_id:
            o_node = o_flow_data.next_node
            if request.user.pk in get_approve_user(request, o_flow_data, o_node):
                o_flow_node = o_node

        o_panel = _make_workflow_custom(request, o_node_star, o_flow_node,
                                        dict_para, change_list, o_flow_data)

    else:  # 新建
        o_panel = _make_workflow_custom(request, o_node_star, o_node_star,
                                        {}, change_list)

    return o_panel


def _make_workflow_custom(request, o_node_star, o_flow_node, dict_para, change_list, o_flow_data=None):
    o_grid = None

    if o_node_star and o_node_star.view_main:
        o = parse.urlparse(o_node_star.view_main, allow_fragments=True)
        # dict_param = parse.parse_qs(o.query)
        # if dict_param:
        #     common.make_request_url(request, param=dict_param)

        lst_interface = o.path.split(".")
        o_module = importlib.import_module(".".join(lst_interface[0:-1]))
        fun = getattr(o_module, lst_interface[-1])
        if type(fun).__name__ in ['ModelBase']:
            o_theme = theme.get_theme(request.user.id)
            o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
            app_label = request.GET.get("app_label", None)
            model_name = request.GET.get("model_name", lst_interface[2])
            object_id = request.GET.get("id", None)
            model_admin = admin_api.get_model_admin(app_label, model_name=model_name)
            obj = None
            if object_id not in ["", None]:
                obj = model_admin.get_object(request, object_id)
            o_change_form = o_module.ChangeForm(request, model_admin, o_theme, obj)
            # o_change_form.display_mode = const.DM_FORM_LINK

            if o_flow_data and o_flow_data.flow_state != models.NODE_TYPE_SAVE:
                o_change_form.readonly = True
            o_grid = o_change_form.make_form_field(model_admin, obj)
            common.make_request_url(request, param={"app_label": model_admin.opts.app_label, "model_name": model_name})
        else:
            o_grid = fun(request, o_flow_data)

    return o_grid


def make_workflow_attachment(request, o_theme, o_flow_node, readonly_text=True, flow_data_id=None):
    """构造附件组件数据"""
    attachments_value = None
    images_value = None
    if flow_data_id:
        o_flow_node_data = FlowNodeData.objects.filter(flow_data_id=flow_data_id, node_type__in=[1, 2, 7]).last()
        attachments_value = str(o_flow_node_data.attachments) if o_flow_node_data.attachments else None
        images_value = str(o_flow_node_data.images) if o_flow_node_data.images else None

    o_panel = widgets.Panel()
    if o_flow_node is None:
        return o_panel

    o_template = importlib.import_module("vadmin.templates.%s" % o_theme.template)
    o_style = o_template.Style()

    if o_flow_node.attachment_flag:
        o_panel.add_widget(widgets.Row(10))
        o_grid = widgets.Grid(col_num=4, padding=o_style.MARGIN)
        o_grid.set_col_attr(col=0, width=2)
        o_grid.set_col_attr(col=1, horizontal="right", width="16%")
        o_grid.set_col_attr(col=3, width=200)
        # o_grid.set_col_attr(col=1, width=10)
        o_grid.add_widget(widgets.Text(text="附件:     "), col=1)
        o_attachments = widgets.Upload(name="attachments", type="file", multiple=True, value=attachments_value)
        o_grid.add_widget(o_attachments, col=2)
        o_panel.add_widget(o_grid)
        o_panel.add_widget(widgets.Row(10))

    if o_flow_node.image_flag:
        o_panel.add_widget(widgets.Row(10))
        o_grid = widgets.Grid(col_num=4, padding=o_style.MARGIN)
        o_grid.set_col_attr(col=0, width=2)
        o_grid.set_col_attr(col=1, horizontal="right", width="16%")
        o_grid.set_col_attr(col=3, width=200)
        o_grid.add_widget(widgets.Text(text="图片:     "), col=1)
        o_images = widgets.Upload(name="images", type="image_card", multiple=True, value=images_value)
        o_grid.add_widget(o_images, col=2)
        o_panel.add_widget(o_grid)
        o_panel.add_widget(widgets.Row(10))

    o_panel.readonly_text = readonly_text
    return o_panel


def make_workflow_timeline(request, flow_id, flow_data_id, o_theme=None):
    """构造时间轴数据"""

    data = []
    node_width = 46
    node_height = 46
    o_flow_node_data = None
    o_flow_data = FlowData.objects.filter(pk=flow_data_id).first()
    for obj in FlowNodeData.objects.filter(flow_data_id=flow_data_id):
        try:
            label = obj.flow_node.label
        except (BaseException,):
            continue

        if obj.node_type in [models.NODE_TYPE_SAVE, models.NODE_TYPE_SUBMIT, models.NODE_TYPE_RESUBMIT]:
            title = models.FLOW_NODE_TYPE[obj.node_type]
        else:
            title = label or ""

        o_panel = widgets.Panel(width="100%")
        if obj.node_type == models.NODE_TYPE_COMMENT:
            pass
        else:
            o_panel.append(widgets.Text(text=title, font={"size": 18}))
        if request.user.pk == obj.user_id:
            desc = "我(%s)" % models.FLOW_NODE_TYPE[obj.node_type]
        else:
            desc = "%s(%s)" % (str(obj.user), models.FLOW_NODE_TYPE[obj.node_type])

        name = get_username(obj.user)

        o_panel.append(widgets.Row())
        o_panel.append(desc)
        o_panel.append(widgets.Row())

        o_node = None
        if obj.comments:
            comments = obj.comments
            comments = comments.replace("\n", "{{\n}}")
            o_panel.append(widgets.Text(text=comments))
            o_panel.append(widgets.Row())

        if obj.node_type != models.NODE_TYPE_COMMENT:
            o_node = widgets.Button(text=name, width=node_width, height=node_height, font={"size": 14}, round=6)

        o_panel.append(widgets.Text(text=obj.create_time.strftime("%Y-%m-%d %H:%M")))

        data.append({
            "content": o_panel,
            "node": o_node,
        })
        # 记录非评论的最后一个节点
        if obj.node_type != models.NODE_TYPE_COMMENT:
            o_flow_node_data = obj

        # if o_flow_data is None:
        #     o_flow_data = obj.flow_data

    o_flow_node = None
    if o_flow_node_data:
        if o_flow_node_data.node_type == models.NODE_TYPE_TURN_DOWN:
            return widgets.Timeline(data=data, margin_top=20, margin_left=10)

        o_flow_node = o_flow_node_data.flow_node
        o_flow_node = o_flow_node.next_node

    elif o_flow_node is None:
        o_flow_node = FlowNode.objects.filter(flow_id=flow_id, type="star").first()
        o_flow_node = o_flow_node.next_node

    while o_flow_node:
        node_color = const.COLOR_CANCEL
        dict_user = {}
        lst_label = []
        if isinstance(o_flow_node, str):
            for flow_node_id in o_flow_node.split(","):
                o_flow_node = FlowNode.objects.filter(pk=flow_node_id).first()
                if o_flow_data and o_flow_data.next_node_id == o_flow_node.pk:  # 指定了审批人
                    o_user = o_flow_data.next_approval_user
                    if o_user is None and o_flow_data.next_node_id:  # 有可能没有提交
                        dict_user_temp = get_approve_user(request, o_flow_data, o_flow_data.next_node)
                        if dict_user_temp:
                            o_user = list(dict_user_temp.items())[0][1]

                    try:
                        label = o_flow_node.label
                        if label:
                            label = "%s(审批中)" % label
                        else:
                            label = "审批中"
                    except (BaseException,):
                        label = "审批中"

                    node_color = const.COLOR_PROCESS
                    lst_label.append(label)
                    if o_user:
                        dict_user[o_user.pk] = o_user
                    break

                else:
                    # o_flow_node_prev = FlowNode.objects.filter(pk=o_flow_node.prev_node.split(",")[0]).first()
                    dict_user.update(get_approve_user(request, o_flow_data, o_flow_node))
                    try:
                        label = o_flow_node.label
                        label = label or "审批人"
                    except (BaseException,):
                        label = "审批人"

                    if label not in lst_label:
                        lst_label.append(label)
                    break

        elif o_flow_data.next_node_id == o_flow_node.pk:
            o_user = o_flow_data.next_approval_user
            try:
                label = o_flow_node.label
                label = label or "审批人"
            except (BaseException,):
                label = "审批人"

            lst_label.append(label)
            dict_user[o_user.pk] = o_user
        else:
            try:
                label = o_flow_node.label
                label = label or "审批人"
            except (BaseException,):
                label = "审批人"

            lst_label.append(label)

            o_flow_node_prev = FlowNode.objects.filter(pk=o_flow_node.prev_node.split(",")[0]).first()
            dict_user = get_approve_user(request, o_flow_data, o_flow_node_prev)

        title = ""
        name = "..."
        desc = ""
        if lst_label:
            title = ",".join(lst_label)
            if len(dict_user) == 1:
                o_user = list(dict_user.items())[0][1]
                name = get_username(o_user)

            lst_content = []
            for user_id, o_user in dict_user.items():
                lst_content.append(str(o_user))
            desc = "审批人:%s" % ", ".join(lst_content)

        o_panel = widgets.Panel(width="100%")
        o_panel.append(widgets.Text(text=title, font={"size": 18}))
        o_panel.append(widgets.Row())
        o_panel.append(desc)
        o_panel.append(widgets.Row())
        data.append({
            "content": o_panel,
            "node": widgets.Button(text=name, width=node_width, height=node_height, font={"size": 14},
                                   bg={"color": node_color}, round=6)
        })

        o_flow_node = o_flow_node.next_node

    if data:
        return widgets.Timeline(data=data, margin_top=20, margin_left=10)

    return None


def make_operate_button(request, o_flow_data, o_flow_node_star,
                        app_label=None, model_name=None):
    """
    构造操作区域
    """
    if o_flow_data:
        flow_id = o_flow_data.flow_id
        flow_data_id = o_flow_data.pk
    elif o_flow_node_star:
        flow_id = o_flow_node_star.flow_id
        flow_data_id = None
    else:
        flow_id = request.GET["flow_id"]
        flow_data_id = request.GET.get("flow_data_id", None)

    if app_label and model_name:
        common.make_request_url(request, {"flow_id": flow_id, "flow_data_id": flow_data_id,
                                          "app_label": app_label, "model_name": model_name})
    else:
        common.make_request_url(request, {"flow_id": flow_id, "flow_data_id": flow_data_id})

    lst_button = []
    if flow_data_id is None:  # 新建
        o_flow_node = FlowNode.objects.filter(flow_id=flow_id, type="star").first()
        if o_flow_node:
            # if o_flow_node.interface_opera:
            #     o = parse.urlparse(o_flow_node.interface_opera, allow_fragments=True)
            #
            # else:
            o_button = get_save_button(request, o_flow_node, o_flow_data)
            lst_button.append(o_button)

            o_button = get_submit_button(request, o_flow_node, o_flow_data)
            lst_button.append(o_button)
    else:
        o_flow_data = FlowData.objects.get(pk=flow_data_id)
        o_flow_node = o_flow_data.flow_node

        o_node = None
        if o_flow_node.next_node:
            for next_node in o_flow_node.next_node.split(","):
                o_node = FlowNode.objects.filter(pk=next_node).first()
                dict_user = get_approve_user(request, o_flow_data, o_node)
                if request.user.pk in dict_user:
                    break

        # if o_node and o_node.interface_opera:
        #     o = parse.urlparse(o_node.interface_opera, allow_fragments=True)
        #     dict_param = parse.parse_qs(o.query)
        #     lst_interface = o.path.split(".")
        #     o_module = importlib.import_module(".".join(lst_interface[0:-1]))
        #     fun = getattr(o_module, lst_interface[-1])
        #     o_button = fun(request, o_node, o_flow_data, **dict_param)
        #     lst_button.append(o_button)
        #
        # else:
        # 评论
        o_button = get_comment_button(request, o_flow_data)
        if o_button is not None:
            lst_button.append(o_button)

        # 保存
        o_button = get_save_button(request, o_flow_node_star, o_flow_data)
        if o_button is not None:
            lst_button.append(o_button)

        # 提交
        o_button = get_submit_button(request, o_flow_node_star, o_flow_data)
        if o_button is not None:
            lst_button.append(o_button)

        # 审核
        o_button = get_approval_button(request, o_flow_data)
        if o_button is not None:
            lst_button.append(o_button)

        # 驳回
        o_button = get_turn_down_button(request, o_flow_data)
        if o_button is not None:
            lst_button.append(o_button)

        # 撤销
        o_button = get_cancel_button(request, o_flow_node, o_flow_data)
        if o_button is not None:
            lst_button.append(o_button)

    return lst_button


def make_approval_view(request, o_flow_data, o_step, o_node=None):
    o_panel = widgets.Grid(width="100%", horizontal="left")
    o_panel.add_widget(widgets.Input(name="desc", input_type="textarea", width="100%-40", height=200,
                                     margin=[0, 20, 0, 20]))
    o_panel.add_widget(widgets.Row(20))

    if o_flow_data is None:  # 新建时为空，取第一个节点的下一个节点
        flow_node_id = o_node.next_node.split(",")[0]
        o_flow_node = FlowNode.objects.get(pk=flow_node_id)
    else:
        if o_flow_data.next_node_id and o_flow_data.next_node.next_node:
            flow_node_id = o_flow_data.next_node.next_node.split(",")[0]
            o_flow_node = FlowNode.objects.get(pk=flow_node_id)
        else:
            o_flow_node = None

    if o_flow_node:
        dict_user = get_approve_user(request, o_flow_data, o_flow_node)
        data = []
        for k, v in dict_user.items():
            data.append([k, str(v)])

        if data:
            value = data[0][0]
        else:
            value = None

        if len(data) <= 1:
            o_select = widgets.Select(name="user_id", data=data, value=value, required=True, hide=True)
        else:
            o_panel.append(widgets.Text(text="请选择下一步骤审批人：", margin_left=20, height=32))
            o_select = widgets.Select(name="user_id", data=data, value=value, required=True)

        o_panel.append(o_select)

    result = step_ex.ConfirmBox(title="同意", width="90%", data=o_panel, step=[step.LayerClose(), o_step],
                                request=request)
    return result


def make_approval_comments_view(request, o_step):
    o_panel = widgets.Panel(width="100%", horizontal="center")
    o_panel.add_widget(widgets.Input(name="desc", input_type="textarea", width="100%-40", height=200, padding=20))
    o_panel.add_widget(widgets.Row(20))
    result = step_ex.ConfirmBox(title="评论", width="90%", data=o_panel, step=[o_step, step.LayerClose()],
                                request=request)
    return result


def make_approval_turn_down_view(request, o_flow_node, o_step):
    o_panel = widgets.Panel(width="100%", horizontal="center")
    o_panel.add_widget(widgets.Input(name="desc", input_type="textarea", width="100%-40", height=200, padding=10))
    o_panel.add_widget(widgets.Row(20))
    # o_node_first = FlowNode.objects.filter(flow_id=o_flow_node.flow_id, type="star").first()
    # if o_flow_node.go_back_interface:
    #     o = parse.urlparse(o_flow_node.go_back_interface, allow_fragments=True)
    #     dict_param = parse.parse_qs(o.query)
    #     lst_interface = o.path.split(".")
    #     o_module = importlib.import_module(".".join(lst_interface[0:-1]))
    #     fun = getattr(o_module, lst_interface[-1])
    #     o_node = fun(request, o_flow_node, **dict_param)
    #     o_radio = widgets.Input(name="node_id", value=o_node.pk, padding_left=10, hide=True)
    #     o_grid.add_widget(o_radio)
    #     o_radio = widgets.InputNumber(name="return", value=10, padding_left=10, hide=True)
    #     o_grid.add_widget(o_radio)

    # if o_flow_node.go_back_flag:
    #     o_event = event.Event("change", step=step.RunScript("workflow.service.change_turn_down_node"))
    #     o_radio = widgets.Radio(name="return", data=((4, "返回提交人"), (9, "返回上一步")),
    #                             value=9, padding_left=10, event=o_event)
    #     o_grid.add_widget(o_radio)
    #
    #     if o_flow_node.prev_node and "," in o_flow_node.prev_node:
    #         data = []
    #         for node in o_flow_node.prev_node.split(","):
    #             o_node = FlowNode.objects.get(pk=node)
    #             data.append((o_node.pk, o_node.label or o_node.pk))
    #         value = data[0][0]
    #
    #         o_grid.add_widget(widgets.Row(20))
    #         o_radio = widgets.Radio(name="node_id", data=data, value=value, padding_left=10, hide=True)
    #         o_grid.add_widget(widgets.Text(name="node_text", text="返回上一步步骤：", padding_left=10, hide=True))
    #         o_grid.add_widget(widgets.Row(10))
    #         o_grid.add_widget(o_radio)

    result = step_ex.ConfirmBox(title="驳回", width="90%", data=o_panel, step=[o_step, step.LayerClose()],
                                request=request)
    return result


def check_me_approve(request, o_flow_data):
    flag = False
    if o_flow_data.flow_node_id is None:
        return flag

    o_flow_node = o_flow_data.flow_node
    if o_flow_node is None:
        return flag

    if o_flow_node.next_node in ["", None]:
        return flag

    for node_id in o_flow_node.next_node.split(","):
        o_flow_node = FlowNode.objects.filter(pk=node_id).first()
        dict_user = get_approve_user(request, o_flow_data, o_flow_node)
        if request.user.pk in dict_user:
            flag = True
            break

    return flag


def get_approve_user(request, o_flow_data, o_flow_node):
    """获取审批用户"""
    dict_user = {}
    if not isinstance(o_flow_node, FlowNode):
        return dict_user

    if o_flow_node.approval_user and o_flow_node.approval_user != "[]":
        lst_user_id = eval(o_flow_node.approval_user)
        dict_user = {}
        for obj in User.objects.filter(pk__in=lst_user_id):
            dict_user[obj.pk] = obj

    elif o_flow_node.approval_interface:
        o = parse.urlparse(o_flow_node.approval_interface, allow_fragments=True)
        # dict_param = parse.parse_qs(o.query)
        lst_interface = o.path.split(".")
        o_module = importlib.import_module(".".join(lst_interface[0:-1]))
        fun = getattr(o_module, lst_interface[-1])
        result = fun(request, o_flow_data)
        if isinstance(result, list):
            for k, v in result:
                dict_user[k] = v
        else:
            dict_user = result

    # if o_flow_node.default_approval:
    #     for user_id in o_flow_node.default_approval.split(","):
    #         o_user = User.objects.filter(pk=user_id).first()
    #         dict_user[o_user.pk] = o_user
    #
    # elif o_flow_node.department_id and o_flow_node.role_id:
    #     for o_user in User.objects.filter(department_id=o_flow_node.department_id, role_id=o_flow_node.role_id):
    #         dict_user[o_user.pk] = o_user
    #
    # elif o_flow_node.interface_approval:  # 接口返回审批人
    #     o = parse.urlparse(o_flow_node.interface_approval, allow_fragments=True)
    #     dict_param = parse.parse_qs(o.query)
    #     lst_interface = o.path.split(".")
    #     o_module = importlib.import_module(".".join(lst_interface[0:-1]))
    #     fun = getattr(o_module, lst_interface[-1])
    #     lst_user = fun(request, o_flow_node, **dict_param)
    #     for o_user in lst_user:
    #         dict_user[o_user.pk] = o_user

    return dict_user


def get_username(user):
    if hasattr(user, "name") and user.name:
        name = user.name[-2:]
    else:
        name = user.username

    return name


def update_flow_data(request, flow_data_id, opera_node_id,
                     opera_type, object_id=None, next_node_id=None, approval_user_id=None,
                     perv_node_id=None, state_desc=None):
    """

    :param request:
    :param flow_data_id: 流程数据ID
    :param opera_node_id: 当前操作ID
    :param opera_type:  操作类型
    :param object_id: 保存的model id
    :param next_node_id: 下一步节点ID，下一步有多个节点的情况下，前端提交时必须选择
    :param approval_user_id: 下一步审批人，结点中配置了select_approval，前端提交时必须选择
    :param perv_node_id: 上一步节点ID，上一步有多个节点的情况下，前端返回时必须选择
    :param state_desc: 自定义状态（一般在自定义结点中使用）
    :return:
    """
    widget_data = request.POST.get(const.SUBMIT_WIDGET, "{}")
    dict_data = json.loads(widget_data)
    app_label = request.GET.get("app_label", None)
    model_name = request.GET.get("model_name", None)

    # NODE_TYPE_SAVE = 1  # 待提交 / 保存
    # NODE_TYPE_SUBMIT = 2  # 已提交 / 审批中
    # NODE_TYPE_APPROVAL = 3  # 审批通过
    # NODE_TYPE_TURN_DOWN = 4  # 已驳回
    # NODE_TYPE_CANCEL = 5  # 已撤销
    # NODE_TYPE_COMMENT = 6  # 添加评论
    # NODE_TYPE_RESUBMIT = 7  # 重新提交申请
    # NODE_TYPE_TURN_DOWN_PREV = 8  # 驳回（上一步）
    # flow_state = ((1, "待提交"), (2, "审批中"), (3, "审批通过"), (4, "已驳回"), (5, "已撤销"))
    # opera_type = ((1, "保存"), (2, "提交申请"), (3, "同意"),
    #                                              (4, "驳回（提交人"), (5, "撤销"),
    #                                              (6, "添加评论"), (7, "重新提交申请"), (8, "驳回（上一步）"))
    user_id = request.user.pk  # 此处要判读代填写的情况

    o_flow_node = FlowNode.objects.get(pk=opera_node_id)
    flow_id = o_flow_node.flow_id

    if flow_data_id in ["", None]:
        o_flow_data = FlowData(user_id=user_id, user_create_id=user_id, flow_id=flow_id, object_id=object_id)
    else:
        o_flow_data = FlowData.objects.filter(pk=flow_data_id).first()

    flow_state = opera_type
    if opera_type in [models.NODE_TYPE_SUBMIT, models.NODE_TYPE_RESUBMIT]:
        # if o_flow_data.flow_state != 1:
        #     opera_type = 7
        flow_state = models.NODE_TYPE_SUBMIT

    elif opera_type == models.NODE_TYPE_APPROVAL:
        if o_flow_node.next_node:
            flow_state = models.NODE_TYPE_SUBMIT

    # elif opera_type in [8, ]:  # 返回上一步，上一步有可能有多个,返回操作的那一步
    #     if perv_node_id is None:
    #         next_node = o_flow_data.flow_node_id
    #
    #     o_node = FlowNode.objects.get(pk=next_node)
    #     if o_node.type == "star":
    #         flow_state = 1
    #         o_flow_node = o_node
    #     else:
    #         flow_state = 2
    #         for node in o_node.prev_node.split(","):
    #             o_flow_node = FlowNode.objects.get(pk=node)
    #             break
    #
    #     approval_user_id = o_flow_data.user_id

    if opera_type != models.NODE_TYPE_COMMENT:  # 不等于评论
        o_flow_data.flow_state = flow_state

        # 审批完成或者取消申报流则记录结束时间
        if flow_state in [models.NODE_TYPE_APPROVAL, models.NODE_TYPE_CANCEL]:
            o_flow_data.end_time = datetime.datetime.now()

        if not next_node_id:
            # if opera_type in [models.NODE_TYPE_SAVE, models.NODE_TYPE_TURN_DOWN]:
            #     o_flow_node = FlowNode.objects.filter(flow_id=flow_id, type="star").first()
            #     next_node = o_flow_node.next_node
            # elif perv_node_id is not None:
            #     next_node = perv_node_id
            # else:
            #     next_node = o_flow_node.next_node

            next_node_id = o_flow_node.next_node.split(",")[0]  # 取第一个

        if not approval_user_id:
            o_next_node = FlowNode.objects.filter(pk=next_node_id).first()

            if o_next_node:
                dict_user = get_approve_user(request, o_flow_data, o_next_node)
                if dict_user:
                    approval_user_id = list(dict_user.items())[0][0]

        if o_flow_data.user_id is None:
            o_flow_data.user_id = user_id

        o_flow_data.flow_node_id = o_flow_node.pk
        o_flow_data.flow_node_user_id = request.user.pk
        o_flow_data.next_node_id = next_node_id
        o_flow_data.next_approval_user_id = approval_user_id
        # o_flow_data.opera_node_id = opera_node
        o_flow_data.app_label = app_label
        o_flow_data.model_name = model_name
        o_flow_data.save()

    FlowNodeData.objects.create(user_id=user_id, flow_id=flow_id, flow_node_id=o_flow_node.pk,
                                next_node_id=next_node_id,
                                flow_data_id=o_flow_data.pk, data=json.dumps(dict_data, ensure_ascii=False),
                                attachments=str(dict_data.get("attachments", "[]")),
                                images=str(dict_data.get("images", "[]")),
                                node_type=opera_type, comments=dict_data.get("desc", None),
                                state_desc=state_desc)

    return o_flow_data


def get_save_button(request, o_flow_node, o_flow_data):
    """获取保存按钮"""
    if (o_flow_data is None) or (o_flow_data.flow_state in [1, 4] and request.user.pk == o_flow_data.user_id):
        if o_flow_data is None:
            url = common.make_url("/workflow_save/", request,
                                  param={"flow_node_id": o_flow_node.pk})
        else:
            url = common.make_url("/workflow_save/", request,
                                  param={"flow_node_id": o_flow_node.pk, "flow_data_id": o_flow_data.pk,
                                         "id": o_flow_data.object_id})
        o_step = step.Post(url=url)
        o_button = widgets.Button(text="保存", width=100, step=o_step)
        return o_button

    return None


def get_submit_button(request, o_flow_node, o_flow_data, button_text="提交"):
    """获取提交按钮"""
    if (o_flow_data is None) or (o_flow_data.flow_state in [1, 4] and request.user.pk == o_flow_data.user_id):
        if o_flow_data is None:
            url = common.make_url("/workflow_submit/", request,
                                  param={"flow_node_id": o_flow_node.pk})
        else:
            url = common.make_url("/workflow_submit/", request,
                                  param={"flow_node_id": o_flow_node.pk, "flow_data_id": o_flow_data.pk,
                                         "id": o_flow_data.object_id})
        o_step = step.Post(url=url, check_required=True, submit_type="all")
        # o_step = step.GridPopup(make_approval_view(o_flow_node, o_step), title=button_text)
        o_button = widgets.Button(text=button_text, width=100,
                                  step=make_approval_view(request, o_flow_data, o_step, o_flow_node))
        return o_button

    return None


def get_comment_button(request, o_flow_data=None):
    """获取评论按钮"""
    if o_flow_data and o_flow_data.flow_state in [2, 3]:
        # url = common.make_url("/workflow_comment/", request,
        #                       param={"flow_node_id": o_flow_data.flow_node_id, "flow_data_id": o_flow_data.pk,
        #                              "id": o_flow_data.object_id})
        # o_step = step.Post(url=url)
        o_step = step.ViewOpera(back=1)
        o_button = widgets.Button(text="评论", width=100, icon="fa-comment-o",
                                  step=make_approval_comments_view(request, o_step))
        return o_button

    return None


def get_approval_button(request, o_flow_data=None, button_text="同意"):
    """获取审批同意按钮"""
    if o_flow_data and o_flow_data.flow_state in [models.NODE_TYPE_SUBMIT, ] and o_flow_data.next_node_id:
        flag = False
        o_flow_node = o_flow_data.next_node
        if o_flow_data.next_approval_user_id:  # 指定的审批人
            if o_flow_data.next_approval_user_id == request.user.pk:
                flag = True

        elif request.user.pk in get_approve_user(request, o_flow_data, o_flow_node):
            flag = True

        if flag:
            url = common.make_url("/workflow_approval/", request,
                                  param={"flow_data_id": o_flow_data.pk, "flow_node_id": o_flow_node.pk,
                                         "id": o_flow_data.object_id})
            o_step = step.Post(url=url, check_required=True)
            # o_step = step.LayerPopup(data=make_approval_view(request, o_flow_data, o_step),
            #                          title=button_text, width="90%", max_width=600)

            o_button = widgets.Button(text=button_text, width=100,
                                      step=make_approval_view(request, o_flow_data, o_step))
            return o_button

    return None


def get_turn_down_button(request, o_flow_data=None, button_text="驳回"):
    """获取审批驳回按钮"""
    if o_flow_data and o_flow_data.flow_state in [2, ] and o_flow_data.next_node_id:
        flag = False
        o_node = o_flow_data.next_node
        if o_flow_data.next_approval_user_id:
            if o_flow_data.next_approval_user_id == request.user.pk:
                flag = True

        elif request.user.pk in get_approve_user(request, o_flow_data, o_node):
            flag = True

        if flag:
            url = common.make_url("/workflow_turn_down/?flow_node_id=%s&id=%s" %
                                  (o_node.pk, o_flow_data.object_id), request)
            o_step = step.Post(url=url)
            o_button = widgets.Button(text=button_text, width=100,
                                      step=make_approval_turn_down_view(request, o_node, o_step))
            return o_button

    return None


def get_cancel_button(request, o_flow_node, o_flow_data=None):
    if o_flow_data and o_flow_data.flow_state in [1, 4] and request.user.pk == o_flow_data.user_id:
        url = "/workflow_cancel/?flow_id=%s&flow_node_id=%s&flow_data_id=%s&id=%s" % \
              (o_flow_node.flow_id, o_flow_node.next_node, o_flow_data.pk, o_flow_data.object_id)
        url = common.make_url(url, request)
        o_step = step.Post(url=url)
        o_button = widgets.Button(text="撤销", width=100, step=o_step)
        return o_button

    return None

# def change_turn_down_node(request, **kwargs):
#     dict_data = kwargs["widget_data"]
#     if dict_data["return"] == 2:
#         return step.WidgetUpdate([widgets.Widget(name="node_id", hide=False),
#                                   widgets.Widget(name="node_text", hide=False)])
#
#     return step.WidgetUpdate([widgets.Widget(name="node_id", hide=True), widgets.Widget(name="node_text", hide=True)])
#
#
# def change_approval_user(request, **kwargs):
#     dict_data = kwargs["widget_data"]
#     node = dict_data["node_id"]
#     o_node = FlowNode.objects.get(pk=node)
#     dict_user = get_approve_user(request, None, o_node)
#     if len(dict_user) > 1:
#         data = []
#         for user_id, o_user in dict_user.items():
#             data.append((user_id, str(o_user)))
#         return step.WidgetUpdate([widgets.Widget(name="user_id", hide=False, data=data, value=data[0][0]),
#                                   widgets.Widget(name="user_text", hide=False)])
#
#     return step.WidgetUpdate([widgets.Widget(name="user_id", hide=True), widgets.Widget(name="user_text", hide=True)])
