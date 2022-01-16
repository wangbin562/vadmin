"""
1、电子流的主界面自定义，在流程节点中配置
2、附件的自定义在make_workflow_attachment函数，如果效果要求不一样，可以修改此函数
3、流程时间轴定义在make_workflow_timeline函数，如果效果要求不一样，可以修改此函数
4、整个流程流转界面在workflow_approval_view函数
5、流程审批人可以指定具体责任人（default_approval字段）和角色（role字段），
   例如：在提定审批角色时，提交人是研发部，提定的审指角色是经理，那么研发经理就有审批权
"""

import importlib
import json
import logging
from urllib import parse

from django.db import transaction
from django.http import HttpResponse

from vadmin import admin_api
from vadmin import admin_auth
from vadmin import common
from vadmin import const
from vadmin import service
from vadmin import step
from vadmin import theme
from vadmin import widgets
from vadmin import widgets_ex
from vadmin.json_encoder import Encoder
from workflow import models
from workflow import service as workflow_service
from workflow.models import Flow
from workflow.models import FlowData
from workflow.models import FlowNode
from workflow.models import FlowNodeData

logger = logging.getLogger(__name__)


def workflow_view(request):
    """审批界面"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_panel = widgets.Panel(vertical="top")

        for o_flow in Flow.objects.filter(del_flag=False):
            if o_flow.interface_auth:
                o = parse.urlparse(o_flow.interface_auth, allow_fragments=True)
                dict_param = parse.parse_qs(o.query)
                lst_interface = o.path.split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                fun = getattr(o_module, lst_interface[-1])
                if not fun(request, o_flow, **dict_param):
                    continue

            url = "/workflow_approval_view/?flow_id=%s" % o_flow.pk
            url = common.make_url(url, param={const.UPN_MENU_ID: "url:/workflow_view/"})

            o_step = step.Get(url=url, jump=True)
            o_panel.add_widget(widgets.Button(text=o_flow.name, size=20, width=120, height=60,
                                              step=o_step, margin_left=30, margin_top=30))

        result = service.refresh_page(request, o_panel, menu_value="/workflow_view/")
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_me_view(request, panel=False):
    """审批列表界面"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)
        tabs_name = "workflow_tabs"
        value = request.GET.get(tabs_name, "1")
        tabs_data = [
            {"label": "已发起", "id": "0", "content": workflow_service.workflow_me_star(request, False)},
            {"label": "待处理", "id": "1", "content": workflow_service.workflow_me_approve(request, False)},
            {"label": "已处理", "id": "2", "content": workflow_service.workflow_me_already_approve(request, False)},
            {"label": "抄送我", "id": "3", "content": workflow_service.workflow_me_cc(request, False)},
        ]

        user_agent = request.META["HTTP_USER_AGENT"].lower()
        if ("android" in user_agent) or ("iphone" in user_agent):
            o_panel = widgets.Panel(vertical="top", width="100%", height="100vh")
            o_panel.append(widgets_ex.TitleBar(title="代办事项", bg_color=o_theme.right_bg_color))
            for i in range(4):
                tabs_data[i]["content"].height = "100vh-90"
                tabs_data[i]["content"].scroll = {"y": "drag"}
        else:
            o_panel = widgets.Panel(vertical="top", width="100%", scroll={"y": "hidden"})
            if not panel:
                o_panel.append(widgets_ex.TitleBar(title="代办事项", bg_color=o_theme.right_bg_color, back_icon=None))

        o_panel.append(widgets.Tabs(name=tabs_name, data=tabs_data, value=value, width="100%", tab_width="25%",
                                    event={"change": step.Get(splice=tabs_name, submit_type="update_url")}))
        if panel:
            return o_panel

        result = service.refresh_page(request, o_panel)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


# def workflow_me_approve_view(request):
#     """待我审批的界面"""
#     try:
#         result = admin_auth.check_opera_auth(request)
#         if result:
#             return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#         o_panel = widgets.Panel(width="100%")
#         o_panel.add_widget(workflow_service.workflow_me_approve(request))
#         result = service.refresh_page(request, o_panel, menu_value="/workflow_me_approve_view/")
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#     except (BaseException,):
#         result = admin_auth.save_error(request)
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')

