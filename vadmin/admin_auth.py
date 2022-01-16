# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
auth
"""
import logging
import re
import traceback
from django.conf import settings

from vadmin import admin_api
from vadmin import common
from vadmin import const
from vadmin import step

logger = logging.getLogger(__name__)


def check_login(request):
    """
    检查登录
    """
    lst_step = []
    if not request.user.is_authenticated:
        lst_step = [step.Msg(text="未登录或登录超时，请重新登录！")]
        if settings.V_LOGGED_JUMP:
            o_re = re.search("<WSGIRequest: .*'(.*)'>", str(request))
            if o_re:
                redirect_url = o_re[1]
                base = "/" + settings.V_URL_BASE
                if redirect_url.find(base) > -1:
                    redirect_url = redirect_url.replace(base, "")
            else:
                redirect_url = ""
            url = common.make_url(const.URL_INDEX_VIEW, param={const.UPN_REDIRECT_URL: redirect_url})
            lst_step.append(step.Get(url=url, jump=True))
    return lst_step


def check_opera_auth(request, app_label=None, model_name=None, is_edit=False, is_add=False, is_del=False, obj=None,
                     is_custom=False, is_auth=False):
    """
    检查操作权限
    :param request:
    :param app_label:应用名称
    :param model_name:模块名称
    :param is_edit:是否编辑
    :param is_add:是否增加
    :param is_del:是否删除
    :param obj:对象
    :param is_custom:是否为自定义
    :param is_auth:是否检查权限
    :return:提示信息
    """
    # if settings.V_CHECK_OPERA_AUTH_CALLBACK:
    #     dict_resp = settings.V_CHECK_OPERA_AUTH_CALLBACK(request)
    #     if dict_resp:
    #         return dict_resp

    o_step = check_login(request)
    if o_step:
        return o_step

    if not is_auth:
        return []

    if request.user.is_superuser:
        return []

    if (app_label is None) or (model_name is None):
        return []

    if is_custom:
        lst_permissions = request.user.get_all_permissions()
        # codename = "vadmin.view_%s" % model_name.lower()
        if lst_permissions:
            return []
        else:
            return step.Msg(text="无权查看。 ", msg_type="error").render()

    model_admin = admin_api.get_model_admin(app_label, model_name)
    if model_admin is None:  # 有可能没有注册，只用在inlines中
        return o_step

    change = model_admin.has_change_permission(request, obj)
    add = model_admin.has_add_permission(request)
    delete = model_admin.has_delete_permission(request, obj)
    try:
        view = model_admin.has_module_permission(request)
    except (BaseException,):
        view = False

    if (not change) and (not add) and (not delete) and (not view):
        return step.Msg(text="无权查看。 ", msg_type="error").render()

    if is_edit:
        if not change:
            return step.Msg(text="无权修改。 ", msg_type="error").render()

    if is_add:
        if not add:
            return step.Msg(text="无权增加。 ", msg_type="error").render()

    if is_del:
        if not delete:
            return step.Msg(text="无权删除。 ", msg_type="error").render()

    return None


def save_error(request):
    s_err_info = traceback.format_exc()
    logger.error("request:%s" % request)
    logger.error(s_err_info)
    if settings.V_POPUP_ERROR:
        result = [step.Msg(text=s_err_info, msg_type="error"), step.ExitStep()]
    else:
        result = [step.Msg(text="数据异常，请检查日志！", msg_type="error"), step.ExitStep()]
    return result
