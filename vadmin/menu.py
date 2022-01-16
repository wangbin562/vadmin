# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
menu
"""
import collections
import copy
import json

from django.apps import apps as django_apps
from django.conf import settings
from django.contrib.auth.models import Permission, Group
from django.contrib.contenttypes.models import ContentType

from vadmin import admin_api
from vadmin import const
from vadmin import step
from vadmin import common
from vadmin import widgets
from vadmin.models import GroupEx
from vadmin.models import PermissionEx

MENU_ID = collections.OrderedDict()


def make_left_menu_list(request, menu_item, menu_data, is_close=False):
    """
    构造左边菜单数据，给menu组件直接使用
    """
    for dict_item in menu_item:
        dict_menu = parse_menu_item_param(dict_item)

        if "children" in dict_item:
            dict_menu["children"] = []
            make_left_menu_list(request, dict_item["children"], dict_menu["children"], is_close)
        else:
            menu_id = get_menu_id(dict_item)
            # o_step, value = make_single_menu(request, dict_item, is_close)
            lst_step = []
            if is_close:
                lst_step.append(step.LayerClose())

            url = common.make_url(const.URL_HOME,
                                  param={const.UPN_MENU_ID: menu_id, const.UPN_SCREEN_WIDTH: "{{window.innerWidth}}"})
            lst_step.append(step.Post(url=url, jump=True, submit_type="hide"))
            dict_menu["step"] = lst_step
            dict_menu["id"] = menu_id

        menu_data.append(dict_menu)


def parse_menu_item_param(dict_item):
    dict_menu = dict()
    dict_menu["label"] = dict_item.get("label", "")
    if "id" in dict_item:
        dict_menu["id"] = dict_item["id"]

    if "select" in dict_item:
        dict_menu["select"] = dict_item["select"]

    if "icon" in dict_item:
        if isinstance(dict_item["icon"], str):
            dict_menu["icon"] = widgets.Icon(icon=dict_item["icon"]).render()
        else:
            dict_menu["icon"] = dict_item["icon"]

    if "expand" in dict_item:
        dict_menu["expand"] = dict_item["expand"]

    return dict_menu


def get_top_left_id(request, menu_id=None):
    top_id = None
    left_id = None

    if MENU_ID:
        if menu_id:
            top_id = MENU_ID.get(menu_id.lower(), None) or MENU_ID.get("%s/" % menu_id.lower(), None)
            menu_mode = request.GET.get(const.UPN_MENU_MODE, None)
            if menu_mode:
                left_id = menu_id + "&%s=%s" % (const.UPN_MENU_MODE, menu_mode)
                top_id = MENU_ID.get(left_id.lower(), None) or MENU_ID.get("%s/" % left_id.lower(), None)
            else:
                left_id = menu_id
        else:
            top_id, left_id = list(MENU_ID.items())[0]

    return top_id, left_id


def get_menu_id(dict_item, idx=0):
    return dict_item["id"]


def get_first_top_left_id(dict_item):
    """
    根据第一级菜单获取第一个可选择的子菜单ID
    :param dict_item:
    :return:
    """
    top_id = get_menu_id(dict_item)
    if "children" in dict_item:
        tmp_id, left_id = get_first_top_left_id(dict_item["children"][0])
    else:
        left_id = top_id

    return top_id, left_id


def get_url_by_menu_id(menu_id):
    url = href = None
    if not menu_id:
        return url, href

    mode, param = menu_id.split(":", 1)
    if mode == "url":
        url = param

    elif mode == "href":
        href = param

    elif mode == "model":
        app_label, model_name = param.split(".")
        model_name = model_name.split("/")[0]
        model_name = model_name.split("&")[0]
        url = const.URL_LIST % (app_label, model_name)

    elif mode == "id":
        url, href = get_url_by_id(settings.V_MENU_ITEMS, param)

    return url, href


def get_url_by_id(lst_menu, menu_id):
    for dict_item in lst_menu:
        if dict_item.get("id", None) == menu_id:
            url = href = None
            if "url" in dict_item:
                url = dict_item["url"]
            elif "href" in dict_item:
                href = dict_item["href"]
            elif "model" in dict_item:
                app_label, model_name = dict_item["model"].split(".")
                model_name = model_name.split("/")[0]
                url = const.URL_LIST % (app_label, model_name)
            return url, href

        elif "children" in dict_item:
            url, href = get_url_by_id(dict_item["children"], menu_id)
            if url or href:
                return url, href

    return None, None


def get_mode_param_by_id(lst_menu, menu_id):
    for dict_item in lst_menu:
        if dict_item.get("id", None) == menu_id or dict_item.get('id', None) == "id:%s" % menu_id:
            if "url" in dict_item:
                return "url", dict_item["url"]
            elif "href" in dict_item:
                return "href", dict_item["href"]
            elif "model" in dict_item:
                return "model", dict_item["model"]

        elif "children" in dict_item:
            mode, param = get_mode_param_by_id(dict_item["children"], menu_id)
            if param:
                return mode, param

    return None, None


def get_label(menu_id):
    def _get_label(lst_item):
        for item in lst_item:
            item_id = get_menu_id(item)
            if item_id == menu_id:
                return item.get("label", "")

            if "children" in item:
                label = _get_label(item["children"])
                if label is not None:
                    return label

        return None

    return _get_label(settings.V_MENU_ITEMS)


def get_menu(request):
    """
    获取获取菜单（对应用户权限）
    """
    return MenuAuthManage(request).get_menu()


def create_auth_group(name, key, lst_permission):
    """
    创建权限组
    """
    o_group_ex = GroupEx.objects.filter(key=key, del_flag=False).first()
    if not o_group_ex:
        o_group_ex = GroupEx.objects.create(name=name, key=key)

    o_group = Group.objects.filter(pk=o_group_ex.group_id).first()
    if not o_group:
        o_group = Group.objects.create(name=name)
        o_group.name = o_group_ex.name
        o_group_ex.group_id = o_group.pk

    o_group.permissions.set(lst_permission)
    o_group_ex.tree_value = json.dumps(lst_permission, ensure_ascii=False)
    o_group_ex.save()


class MenuAuthManage(object):
    """
    菜单管理
    """
    CON_BASE_MENU = "BASE_MENU"

    def __init__(self, request=None, is_all=False):
        self.request = request
        self.is_all = is_all
        self.item_count = 0

    def init_menu_id(self, menu_items=settings.V_MENU_ITEMS):
        self.item_count = 0

        def deep(lst_menu, parent_id):
            for dict_item_sub in lst_menu:
                self.item_count += 1
                if "children" in dict_item_sub:
                    if "id" in dict_item_sub:
                        sub_menu_id = "id:%s" % dict_item_sub["id"]
                    else:
                        sub_menu_id = "id:menu-%s" % self.item_count
                    deep(dict_item_sub["children"], parent_id)

                elif "id" in dict_item_sub:
                    sub_menu_id = dict_item_sub["id"]

                elif "href" in dict_item_sub:
                    sub_menu_id = "href:%s" % dict_item_sub["href"]

                elif "url" in dict_item_sub:
                    sub_menu_id = "url:%s" % dict_item_sub["url"]

                elif "model" in dict_item_sub:
                    sub_menu_id = "model:%s" % dict_item_sub["model"]
                else:
                    sub_menu_id = "id:menu-%s" % self.item_count

                sub_menu_id = sub_menu_id.lower()
                dict_item_sub["id"] = sub_menu_id
                MENU_ID[sub_menu_id] = parent_id

        for dict_item in menu_items:
            self.item_count += 1

            if "id" in dict_item:
                menu_id = dict_item["id"]
            elif "href" in dict_item:
                menu_id = "href:%s" % dict_item["href"]
            elif "url" in dict_item:
                menu_id = "url:%s" % dict_item["url"]
            elif "model" in dict_item:
                menu_id = "model:%s" % dict_item["model"]
            else:
                menu_id = "id:menu-%s" % self.item_count

            menu_id = menu_id.lower()
            dict_item["id"] = menu_id
            MENU_ID[menu_id] = menu_id

            if "children" in dict_item:
                deep(dict_item["children"], menu_id)

    def init_menu_permission(self):
        """
        初始化菜单权限(全量)
        :return:
        """
        self.init_menu_id()
        o_group_ex = GroupEx.objects.filter(key=self.CON_BASE_MENU).first()
        if o_group_ex:
            menu = json.dumps(settings.V_MENU_ITEMS, ensure_ascii=False).lower()
            if menu == o_group_ex.menu:
                return o_group_ex
            else:
                # o_group_ex.menu_data = None
                # o_group_ex.menu = None
                # o_group_ex.save()
                GroupEx.objects.all().update(menu_data=None, menu=None)

        else:
            o_group_ex = GroupEx.objects.create(key=self.CON_BASE_MENU, del_flag=True)

        self.create_menu_permission(settings.V_MENU_ITEMS)

        models = self.get_models()
        no_menu_model = copy.copy(models)
        self.is_all = True
        lst_menu = self.get_menu_data(no_menu_model=no_menu_model)
        tree_data = []
        self.menu_2_tree(lst_menu, tree_data)

        other_data = []
        lst_permission_ex = PermissionEx.objects.all()
        for model, label in models.items():
            app_label, model_name = model.split(".")

            o_content_type = ContentType.objects.filter(app_label=app_label, model=model_name).first()
            if o_content_type is None:
                o_content_type = ContentType.objects.create(app_label=app_label, model=model_name)

            for o_permission_ex in lst_permission_ex:
                name = "%s %s(%s)" % (o_permission_ex.name, label, model)
                codename = "%s_%s" % (o_permission_ex.codename, model_name)
                o_permission = Permission.objects.filter(content_type_id=o_content_type.pk, codename=codename).first()
                if o_permission is None:
                    o_permission = Permission.objects.create(name=name, content_type_id=o_content_type.pk,
                                                             codename=codename)

                other_data.append([o_permission.pk, name])

        # 权限配置树结构
        o_group_ex.tree_data = json.dumps(tree_data, ensure_ascii=False)

        # 界面菜单数据结构（每个用户不一致）
        o_group_ex.menu_data = json.dumps(lst_menu, ensure_ascii=False)

        # o_group_ex.menu = json.dumps(settings.V_MENU_ITEMS, ensure_ascii=False).lower()
        o_group_ex.other_data = json.dumps(other_data, ensure_ascii=False)
        o_group_ex.save()
        return o_group_ex

    def update_menu_permission(self):
        """
        修改菜单基础权限
        """
        models = self.get_models()
        no_menu_model = copy.copy(models)
        self.is_all = True
        lst_menu = self.get_menu_data(no_menu_model=no_menu_model)
        tree_data = []
        self.menu_2_tree(lst_menu, tree_data)

        other_data = []
        lst_permission_ex = PermissionEx.objects.all()
        for model, label in models.items():
            app_label, model_name = model.split(".")

            o_content_type = ContentType.objects.filter(app_label=app_label, model=model_name).first()
            if o_content_type is None:
                o_content_type = ContentType.objects.create(app_label=app_label, model=model_name)

            for o_permission_ex in lst_permission_ex:
                name = "%s %s(%s)" % (o_permission_ex.name, label, model)
                codename = "%s_%s" % (o_permission_ex.codename, model_name)
                o_permission = Permission.objects.filter(content_type_id=o_content_type.pk, codename=codename).first()
                if o_permission is None:
                    o_permission = Permission.objects.create(name=name, content_type_id=o_content_type.pk,
                                                             codename=codename)

                other_data.append([o_permission.pk, name])

        o_group_ex = GroupEx.objects.filter(key=self.CON_BASE_MENU).first()
        if o_group_ex:
            o_group_ex.tree_data = json.dumps(tree_data, ensure_ascii=False)
            o_group_ex.menu_data = json.dumps(lst_menu, ensure_ascii=False)
            o_group_ex.menu = json.dumps(settings.V_MENU_ITEMS, ensure_ascii=False).lower()
            o_group_ex.other_data = json.dumps(other_data, ensure_ascii=False)
            o_group_ex.save()

        else:

            o_group_ex = GroupEx.objects.create(key=self.CON_BASE_MENU,
                                                tree_data=json.dumps(tree_data, ensure_ascii=False),
                                                menu_data=json.dumps(lst_menu, ensure_ascii=False),
                                                menu=json.dumps(settings.V_MENU_ITEMS, ensure_ascii=False).lower(),
                                                other_data=json.dumps(other_data, ensure_ascii=False))
        return o_group_ex

    def create_menu_permission(self, menu_item):
        """
        创建菜单中的model和url、href权限
        :return:
        """
        for dict_item in menu_item:
            if "children" in dict_item:
                self.create_menu_permission(dict_item["children"])
            else:
                if "href" in dict_item:
                    model_name = dict_item["href"].lower()
                    label = dict_item.get("label", model_name)
                    self.create_permission("vadmin", model_name, label, is_sub=False)

                elif "url" in dict_item:
                    model_name = dict_item["url"].lower()
                    label = dict_item.get("label", model_name)
                    self.create_permission("vadmin", model_name, label, is_sub=False)

                elif "model" in dict_item:
                    app_label, model_name = dict_item["model"].lower().split(".")
                    if "label" in dict_item:
                        label = dict_item["label"]
                    else:
                        label = admin_api.get_verbose_name(app_label, model_name)

                    self.create_permission(app_label, model_name, label)

    def has_menu_permission(self, dict_permission, app_model_name):
        """
        检查菜单权限
        :return:
        """
        if self.is_all:
            if app_model_name in dict_permission:
                return True

        if self.request and self.request.user.is_superuser:
            if app_model_name in dict_permission:
                return True

        return bool(dict_permission.get(app_model_name, False))

    def get_menu_permission(self, app_label, model_name, is_sub=True):
        """
        获取菜单下面的权限，菜单只显示一级，但model有增、删、改、查等子权限
        :param app_label:
        :param model_name:
        :param is_sub:
        :return:
        """
        dict_permission = collections.OrderedDict()
        o_content_type = ContentType.objects.filter(app_label=app_label, model=model_name).first()
        if o_content_type is None:
            return dict_permission

        if is_sub:
            for o_permission_ex in PermissionEx.objects.all():
                codename = "%s_%s" % (o_permission_ex.codename, model_name)
                o_permission = Permission.objects.filter(content_type_id=o_content_type.pk, codename=codename).first()
                if o_permission:
                    dict_permission[o_permission.pk] = o_permission_ex.name
        else:  # 非model菜单
            name = app_label
            codename = model_name
            o_permission = Permission.objects.filter(content_type_id=o_content_type.pk, codename=codename).first()
            if o_permission:
                dict_permission[o_permission.pk] = ""

        return dict_permission

    def menu_2_tree(self, menu_item, tree_data, is_sub=True):
        """菜单数据转换成树数据"""
        for dict_item in menu_item:
            dict_tmp = dict()
            dict_tmp["label"] = dict_item['label']
            if "children" in dict_item:
                dict_tmp["children"] = []
                dict_tmp["expand"] = True
                self.menu_2_tree(dict_item["children"], dict_tmp["children"], is_sub)
            else:
                if "href" in dict_item:
                    # codename = "view_%s" % dict_item["href"].lower()
                    # dict_tmp["id"] = Permission.objects.filter(codename=codename).first().pk
                    dict_tmp["id"] = "vadmin.%s" % dict_item["href"].lower()
                    app_label = "vadmin"
                    model_name = dict_item["href"].lower()

                elif "url" in dict_item:
                    # codename = "view_%s" % dict_item["url"].lower()
                    # dict_tmp["id"] = Permission.objects.filter(codename=codename).first().pk
                    dict_tmp["id"] = "vadmin.%s" % dict_item["url"].lower()
                    app_label = "vadmin"
                    model_name = dict_item["url"].lower()

                else:  # "model" in dict_item:
                    # app_label, model_name = dict_item["model"].lower().split(".")
                    # if "?" in model_name:
                    #     model_name, para = model_name.split("?")
                    #     model_name = model_name.strip("/\\")
                    #     url = const.CHANGE_LIST % (app_label, model_name, 1) + "&%s" % para
                    # else:
                    #     url = const.CHANGE_LIST % (app_label, model_name, 1)
                    dict_tmp["url"] = dict_item["model"]
                    dict_tmp["id"] = dict_item["model"]
                    app_label, model_name = dict_item["model"].lower().split(".")
                    if "label" not in dict_item:
                        dict_tmp["label"] = admin_api.get_verbose_name(app_label, model_name)

                if is_sub:
                    dict_permission = self.get_menu_permission(app_label, model_name)
                    dict_tmp["children"] = []
                    for k, v in dict_permission.items():
                        dict_tmp["children"].append({"label": v, "id": k})

            tree_data.append(dict_tmp)

    def create_menu(self, group_id, o_group_ex=None):
        """创建权限组对应的基础数据，不是全量"""
        lst_menu, tree_value = self.get_menu_data_by_group(group_id=group_id)
        if o_group_ex:
            o_group_ex.menu_data = json.dumps(lst_menu, ensure_ascii=False).lower()
            o_group_ex.tree_value = json.dumps(tree_value, ensure_ascii=False)
            o_group_ex.save()
        else:
            o_group_ex = GroupEx.objects.create(name=group_id, group_id=group_id,
                                                menu_data=json.dumps(lst_menu, ensure_ascii=False).lower(),
                                                tree_value=json.dumps(tree_value, ensure_ascii=False), )

        return o_group_ex

    def init_permissions(self):
        """初始化子项权限"""
        lst_codename = (("增加", "add"), ("删除", "delete"), ("修改", "change"), ("查看", "view"))
        for name, codename in lst_codename:
            o_permission_ex = PermissionEx.objects.filter(codename=codename).first()
            if o_permission_ex is None:
                PermissionEx.objects.create(name=name, codename=codename)

    def create_permission(self, app_label, model_name, label, is_sub=True):
        """
        创建权限子项
        :param app_label:
        :param model_name:
        :param label: 菜单中的单项显示名称，或者model中verbose_name
        :param is_sub: 是否有子权限，一般在model下面有多个权限，但是在自定义的url或者herf只有一个view权限
        """
        o_content_type = ContentType.objects.filter(app_label=app_label, model=model_name).first()
        if o_content_type is None:
            o_content_type = ContentType.objects.create(app_label=app_label, model=model_name)

        if is_sub:
            for o_permission_ex in PermissionEx.objects.all():
                name = "%s %s" % (o_permission_ex.name, label)
                codename = "%s_%s" % (o_permission_ex.codename.lower(), model_name.lower())
                o_permission = Permission.objects.filter(content_type_id=o_content_type.pk, codename=codename).first()
                if o_permission is None:
                    Permission.objects.create(name=name, content_type_id=o_content_type.pk, codename=codename)

        else:
            name = app_label
            codename = "view_%s" % model_name.lower()
            o_permission = Permission.objects.filter(content_type_id=o_content_type.pk, codename=codename).first()
            if o_permission is None:
                Permission.objects.create(name=name, content_type_id=o_content_type.pk, codename=codename)

    def get_permissions(self, group_id=None):
        """
        获取用户权限信息
        :param group_id:
        :return:
        """
        if group_id:
            o_group = Group.objects.filter(pk=group_id).first()
            permissions = []
            for o_permission in o_group.permissions.all():
                o_content_type = ContentType.objects.filter(pk=o_permission.content_type_id).first()
                permissions.append("%s.%s" % (o_content_type.app_label, o_permission.codename))

        elif self.request:
            if self.request.user.is_superuser:
                permissions = []
                for o_content_type in ContentType.objects.all():
                    for o_permission in Permission.objects.filter(content_type_id=o_content_type.pk):
                        permissions.append("%s.%s" % (o_content_type.app_label, o_permission.codename))
            else:
                permissions = self.request.user.get_all_permissions()

        else:
            permissions = []
            for o_content_type in ContentType.objects.all():
                for o_permission in Permission.objects.filter(content_type_id=o_content_type.pk):
                    permissions.append("%s.%s" % (o_content_type.app_label, o_permission.codename))

        return permissions

    def get_menu_data(self, no_menu_model=None, menu_items=settings.V_MENU_ITEMS):
        """
        获取菜单数据（重新构造，不从缓存中获取）
        no_menu_model:没有再settings中配置的model
        menu_items:settings中配置的菜单数据
        """
        dict_model_name = {}
        dict_permission = {}
        permissions = self.get_permissions()
        for permission in permissions:
            app_label, model_name = permission.split(".", 1)
            auth, model_name = model_name.split("_", 1)
            app_model_name = "%s.%s" % (app_label, model_name)
            dict_model_name[app_model_name] = admin_api.get_verbose_name(app_label, model_name)
            dict_permission.setdefault(app_model_name, []).append(permission)

        lst_menu = []
        self.parse_menu(menu_items, lst_menu, dict_permission, dict_model_name, no_menu_model)
        return lst_menu

    def get_menu_data_by_group(self, group_id):
        """
        根椐分组id，获取菜单数据
        :param group_id: 分组id
        :return:
        """
        # dict_model_auth = {}
        dict_model_name = {}
        dict_permission = {}
        permissions = self.get_permissions(group_id)
        for permission in permissions:
            app_label, model_name = permission.split(".", 1)
            auth, model_name = model_name.split("_", 1)
            app_model_name = "%s.%s" % (app_label, model_name)
            dict_model_name[app_model_name] = admin_api.get_verbose_name(app_label, model_name)

            dict_permission.setdefault(app_model_name, []).append(permission)

        lst_menu = []
        tree_value = []
        self.parse_menu(settings.V_MENU_ITEMS, lst_menu, dict_permission, dict_model_name, tree_value=tree_value)
        return lst_menu, tree_value

    def get_menu(self):
        if self.request:
            if hasattr(settings, "V_USER_MENU_ITEMS"):
                if "user" in settings.V_USER_MENU_ITEMS:
                    user = settings.V_USER_MENU_ITEMS["user"]
                    if isinstance(user, str):
                        user = [user, ]

                    if self.request.user.username in user:
                        self.init_menu_id(settings.V_USER_MENU_ITEMS["menu"])
                        lst_menu = self.get_menu_data(None, settings.V_USER_MENU_ITEMS["menu"])
                        return lst_menu

                elif "filter_user" in settings.V_USER_MENU_ITEMS:
                    filter_user = settings.V_USER_MENU_ITEMS["filter_user"]
                    if isinstance(filter_user, str):
                        filter_user = [filter_user, ]

                    if self.request.user.username not in filter_user:
                        self.init_menu_id(settings.V_USER_MENU_ITEMS["menu"])
                        lst_menu = self.get_menu_data(None, settings.V_USER_MENU_ITEMS["menu"])
                        return lst_menu

            if self.request.user.is_superuser:
                o_group_ex = GroupEx.objects.filter(key=self.CON_BASE_MENU).first()
                if (o_group_ex is None) or (o_group_ex.menu_data in [None, "", "[]"]):
                    o_group_ex = self.init_menu_permission()

                return json.loads(o_group_ex.menu_data)

            else:
                # 只有一个权限组的情况下
                lst_group = self.request.user.groups.all()
                group_num = len(lst_group)
                if group_num == 0:
                    return []

                elif group_num == 1:
                    group_id = lst_group[0].pk
                    o_group_ex = GroupEx.objects.filter(group_id=group_id).first()
                    if (o_group_ex is None) or (o_group_ex.menu_data in [None, "", "[]"]):
                        o_group_ex = self.create_menu(group_id, o_group_ex)

                    return json.loads(o_group_ex.menu_data)
                else:
                    return self.get_menu_data()  # 多个权限组的情况

        elif self.is_all:
            o_group_ex = GroupEx.objects.filter(key=self.CON_BASE_MENU).first()
            if (o_group_ex is None) or (o_group_ex.menu_data is None):
                o_group_ex = self.init_menu_permission()

            return json.loads(o_group_ex.menu_data)

    def update_menu_data(self, obj=None):
        """更新菜单数据"""
        for o_group_ex in GroupEx.objects.all():
            if o_group_ex.key == self.CON_BASE_MENU:
                # 更新
                self.update_menu_permission()

            else:
                o_group_ex.menu_data = None
                if obj:
                    new_value = []
                    lst_value = eval(o_group_ex.tree_value or "[]")
                    for permission_id in lst_value:
                        o_permission = Permission.objects.filter(pk=permission_id).first()
                        if (o_permission is None) or (obj.codename == o_permission.codename.split("_")[0]):
                            pass
                        else:
                            new_value.append(permission_id)
                    o_group_ex.tree_value = str(new_value)
                o_group_ex.save()

    def _parse_menu_item(self, item, lst_menu, dict_permission, dict_model_name, no_menu_model=None, tree_value=None):
        app_model_name = None
        if "model" in item:
            item["model"] = item["model"].lower()
            app_model_name = item["model"]

            if self.has_menu_permission(dict_permission, app_model_name):
                dict_menu = parse_menu_item_param(item)
                dict_menu["label"] = item.get("label", dict_model_name.get(app_model_name, app_model_name))
                dict_menu["model"] = item["model"]
                lst_menu.append(dict_menu)

            if no_menu_model and app_model_name in no_menu_model:
                del no_menu_model[app_model_name]

        elif "url" in item:
            app_model_name = "vadmin.%s" % item["url"].lower()
            if self.has_menu_permission(dict_permission, app_model_name):
                dict_menu = parse_menu_item_param(item)
                dict_menu["url"] = item["url"]
                lst_menu.append(dict_menu)

        elif "href" in item:
            app_model_name = "vadmin.%s" % item["href"].lower()
            if self.has_menu_permission(dict_permission, app_model_name):
                dict_menu = parse_menu_item_param(item)
                dict_menu["href"] = item["href"]
                lst_menu.append(dict_menu)

        if tree_value is not None and app_model_name:
            for permission in dict_permission.get(app_model_name, []):
                app_label, codename = permission.split(".", 1)
                o_permission = Permission.objects.filter(codename=codename).first()
                if o_permission and (o_permission.pk not in tree_value):
                    tree_value.append(o_permission.pk)

    def parse_menu(self, items, lst_menu, dict_permission, dict_model_name, no_menu_model=None, tree_value=None):
        """
        从配置数据转换成menu 格式数据
        """
        if isinstance(items, (list, tuple)):
            for item in items:
                if "children" in item:
                    dict_menu = parse_menu_item_param(item)
                    lst_menu_sub = []
                    self.parse_menu(item['children'], lst_menu_sub, dict_permission, dict_model_name, no_menu_model,
                                    tree_value)
                    if lst_menu_sub:
                        dict_menu["children"] = lst_menu_sub
                        lst_menu.append(dict_menu)
                else:
                    self._parse_menu_item(item, lst_menu, dict_permission, dict_model_name, no_menu_model, tree_value)

        else:
            self._parse_menu_item(items, lst_menu, dict_permission, dict_model_name, no_menu_model, tree_value)

    def get_models(self):
        no_menu_model = {}
        for model in django_apps.get_models():
            if model._meta.app_label in ["vadmin", "admin", "auth", "contenttypes", "sessions"]:
                continue

            no_menu_model["%s.%s" % (model._meta.app_label, model._meta.model_name)] = \
                str(model._meta.verbose_name)

        return no_menu_model