#
# def workflow_me_already_approve_view(request):
#     """我已审批的界面"""
#     try:
#         result = admin_auth.check_opera_auth(request)
#         if result:
#             return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#         o_panel = widgets.Panel(width="100%")
#         o_panel.add_widget(workflow_service.workflow_me_already_approve(request))
#         result = service.refresh_page(request, o_panel, menu_value="/workflow_me_already_approve_view/")
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#     except (BaseException,):
#         result = admin_auth.save_error(request)
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')
#
#
# def workflow_me_star_view(request):
#     """我发起的界面"""
#     try:
#         result = admin_auth.check_opera_auth(request)
#         if result:
#             return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#         o_panel = widgets.Panel(width="100%")
#         o_panel.add_widget(workflow_service.workflow_me_star(request))
#         result = service.refresh_page(request, o_panel, menu_value="/workflow_me_star_view/")
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#     except (BaseException,):
#         result = admin_auth.save_error(request)
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')
#
#
# def workflow_me_cc_view(request):
#     """抄送我的界面"""
#     try:
#         result = admin_auth.check_opera_auth(request)
#         if result:
#             return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#         o_panel = widgets.Panel(width="100%")
#         o_panel.add_widget(workflow_service.workflow_me_cc(request))
#         result = service.refresh_page(request, o_panel, menu_value="/workflow_me_cc_view/")
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")
#
#     except (BaseException,):
#         result = admin_auth.save_error(request)
#         return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_approval_view(request):
    """审批流程主界面"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        o_theme = theme.get_theme(request.user.id)

        flow_id = request.GET["flow_id"]  # 工作流ID
        flow_data_id = request.GET.get("flow_data_id", None)  #

        user_agent = request.META["HTTP_USER_AGENT"].lower()
        if ("android" in user_agent) or ("iphone" in user_agent):
            o_panel = widgets.Panel(width="100%", height="100%", background_color=o_theme.bg_color,
                                    vertical="top", scroll={"y": "auto"}
                                    )
        else:
            o_panel = widgets.Panel(width="100%", height="100%", background_color=o_theme.bg_color,
                                    vertical="top", scroll={"y": "drag"}
                                    )

        o_node_star = FlowNode.objects.filter(flow_id=flow_id, type="star").first()
        o_flow = o_node_star.flow

        readonly_text = False
        o_flow_data = None
        if flow_data_id:
            o_flow_data = FlowData.objects.filter(pk=flow_data_id).first()
            if o_flow_data.flow_state not in [1, 4]:
                readonly_text = True
        # else:
        #     FlowData.objects.create(user_id=request.user.pk, user_create_id=request.user.pk,
        #                             flow_id=flow_id, )

        # 头部
        o_panel.append(widgets_ex.TitleBar(title="详情", bg_color=o_theme.right_bg_color))
        o_head = workflow_service.make_workflow_head(request, o_node_star, flow_data_id)
        o_panel.append(o_head)

        o_panel.append(widgets.Row(10, bg={"color": o_theme.bg_color}))

        # 主界面
        o_grid = workflow_service.make_workflow_custom(request, o_node_star, flow_data_id)
        o_panel_main = widgets.Panel(width="100%-20", margin=[0, 10, 0, 10], bg={"color": o_theme.right_bg_color})
        o_panel_main.append(o_grid)
        o_panel.add_widget(o_panel_main)
        o_panel.append(widgets.Row(10, bg={"color": o_theme.bg_color}))

        # 附件
        o_grid = workflow_service.make_workflow_attachment(request, o_theme, o_node_star, readonly_text,
                                                           flow_data_id)
        o_panel.add_widget(o_grid)

        # 时间轴
        o_grid = workflow_service.make_workflow_timeline(request, flow_id, flow_data_id, o_theme)
        o_panel_timeline = widgets.Panel(width="100%-20", margin=[0, 10, 0, 10], bg={"color": o_theme.right_bg_color},
                                         round=6)
        o_panel_timeline.append(widgets.Text(text="流程", font={"size": 20}, margin=6))
        o_panel_timeline.append(o_grid)
        o_panel.add_widget(o_panel_timeline)
        o_panel.add_widget(widgets.Row(40, bg={"color": o_theme.bg_color}))

        o_theme = theme.get_theme(request.user.id)
        o_module = importlib.import_module("vadmin.templates.%s" % o_theme.template)
        o_template = o_module.Style()
        o_panel_suspension = widgets.Panel(width="100%%-%s" % o_template.WIDTH_LEFT,
                                           height=50, horizontal="center", vertical="center",
                                           border={"color": "#F1F1F2"},
                                           float={"bottom": 0, "left": o_template.WIDTH_LEFT},
                                           bg={"color": o_theme.right_bg_color}
                                           )
        lst_button = workflow_service.make_operate_button(request, o_flow_data, o_node_star)
        for o_button in lst_button:
            o_button.margin_right = 20
        o_panel_suspension.add_widget(lst_button)

        o_panel.add_widget(o_panel_suspension)
        o_panel.add_widget(widgets.Row(20))

        result = service.refresh_page(request, o_panel)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_comment_view(request):
    o_panel = widgets.Panel(percentage_reference="parent")

    return o_panel


def workflow_submit(request):
    """提交电子流，分第一次提交和重复提交"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        flow_id = request.GET["flow_id"]
        flow_node_id = request.GET["flow_node_id"]
        flow_data_id = request.GET.get("flow_data_id", None)
        object_id = request.GET.get('id', None)
        app_label = request.GET.get("app_label", None)
        model_name = request.GET.get("model_name", None)
        # create_time = request.GET.get("create_time", None)  # 如果有时间，则是重复提交
        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)

        o_flow_node = FlowNode.objects.filter(flow_id=flow_id, type="star").first()
        with transaction.atomic():
            node_type = models.NODE_TYPE_SUBMIT
            if flow_data_id:
                if FlowNodeData.objects.filter(flow_data_id=flow_data_id, node_type=models.NODE_TYPE_SUBMIT).exists():
                    node_type = models.NODE_TYPE_RESUBMIT  # 重新提交

            with transaction.atomic():
                next_node_id = widget_data.get("node_id", None)
                approval_user_id = widget_data.get("user_id", None)
                o_flow_data = workflow_service.update_flow_data(request, flow_data_id, flow_node_id, node_type,
                                                                object_id, next_node_id=next_node_id,
                                                                approval_user_id=approval_user_id)

                # 调用自定义接口
                if o_flow_node.submit_interface:
                    o = parse.urlparse(o_flow_node.submit_interface, allow_fragments=True)
                    lst_interface = o.path.split(".")
                    o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                    fun = getattr(o_module, lst_interface[-1])
                    result = fun(request, o_flow_data)
                    if result:
                        try:
                            o_flow_data.pk = "error" * 50  # 手动抛异常，让批处理失败
                            o_flow_data.save()
                        except (BaseException,):
                            pass
                        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                            content_type="application/json")

                elif model_name:  # 使用admin提交保存
                    # o = parse.urlparse(o_flow_node.interface_init_admin, allow_fragments=True)
                    # dict_param = parse.parse_qs(o.query)
                    # common.make_request_url(request, param=dict_param)
                    # app_label, model_name = o.path.split(".", 1)
                    model_admin = admin_api.get_model_admin(app_label, model_name)
                    obj = None
                    if object_id not in ["", None]:
                        obj = model_admin.get_object(request, object_id)

                    import vadmin.service
                    model_admin = admin_api.get_model_admin(app_label, model_name)
                    inline_data = vadmin.service.parse_inline_data(request, model_admin, widget_data)
                    obj, dict_error, msg = vadmin.service.change_form_save(request, model_admin, obj, widget_data,
                                                                           inline_data)
                    if dict_error or msg:
                        if isinstance(msg, step.Step):
                            result = msg
                        else:
                            result = step.OperaFailed(data=dict_error, msg=msg)
                        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                            content_type="application/json")
                    elif not object_id:
                        object_id = obj.pk
                        o_flow_data.object_id = object_id
                        o_flow_data.attr = json.dumps(dict(request.GET), ensure_ascii=False)
                        o_flow_data.save()

        if app_label:
            model_admin = admin_api.get_model_admin(app_label, model_name)
            url = model_admin.get_change_list_url(request)
        else:
            url = common.make_url("/workflow_me_view/", request, param={const.UPN_MENU_ID: "url:/workflow_me_view/"})
        result = [step.Get(url=url, jump=True), step.Msg("已提交")]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_save(request):
    """保存电子流，分第一次保存和重复保存"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        # flow_id = request.GET["flow_id"]
        flow_node_id = request.GET["flow_node_id"]
        flow_data_id = request.GET.get("flow_data_id", None)
        object_id = request.GET.get("id", None)
        app_label = request.GET.get("app_label", None)
        model_name = request.GET.get("model_name", None)

        content = request.POST.get(const.SUBMIT_WIDGET, "{}")
        widget_data = json.loads(content)

        o_flow_node = FlowNode.objects.filter(pk=flow_node_id).first()
        with transaction.atomic():
            opera_type = models.NODE_TYPE_SAVE
            o_flow_data = workflow_service.update_flow_data(request, flow_data_id, flow_node_id, opera_type,
                                                            object_id)

            if o_flow_node.submit_interface:
                o = parse.urlparse(o_flow_node.submit_interface, allow_fragments=True)
                lst_interface = o.path.split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                fun = getattr(o_module, lst_interface[-1])
                result = fun(request, o_flow_data)

                if result:
                    try:
                        o_flow_data.pk = "error" * 50  # 手动抛异常，让批处理失败
                        o_flow_data.save()
                    except (BaseException,):
                        pass

                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")
            elif model_name:  # 使用admin提交保存
                # o = parse.urlparse(o_flow_node.interface_init_admin, allow_fragments=True)
                # dict_param = parse.parse_qs(o.query)
                # common.make_request_url(request, param=dict_param)
                # app_label, model_name = o.path.split(".", 1)
                model_admin = admin_api.get_model_admin(app_label, model_name)
                obj = None
                if object_id not in ["", None]:
                    obj = model_admin.get_object(request, object_id)

                import vadmin.service
                model_admin = admin_api.get_model_admin(app_label, model_name)
                inline_data = vadmin.service.parse_inline_data(request, model_admin, widget_data)
                obj, dict_error, msg = vadmin.service.change_form_save(request, model_admin, obj, widget_data,
                                                                       inline_data)
                if dict_error or msg:
                    if isinstance(msg, step.Step):
                        result = msg
                    else:
                        result = step.OperaFailed(data=dict_error, msg=msg)
                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")
                elif not object_id:
                    object_id = obj.pk
                    o_flow_data.object_id = object_id
                    o_flow_data.attr = json.dumps(dict(request.GET), ensure_ascii=False)
                    o_flow_data.save()

        url = common.make_url("/workflow_approval_view/?flow_data_id=%s" % o_flow_data.pk, request,
                              param={"id": object_id})

        result = [step.Get(url=url, jump=True), step.Msg("已保存")]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_cancel(request):
    """撤销电子流"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        flow_id = request.GET["flow_id"]
        flow_node_id = request.GET["flow_node_id"]
        flow_data_id = request.GET["flow_data_id"]
        object_id = request.GET.get("id", None)
        app_label = request.GET.get("app_label", None)
        model_name = request.GET.get("model_name", None)
        widget_data = request.POST[const.SUBMIT_WIDGET]
        dict_data = json.loads(widget_data)

        with transaction.atomic():
            # 调用自定义接口
            opera_type = models.NODE_TYPE_CANCEL
            o_flow_data = workflow_service.update_flow_data(request, flow_data_id, flow_node_id, opera_type, object_id)

            o_flow_node = FlowNode.objects.get(pk=flow_node_id)
            if o_flow_node.submit_interface:
                o = parse.urlparse(o_flow_node.submit_interface, allow_fragments=True)
                lst_interface = o.path.split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                fun = getattr(o_module, lst_interface[-1])
                result = fun(request, o_flow_data)
                if result:
                    try:
                        o_flow_data.pk = "error" * 50  # 手动抛异常，让批处理失败
                        o_flow_data.save()
                    except (BaseException,):
                        pass

                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")

        if app_label:
            model_admin = admin_api.get_model_admin(app_label, model_name)
            url = model_admin.get_change_list_url(request)
        else:
            url = common.make_url("/workflow_me_view/", request, param={const.UPN_MENU_ID: "url:/workflow_me_view/"})
        result = [step.Get(url=url, jump=True), step.Msg("已撤销")]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_approval(request):
    """审批电子流"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        flow_id = request.GET["flow_id"]
        flow_node_id = request.GET["flow_node_id"]
        flow_data_id = request.GET["flow_data_id"]
        object_id = request.GET.get("id", None)
        app_label = request.GET.get("app_label", None)
        model_name = request.GET.get("model_name", None)
        widget_data = request.POST[const.SUBMIT_WIDGET]
        dict_data = json.loads(widget_data)

        with transaction.atomic():
            opera_type = models.NODE_TYPE_APPROVAL
            next_node_id = dict_data.get("node_id", None)
            approval_user_id = dict_data.get("user_id", None)
            o_flow_data = workflow_service.update_flow_data(request, flow_data_id, flow_node_id, opera_type,
                                                            next_node_id=next_node_id,
                                                            approval_user_id=approval_user_id)

            o_flow_node = o_flow_data.flow_node
            if o_flow_node.submit_interface:
                o = parse.urlparse(o_flow_node.submit_interface, allow_fragments=True)
                lst_interface = o.path.split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                fun = getattr(o_module, lst_interface[-1])
                result = fun(request, o_flow_data)
                if result:
                    try:
                        o_flow_data.pk = "error" * 50  # 手动抛异常，让批处理失败
                        o_flow_data.save()
                    except (BaseException,):
                        pass

                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")

        if app_label:
            model_admin = admin_api.get_model_admin(app_label, model_name)
            url = model_admin.get_change_list_url(request)
        else:
            url = common.make_url("/workflow_me_view/", request, param={const.UPN_MENU_ID: "url:/workflow_me_view/"})
        result = [step.Get(url=url, jump=True), step.Msg("已审批")]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_turn_down(request):
    """驳回电子流"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        flow_id = request.GET["flow_id"]
        flow_node_id = request.GET["flow_node_id"]
        flow_data_id = request.GET["flow_data_id"]
        object_id = request.GET.get("id", None)
        app_label = request.GET.get("app_label", None)
        model_name = request.GET.get("model_name", None)
        widget_data = request.POST[const.SUBMIT_WIDGET]
        dict_data = json.loads(widget_data)
        opera_type = dict_data.get("return", models.NODE_TYPE_TURN_DOWN)  # 默认返回提交人

        with transaction.atomic():
            # 调用自定义接口
            node_id = dict_data.get("node_id", None)
            o_flow_data = workflow_service.update_flow_data(request, flow_data_id, flow_node_id, opera_type, object_id,
                                                            perv_node_id=node_id)

            o_flow_node = FlowNode.objects.get(pk=flow_node_id)
            if o_flow_node.submit_interface:
                o = parse.urlparse(o_flow_node.submit_interface, allow_fragments=True)
                lst_interface = o.path.split(".")
                o_module = importlib.import_module(".".join(lst_interface[0:-1]))
                fun = getattr(o_module, lst_interface[-1])
                result = fun(request, o_flow_data)
                if result:
                    try:
                        o_flow_data.pk = "error" * 50  # 手动抛异常，让批处理失败
                        o_flow_data.save()
                    except (BaseException,):
                        pass
                    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder),
                                        content_type="application/json")

        if app_label:
            model_admin = admin_api.get_model_admin(app_label, model_name)
            url = model_admin.get_change_list_url(request)
        else:
            url = common.make_url("/workflow_me_view/", request, param={const.UPN_MENU_ID: "url:/workflow_me_view/"})
        result = [step.Get(url=url, jump=True), step.Msg("已驳回")]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')


def workflow_comment(request):
    """增加评论"""
    try:
        result = admin_auth.check_opera_auth(request)
        if result:
            return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

        flow_id = request.GET["flow_id"]
        flow_node_id = request.GET["flow_node_id"]
        flow_data_id = request.GET["flow_data_id"]
        object_id = request.GET.get("id", None)
        app_label = request.GET.get("app_label", None)
        model_name = request.GET.get("model_name", None)

        with transaction.atomic():
            opera_type = models.NODE_TYPE_COMMENT
            workflow_service.update_flow_data(request, flow_data_id, flow_node_id, opera_type, object_id)

        if app_label:
            model_admin = admin_api.get_model_admin(app_label, model_name)
            url = model_admin.get_change_list_url(request)
        else:
            url = common.make_url("/workflow_me_view/", request, param={const.UPN_MENU_ID: "url:/workflow_me_view/"})

        result = [step.Get(url=url, jump=True), step.Msg("已提交")]
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type="application/json")

    except (BaseException,):
        result = admin_auth.save_error(request)
        return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')
