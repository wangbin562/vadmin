# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
user admin
"""
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _

from user.models import Department  # pylint: disable=E0401
from user.models import Role  # pylint: disable=E0401
from user.models import User  # pylint: disable=E0401
from user import filter
from vadmin import admin_api
from vadmin import theme
from vadmin.admin import VModelAdmin


@admin.register(Department)
class DepartmentAdmin(VModelAdmin):
    """
    部门
    """
    list_display = ["name", "create_time", "del_flag"]
    v_sortable = True
    exclude = ["order"]


@admin.register(Role)
class RoleAdmin(VModelAdmin):
    """
    部门
    """
    list_display = ["department", "name", "create_time", "del_flag"]
    v_sortable = True
    exclude = ["order"]


@admin.register(User)
class UserAdmin(VModelAdmin):
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('email',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
    )
    # form = UserChangeForm
    add_form = UserCreationForm
    # change_password_form = AdminPasswordChangeForm
    list_display = ('username', 'email', 'is_staff', 'department', 'role')
    list_v_filter = (filter.TimeIntervalFilter, 'is_staff', 'is_superuser', 'is_active', 'groups', 'department', 'role')
    search_fields = ('username', 'email')
    ordering = ('username',)
    filter_horizontal = ('groups', 'user_permissions',)
    readonly_fields = ("password",)
    change_form_add = "v_user_add_view/"
    exclude = ('user_permissions',)

    change_list_config = {"col_horizontal": {'username': "left", "email": "center", "is_staff": "right"}}
    change_list_filter_config = {"number": 4}

    def get_fieldsets(self, request, obj=None):
        if not obj:
            return self.add_fieldsets

        model_admin = admin_api.get_model_admin("auth", "group")
        if model_admin.has_module_permission(request):
            fieldsets = (
                (None, {'fields': ('username', 'password')}),
                (_('Personal info'), {'fields': ('mobile', 'email',)}),
                ('部门信息', {'fields': ('department', 'role',)}),
                (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                               'groups', 'user_permissions')}),
                (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
            )
            return fieldsets

        fieldsets = (
            (None, {'fields': ('username', 'password')}),
            (_('Personal info'), {'fields': ('email',)}),
            (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
        )
        return fieldsets

    def password(self, request, obj=None):
        from vadmin import widgets
        from vadmin import step
        from vadmin import widget_view
        from vadmin import const

        if obj and obj.id == request.user.id:
            o_text = None
        else:
            o_theme = theme.get_theme(request.user.id)
            o_step = widget_view.make_update_pwd_other_user(request)
            o_text = widgets.Text(text="修改密码",
                                  font={"size": o_theme.font["size"] - 2, "decoration": "underline",
                                        "color": const.COLOR_LINK},
                                  focus={"color": const.COLOR_LINK_FOCUS},
                                  step=o_step, margin_left=10)

        if obj:
            password = obj.password
            return {"name": "密码", "widget": [widgets.Input(value=password, disabled=True), o_text]}
        else:
            password = None

    # def user_permissions(self, request, obj=None):
    #     """自定义permission组件"""
    #     from vadmin import widgets
    #     from vadmin import menu
    #     lst_menu = menu.get_menu(request)
    #     tree_data = []
    #     if obj is None:
    #         auth_permission_id = []
    #     else:
    #         auth_permission_id = list(obj.user_permissions.all().values_list("pk", flat=True))
    #         # auth_permission_id = list(o_group.permissions.all().values_list("pk", flat=True))
    #         # auth_permission_id = []
    #     menu.parse_menu(lst_menu, tree_data)
    #     o_tree = widgets.Tree(name="user_permissions", data=tree_data, select=True, border_color="#F0F2F4", height=700, width=600)
    #     return {"name": "权限", "widget": o_tree}
    #
    # def user_permissions_save(self, request, obj, k, v, update_data, dict_error):  # 保存时回调，可以没有
    #     """
    #     自定义组件保存函数
    #     同时保存django权限表和本数据表t_auth_group表
    #     :param request:
    #     :param obj:旧对象(如果是新建,pk等于None)
    #     :param k:自定义的组件name
    #     :param v:界面提交的值
    #     :param update_data: 要保存到数据库中的值, key为字段名称，value为修改后的值
    #     :param dict_error: 错误信息
    #     :return:
    #     """
    #     v = v or []
    #     if list(obj.user_permissions.all()) != v:
    #         update_data[k] = v

# admin.site.register(User, UserAdmin)
