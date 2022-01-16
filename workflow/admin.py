# pylint: disable=C0111

import json
from django.contrib import admin
from django.forms.models import ModelForm
from vadmin import widgets
from vadmin import theme
from vadmin import step
from vadmin import event
from vadmin import common
from vadmin import const
from vadmin.admin import VModelAdmin
from workflow.models import Flow
from workflow.models import FlowNode
from workflow.models import FlowData
from workflow.models import FlowNodeData
from user.models import User


class FlowForm(ModelForm):
    v_widgets = {
        'interface_auth': widgets.Widget(width="80%"),
    }


@admin.register(Flow)
class FlowAdmin(VModelAdmin):
    """
    工作流
    """
    form = FlowForm
    list_display = ['id', 'name', 'user', 'desc', 'key', 'create_time', 'del_flag']
    list_display_links = ["id", "name"]
    exclude = ['user', 'create_time', 'update_time']
    fieldsets = (
        (None, {'fields': ('name', 'desc', 'key', 'del_flag',)}),
        # ("使用权限人", {'fields': ('department', 'role', 'default_user_form', 'interface_auth')}),
        ("结点画图数据", {'fields': ('flow_node',)}),
    )
    search_fields = ["name"]

    def flow_node(self, request, obj):
        height = 510
        if obj:
            value = obj.node_value
        else:
            value = None

        try:
            from user.models import User
            data = []
            for o_user in User.objects.filter(is_active=True)[0:20]:
                data.append([o_user.pk, str(o_user)])
        except (BaseException,):
            data = []

        search_field = ["name", "username", "phone"]
        o_draw = widgets.Draw(name="node_value", width="100%", height=height, value=value)
        data1 = [
            [["界面", widgets.Row(), widgets.Input(name="view_main", input_type="textarea", width="100%")]],

            [["抄送人", widgets.Row(), widgets.Select(name="cc_user", width="100%",
                                                   multiple=True).set_remote_method(foreign_key_app_label="user",
                                                                                    foreign_key_model_name="user",
                                                                                    search_field=search_field)]],
            [["抄送人（接口）", widgets.Row(), widgets.Input(name="cc_interface", width="100%")]],
            [["提交接口（新建）", widgets.Row(), widgets.Input(name="submit_interface", input_type="textarea", width="100%")]],
        ]

        data2 = [
            [["审批人", widgets.Row(), widgets.Select(name="approval_user", width="100%",
                                                   multiple=True).set_remote_method(foreign_key_app_label="user",
                                                                                    foreign_key_model_name="user",
                                                                                    search_field=search_field)]],
            [["审批人（接口）", widgets.Row(), widgets.Input(name="approval_interface", input_type="textarea", width="100%")]],
            [["抄送人", widgets.Row(), widgets.Select(name="cc_user", width="100%",
                                                   multiple=True).set_remote_method(foreign_key_app_label="user",
                                                                                    foreign_key_model_name="user",
                                                                                    search_field=search_field)]],
            [["抄送人（接口）", widgets.Row(), widgets.Input(name="cc_interface", width="100%")]],
            [["提交接口（审批）", widgets.Row(), widgets.Input(name="submit_interface", input_type="textarea", width="100%")]],
        ]

        o_round = widgets.Round(icon="v-round",
                                data=widgets.LiteTable(name="workflow_flow_round", data=data1, width="100%",
                                                       height=height - 20,
                                                       padding=10, min_row_height=80))
        o_rectangle = widgets.Rectangle(icon="v-rectangle",
                                        data=widgets.LiteTable(name="workflow_flow_rectangle", data=data2,
                                                               width="100%", height=height - 20,
                                                               padding=10, min_row_height=80))
        o_draw.set_attr_value("widget", [o_round, o_rectangle])
        # o_table = widgets.LiteTable(data=data, width="100%", height=height)
        # o_draw.set_attr_value("data", o_table)
        return o_draw

    def save_after(self, request, old_obj, obj, save_data, update_data,
                   m2m_data, dict_error, inline_data=None, change=True):
        flow_data = json.loads(save_data['node_value'])
        queryset = FlowNode.objects.filter(flow_id=obj.pk)
        queryset.update(del_flag=True)
        for i, node_data in enumerate(flow_data):
            if "id" not in node_data:  # 连接线
                continue

            node_id = node_data["id"]
            label = node_data.get("label", "")
            if not node_data["prev"]:
                type = "star"
            elif not node_data["next"]:
                type = "end"
            else:
                type = "process"

            dict_value = node_data.get('value', {}) or {}
            view_main = dict_value.get("view_main", None)
            view_print = dict_value.get("view_print", None)
            attachment_flag = dict_value.get("attachment_flag", False)
            image_flag = dict_value.get("image_flag", False)
            comment_flag = dict_value.get("comment_flag", True)
            go_back_flag = dict_value.get("go_back_flag", False)
            designated_approval = dict_value.get("designated_approval", False)
            designated_cc = dict_value.get("designated_cc", True)
            approval_interface = dict_value.get("approval_interface", None)
            approval_user = dict_value.get("approval_user", None)
            cc_interface = dict_value.get("cc_interface", None)
            cc_user = dict_value.get("cc_user", None)
            submit_interface = dict_value.get("submit_interface", None)
            next_node = node_data.get("next", None)
            prev_node = node_data.get("prev", None)

            o_flow_node = queryset.filter(pk=node_id).first()
            if o_flow_node:
                o_flow_node.label = label
                o_flow_node.type = type
                o_flow_node.sequence = i
                o_flow_node.view_main = view_main
                o_flow_node.view_print = view_print
                o_flow_node.attachment_flag = attachment_flag
                o_flow_node.image_flag = image_flag
                o_flow_node.comment_flag = comment_flag
                o_flow_node.go_back_flag = go_back_flag
                o_flow_node.designated_approval = designated_approval
                o_flow_node.designated_cc = designated_cc
                o_flow_node.approval_interface = approval_interface
                o_flow_node.approval_user = approval_user
                o_flow_node.cc_interface = cc_interface
                o_flow_node.cc_user = cc_user
                o_flow_node.submit_interface = submit_interface
                o_flow_node.next_node = next_node
                o_flow_node.prev_node = prev_node
                o_flow_node.del_flag = False
                o_flow_node.save()
            else:
                FlowNode.objects.create(pk=node_id, flow_id=obj.pk, label=label,
                                        type=type, sequence=i, view_main=view_main, view_print=view_print,
                                        attachment_flag=attachment_flag, image_flag=image_flag,
                                        comment_flag=comment_flag, go_back_flag=go_back_flag,
                                        designated_approval=designated_approval, designated_cc=designated_cc,
                                        approval_interface=approval_interface, approval_user=approval_user,
                                        cc_interface=cc_interface, cc_user=cc_user,
                                        submit_interface=submit_interface,
                                        next_node=next_node, prev_node=prev_node)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.user_id = request.user.id

        super(FlowAdmin, self).save_model(request, obj, form, change)


