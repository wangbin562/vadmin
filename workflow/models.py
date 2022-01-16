#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
工作流model
"""
import collections
from django.db import models
from user.models import User
# from user.models import Department
# from user.models import Role
from vadmin.models import VModel
from vadmin import admin_fields

NODE_TYPE_SAVE = 1  # 待提交 / 保存
NODE_TYPE_SUBMIT = 2  # 已提交 / 审批中
NODE_TYPE_APPROVAL = 3  # 审批通过
NODE_TYPE_TURN_DOWN = 4  # 已驳回
NODE_TYPE_CANCEL = 5  # 已撤销
NODE_TYPE_COMMENT = 6  # 添加评论
NODE_TYPE_RESUBMIT = 7  # 重新提交申请
NODE_TYPE_TURN_DOWN_PREV = 8  # 驳回（上一步）

FLOW_STATE = collections.OrderedDict((
    (NODE_TYPE_SAVE, "待提交"), (NODE_TYPE_SUBMIT, "审批中"),
    (NODE_TYPE_APPROVAL, "审批通过"), (NODE_TYPE_TURN_DOWN, "已驳回"),
    (NODE_TYPE_CANCEL, "已撤销")
))

FLOW_NODE_TYPE = collections.OrderedDict((
    (NODE_TYPE_SAVE, "保存"), (NODE_TYPE_SUBMIT, "提交申请"),
    (NODE_TYPE_APPROVAL, "已同意"), (NODE_TYPE_TURN_DOWN, "驳回"),
    (NODE_TYPE_CANCEL, "已撤销"), (NODE_TYPE_COMMENT, "添加评论"),
    (NODE_TYPE_RESUBMIT, "重新提交申请"), (NODE_TYPE_TURN_DOWN_PREV, "驳回到上一步")
))


class Flow(VModel):
    """
    工作流
    """
    user = admin_fields.ForeignKey(User, verbose_name=u'创建人')
    name = models.CharField(max_length=64, verbose_name=u'名称')
    desc = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"说明")
    key = models.CharField(max_length=64, blank=True, null=True, verbose_name=u"关键字")

    # department = admin_fields.ForeignKey(Department, blank=True, null=True, verbose_name=u'默认使用部门')
    # role = admin_fields.ForeignKey(Role, blank=True, null=True, verbose_name=u'默认使用角色')
    # default_user = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'默认使用人')
    interface_auth = models.CharField(max_length=256, blank=True, null=True, verbose_name="权限接口",
                                      help_text="由接口判断是否有使用权限")
    # node_xml = models.TextField(verbose_name="结点xml数据")
    node_value = models.TextField(verbose_name="节点数据", blank=True, null=True, help_text="回显查看使用")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta:
        db_table = "t_flow"
        ordering = ["order", 'create_time']
        verbose_name_plural = verbose_name = u"工作流"

    def __str__(self):
        return self.name


class FlowNode(VModel):
    """
    工作流环节
    """
    id = admin_fields.UuidField(max_length=32, verbose_name="节点ID")
    flow = admin_fields.ForeignKey(Flow, verbose_name=u'流程')
    label = models.CharField(max_length=64, blank=True, null=True, verbose_name=u'环节名称',
                             help_text=u'在审批上显示的名称')
    type = models.CharField(max_length=16, db_index=True, default="star",
                            choices=(("star", "开始"), ("process", "过程"), ("end", "结束")),
                            verbose_name="结点类型")
    key = models.CharField(verbose_name=u"结点关键字", max_length=64, blank=True, null=True, db_index=True)
    sequence = models.IntegerField(verbose_name="节点序列", blank=True, null=True, db_index=True,
                                   help_text="分支循序相同")
    # 界面
    view_main = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"主界面",
                                 help_text="自定义界面，开始结点可以配置")

    view_print = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"打印界面")

    # interface_init_phone = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"初始化界面（手机端）",
    #                                         help_text="为空时同PC")
    # interface_init_admin = models.CharField(max_length=256, blank=True, null=True,
    #                                         verbose_name="初始化界面（使用admin)")
    # interface_print = models.CharField(max_length=256, blank=True, null=True, verbose_name="打印接口")

    # interface_config_pc = admin_fields.FileField(upload_to="file/interface_config/%Y-%m-%d/", blank=True, null=True,
    #                                               verbose_name='PC版界面配置文件',
    #                                               help_text='为空时同手机版界面配置文件')
    # interface_config_phone = admin_fields.FileField(upload_to="file/interface_config/%Y-%m-%d/", blank=True, null=True,
    #                                                  verbose_name='Phone版界面配置文件',
    #                                                  help_text='为空时同PC版界面配置文件')

    # 配置
    attachment_flag = models.BooleanField(default=True, verbose_name="允许上传附件")
    image_flag = models.BooleanField(verbose_name="允许上传图片", default=True)
    comment_flag = models.BooleanField(verbose_name="允许输入评论", default=True)
    go_back_flag = models.BooleanField(verbose_name="允许返回上一步", default=False, help_text="默认返回提交人")
    # go_back_interface = models.CharField(max_length=256, blank=True, null=True, verbose_name="返回接口")
    designated_approval = models.BooleanField(verbose_name="允许指定审批人", default=False)
    designated_cc = models.BooleanField(verbose_name="允许指定抄送人", default=True)
    # cc_notification = models.IntegerField(blank=True, null=True,
    #                                       choices=((1, "提交申请时抄送"), (2, "审批通过后抄送"),
    #                                                (3, "提交申请时和审批通过后都抄送")),
    #                                       verbose_name="抄送通知")
    # select_approval = models.BooleanField(default=False, verbose_name="可以选择审批人")

    # 审批
    # department = admin_fields.ForeignKey(Department, blank=True, null=True, verbose_name=u'默认审批部门',
    #                                      help_text="如果没有配置部门，但配置了角色，默认用提交人同一部门此角色人审批")
    # role = admin_fields.ForeignKey(Role, blank=True, null=True, verbose_name=u'默认审批角色')

    # 审批
    approval_interface = models.CharField(max_length=256, blank=True, null=True, verbose_name="审批人接口",
                                          help_text="由接口返回审批人")
    approval_user = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'默认审批人',
                                     help_text='多个用","分割。指定审批后，配置的部门和角色不生效。')

    # 抄送
    cc_interface = models.CharField(max_length=256, blank=True, null=True, verbose_name="抄送人接口",
                                    help_text="由接口返回抄送人")
    cc_user = models.CharField(max_length=512, blank=True, null=True, verbose_name=u'默认抄送人',
                               help_text='多个用","分割。指定审批后，配置的部门和角色不生效。')

    # default_cc = models.CharField(max_length=512, blank=True, null=True, verbose_name="默认抄送人")
    # select_approval = models.BooleanField(default=False, verbose_name="可以选择审批人")

    # interface_opera = models.CharField(max_length=256, blank=True, null=True, verbose_name="操作区域界面接口")
    submit_interface = models.CharField(max_length=256, blank=True, null=True, verbose_name=u"提交调用接口")

    next_node = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"下一环节",
                                 help_text=u'多个用","分割，如果有多个时，在上一环节提交时，要选择提交的结点')
    prev_node = models.CharField(max_length=128, blank=True, null=True, verbose_name=u"上一环节",
                                 help_text=u'多个用","分割，如果有多个时，在下一环节返回时，要选择提交的结点')

    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')
    del_flag = models.BooleanField(default=False, verbose_name=u'是否删除')
    order = models.IntegerField(db_index=True, default=2147483647, verbose_name=u'排序')

    class Meta:
        db_table = "t_flow_node"
        verbose_name_plural = verbose_name = u"工作流环节"
        ordering = ["order", "create_time"]

    def __str__(self):
        if self.label:
            return self.label

        return self.id


class FlowData(VModel):
    """
    工作流数据
    """
    user = admin_fields.ForeignKey(User, verbose_name=u'提交人', help_text="关联审核")
    user_create = admin_fields.ForeignKey(User, verbose_name=u'创建人', blank=True, null=True,
                                          related_name="user_create")
    flow = admin_fields.ForeignKey(Flow, verbose_name=u'流程')
    begin_time = models.DateTimeField(auto_now_add=True, verbose_name=u'创建时间')
    end_time = models.DateTimeField(blank=True, null=True, verbose_name=u"结束时间")
    desc = models.TextField(verbose_name="说明", blank=True, null=True)
    flow_state = models.IntegerField(default=1, choices=FLOW_STATE.items(), verbose_name="流程状态")

    flow_node = admin_fields.ForeignKey(FlowNode, blank=True, null=True, verbose_name=u"当前环节",
                                        help_text="已经操作的环节")
    flow_node_user = admin_fields.ForeignKey(verbose_name="当前环节审批人", to=User,
                                             blank=True, null=True, related_name="flow_node_user",
                                             help_text="如果有多个人, 提交时要选择具体审批人")
    # opera_node = admin_fields.ForeignKey(FlowNode, blank=True, null=True, verbose_name="操作环节",
    #                                      related_name="flow_data_opera_node")

    # 下一个操作环节结点(只能有一个，如果有多个，在提交的时候必须选择）
    next_node = admin_fields.ForeignKey(FlowNode, blank=True, null=True, verbose_name=u"下一环节",
                                        related_name="flow_data_next_node")
    next_approval_user = admin_fields.ForeignKey(verbose_name="下一环节审批人", to=User,
                                                 blank=True, null=True, related_name="next_approval_user",
                                                 help_text="如果有多个人, 提交时要选择具体审批人")
    app_label = models.CharField(max_length=128, blank=True, null=True, verbose_name="app名称")
    model_name = models.CharField(max_length=128, blank=True, null=True, verbose_name="model名称")
    object_id = models.CharField(max_length=32, db_index=True, blank=True, null=True, verbose_name="model对象ID")
    attr = models.TextField(verbose_name="单个审批属性数据", blank=True, null=True,
                            help_text="自定义界面保存的数据")
    update_time = models.DateTimeField(auto_now=True, verbose_name=u'修改时间')

    class Meta:
        db_table = "t_flow_data"
        verbose_name_plural = verbose_name = u"工作流数据"
        ordering = ("-begin_time",)

    def __str__(self):
        return ""


class FlowNodeData(VModel):
    """
    工作流环节数据
    """
    user = admin_fields.ForeignKey(User, verbose_name=u'提交人')
    flow = admin_fields.ForeignKey(Flow, verbose_name=u'工作流')
    flow_data = admin_fields.ForeignKey(FlowData, search_field=["id", "name"], verbose_name=u'工作流数据')
    flow_node = admin_fields.ForeignKey(FlowNode, search_field=["id", "name"], verbose_name=u'操作环节',
                                        related_name="flow_node")
    next_node = admin_fields.ForeignKey(FlowNode, blank=True, null=True, verbose_name=u"下一环节",
                                        related_name="flow_node_data_next_node")
    data = models.TextField(blank=True, null=True, verbose_name='填写数据',
                            help_text='不包含图例样式，图例样式使用配置表格中样式')
    attachments = admin_fields.FileField(multiple=True, blank=True, null=True, verbose_name="上传的附件")
    images = admin_fields.ImageField(multiple=True, blank=True, null=True, verbose_name="上传的图片")
    comments = models.CharField(max_length=256, blank=True, null=True, verbose_name="评论")
    node_type = models.IntegerField(choices=FLOW_NODE_TYPE.items(), verbose_name="状态")
    state_desc = models.CharField(max_length=32, blank=True, null=True, verbose_name="状态说明",
                                  help_text="给自定义显示使用")
    create_time = models.DateTimeField(auto_now_add=True, verbose_name=u'修改时间')

    class Meta:
        db_table = "t_flow_node_data"
        verbose_name_plural = verbose_name = u"工作流环节数据"

    def __str__(self):
        return ""
