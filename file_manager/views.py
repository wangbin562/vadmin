# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
1、电子流的主界面自定义，在流程节点中配置
2、附件的自定义在make_workflow_attachment函数，如果效果要求不一样，可以修改此函数
3、流程时间轴定义在make_workflow_timeline函数，如果效果要求不一样，可以修改此函数
4、整个流程流转界面在workflow_approval_view函数
5、流程审批人可以指定具体责任人（default_approval字段）和角色（role字段），
   例如：在提定审批角色时，提交人是研发部，提定的审指角色是经理，那么研发经理就有审批权
"""

import json
import traceback
import logging
from django.http import HttpResponse
from vadmin import step
from vadmin.json_encoder import Encoder
from file_manager import service

logger = logging.getLogger(__name__)


def file_manager_opera(request, opera_key):
    dict_fun = {
        "add_dir": service.add_dir,
        "update": service.update,
        "upload_file": service.upload_file,
        "search": service.search,
        "download": service.download,
        "delete": service.delete,
        # "preview": service.preview,
    }
    try:
        o_step = dict_fun[opera_key](request)
        result = {"step": o_step}

    except (BaseException,):
        s_err_info = traceback.format_exc()
        logger.error(s_err_info)
        o_step = step.Msg(text=s_err_info)
        result = {"step": o_step}

    return HttpResponse(json.dumps(result, ensure_ascii=False, cls=Encoder), content_type='application/json')