class FlowNodeForm(ModelForm):
    v_widgets = {
        'view_main': widgets.Widget(width=600),
        'view_print': widgets.Widget(width=600),
        'approval_interface': widgets.Widget(width=600),
        'approval_user': widgets.Widget(width=600),
        'cc_interface': widgets.Widget(width=600),
        'cc_user': widgets.Widget(width=600),
        'submit_interface': widgets.Widget(width=600),
        'next_node': widgets.Widget(width=600),
        'prev_node': widgets.Widget(width=600),
    }


@admin.register(FlowNode)
class FlowNodeAdmin(VModelAdmin):
    """
    工作流环节
    """
    form = FlowNodeForm
    list_display = ['id', 'flow', 'label', 'type', 'sequence', 'next_node', 'prev_node', 'del_flag']
    list_v_filter = ['flow', 'type', 'attachment_flag', 'image_flag', 'comment_flag', ]
    search_fields = ['name', 'create_time', 'update_time']
    exclude = ["order", ]

    fieldsets = (
        (None, {'fields': ('flow', 'label', 'del_flag', ('attachment_flag', 'image_flag'), ('comment_flag',))}),
        ("界面数据", {'fields': ('view_main', 'view_print',)}),
        ("审批数据", {'fields': ('approval_interface', 'approval_user', 'cc_interface', 'cc_user')}),
        ("流程数据", {'fields': ('submit_interface', 'next_node', 'prev_node')}),
    )

    def form_v_approval_user(self, request, obj):
        if obj and obj.approval_user:
            lst_user = []
            for user_id in obj.approval_user.split(","):
                lst_user.append(str(User.objects.get(pk=user_id)))

            return ",".join(lst_user)

    def form_v_default_cc(self, request, obj):
        if obj and obj.cc_user:
            lst_user = []
            for user_id in obj.cc_user.split(","):
                lst_user.append(str(User.objects.get(pk=user_id)))

            return ",".join(lst_user)

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        queryset = queryset.filter(del_flag=False)
        return queryset, use_distinct


@admin.register(FlowData)
class FlowDataAdmin(VModelAdmin):
    """
    工作流数据
    """

    list_display = ['user', 'flow', 'flow_node', 'flow_node_user', 'next_node', 'next_approval_user', 'begin_time',
                    'end_time', 'update_time', 'flow_state', 'model_name', 'object_id']
    list_filter = ['user', 'flow', 'flow_state']
    exclude = ['user_create']

    fieldsets = (
        (None, {'fields': ('user', 'flow', 'flow_state', 'begin_time', 'end_time')}),
        ("操作节点", {'fields': ('flow_node', 'flow_node_user', 'next_node', 'next_approval_user')}),
        ("节点数据", {'fields': ('app_label', 'model_name', 'object_id')}),
    )

    change_list_config = {"col_width": {"flow_state": 80, "model_name": 100}}

    def get_change_form_custom(self, request, obj=None):
        if obj:
            url = common.make_url("/admin/#workflow_approval_view/",
                                  param={"flow_id": obj.flow_id, "flow_data_id": obj.pk,
                                         const.UPN_MENU_ID: "url:/workflow_me_view/"})
            return widgets.Button(text="预览", step=step.Get(href=url, new_window=True, unique=True))


@admin.register(FlowNodeData)
class FlowNodeDataAdmin(VModelAdmin):
    """
    工作流环节数据
    """

    list_display = ['user', 'flow', 'flow_node', 'comments', 'create_time']
    list_filter = ['user', 'flow', 'flow_node']

    fieldsets = (
        (None, {'fields': ('user', 'flow', 'flow_data', 'flow_node', 'next_node', 'node_type')}),
        # ("操作节点", {'fields': ('flow_node', 'opera_node', 'next_node', 'next_approval_user')}),
        ("节点数据", {'fields': ('attachments', 'images', 'comments')}),
    )
