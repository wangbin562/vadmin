# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
widget service
"""
import os
import json
from vadmin import step
from vadmin import const
from vadmin import widgets
# from vadmin import api
from vadmin import admin_api


# def file_upload_before(request):
#     """上传文件开始前"""
#     content = request.POST.get(const.SUBMIT_WIDGET, "{}")
#     widget_data = json.loads(content)
#     k = v = None
#     for k, v in widget_data.items():
#         break
#
#     if k is None:
#         return
#
#     lst_path = []
#     if v.find("[") == 0:
#         lst_path = eval(v)
#     else:
#         lst_path.append(v)
#
#     name = k
#     icon = widgets.Icon(icon="el-icon-document", font_size=16)
#     o_step_delete = step.WidgetOpera(name=name, opera=const.O_TABLE_ROW_DEL, data={})
#     icon_delete = widgets.Icon(icon="el-icon-delete", font_size=16, step=o_step_delete)
#     lst_step = []
#     for path in lst_path:
#         file_name = os.path.split(path)[1]
#         size = api.format_file_size(os.path.getsize(path))
#         time = admin_api.format_date(os.path.getmtime(path))
#
#         row_id = -1
#         icon_delete.step.data["row_id"] = row_id
#         row_data = [(icon, file_name), (time, widgets.Row(), size), icon_delete.render()]
#         data = {
#             "row_id": row_id,
#             "row_data": row_data
#         }
#         o_step = step.WidgetOpera(name=name, opera=const.O_TABLE_ROW_ADD, data=data)
#         lst_step.append(o_step)
#
#     return lst_step
#
#
# def file_upload_after(request):
#     """上传文件成功后"""
#     content = request.POST.get(const.SUBMIT_WIDGET, "{}")
#     widget_data = json.loads(content)
#     k = v = None
#     for k, v in widget_data.items():
#         break
#
#     if k is None:
#         return
#
#     lst_path = []
#     if v.find("[") == 0:
#         lst_path = eval(v)
#     else:
#         lst_path.append(v)
#
#     name = k
#     icon = widgets.Icon(icon="el-icon-document", font_size=16)
#     o_step_delete = step.WidgetOpera(name=name, opera=const.O_TABLE_ROW_DEL, data={})
#     icon_delete = widgets.Icon(icon="el-icon-delete", font_size=16, step=o_step_delete)
#     lst_step = []
#     for path in lst_path:
#         file_name = os.path.split(path)[1]
#         size = api.format_file_size(os.path.getsize(path))
#         time = admin_api.format_date(os.path.getmtime(path))
#
#         row_id = -1
#         icon_delete.step.data["row_id"] = row_id
#         row_data = [(icon, file_name), (time, widgets.Row(), size), icon_delete.render()]
#         data = {
#             "row_id": row_id,
#             "row_data": row_data
#         }
#         o_step = step.WidgetOpera(name=name, opera=const.O_TABLE_ROW_ADD, data=data)
#         lst_step.append(o_step)
#
#     return lst_step


def form_field_show(request, field_name, index=1):
    """form字段显示（包括标题，后面提示图标等）,index:父类节点的基本（前端使用）"""
    script = "{{js.var node1 = getParentNode('%s', %s); var node2 = getBeforeNode(node1); showNode([node1, node2])}}" % \
             (field_name, index)
    return step.RunJs(script)


def form_field_hide(request, field_name, index=1):
    script = "{{js.var node1 = getParentNode('%s', %s); var node2 = getBeforeNode(node1); hideNode([node1, node2])}}" % \
             (field_name, index)
    return step.RunJs(script)
