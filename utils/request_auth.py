# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
登录鉴权
"""
from utils.error_code import *

# 是否检查登录
IS_CHECK_LOGIN = True


def auth_check(request, method="POST", lst_module=None, b_check_login=True):
    """
    检查用户是否登录
    :param request:
    :param method:
    :param lst_module:
    :param b_check_login:
    :return:
    """
    dict_resp = {}
    if not IS_CHECK_LOGIN:
        return dict_resp

    if b_check_login:
        if not request.user.is_authenticated:
            dict_resp = {'c': ERR_USER_NOT_LOGIN[0], 'm': ERR_USER_NOT_LOGIN[1]}
            return dict_resp

    lst_module = lst_module
    # if request.user.username == 'admin':
    #    return dictResp

    # if lst_module:
    #     for iModule in lstModule:
    #         if "%s," % iModule in request.user.first_name:
    #             #dictResp = {'c': CON_CODE_USER_AUTH_ERR}
    #             return dictResp
    #     else:
    #         dictResp = {'c': ERR_USER_AUTH[0], 'e':ERR_USER_AUTH[1]}
    #
    if request.method != method.upper():
        dict_resp = {'c': ERR_REQUESTWAY[0], 'm': ERR_REQUESTWAY[1]}

    return dict_resp


def jwt_auth_check(request):
    """
    检查微信用户是否登录
    :param request:
    :return:
    """
    dict_resp = {}
    if not request.jwt_user:
        dict_resp = {'c': ERR_USER_NOT_LOGIN[0], 'm': ERR_USER_NOT_LOGIN[1]}
        return dict_resp

    return dict_resp
