# !/usr/bin/python
# -*- coding=utf-8 -*-
import collections
from vadmin import common

######################################## 操作项 ##############################################
# O_TABLE_ROW_DEL = "table_row_del"  # 行删除(单行）
# # # TABLE_ROW_MULTIPLE_DEL = "table_row_multiple_del"  # 多行删除
# O_TABLE_ROW_ADD = "table_row_add"  # 行增加
# O_TABLE_ROW_EDIT = "table_row_edit"  # 行编辑
# O_TABLE_ROW_SAVE = "table_row_save"  # 行保存
# O_TABLE_ROW_UPDATE = "table_row_update"  # 行修改
# O_TABLE_SELECT_ALL = "table_select_all"  # 表格全部选择
# # TABLE_COL_SORT = "table_sort"  # 列排序

######################################## 表格数据提交关键字 ##################################
# TABLE_SAVE = "table_save"  # 表格数据保存
# TABLE_DEL = "table_del"  # 表格数据保存
# TABLE_OPERA = "table_opera"  # 表格操作

######################################### 页面操作 ###########################################
# PAGE_QUERY = "query"
# PAGE_ADD = "add"
# PAGE_SAVE = "save"
# PAGE_SAVE_EDIT = "save_edit"
# PAGE_SAVE_ADD = "save_add"
# PAGE_SAVE_COPY_ADD = "save_copy_add"

######################################### 关键字 ######################################


# PARENT_ID = "p-id"  # 父窗口对象ID
# RELATED_FIELD_NAME = "r-f-n"  # 外键关联的字段名称
MENU_ITEM_ID = "m-%s"
UPN_SEARCH_KEY = "search-key"  # 搜索按钮关键字

# url参数名称
UPN_SCREEN_WIDTH = "s-w"  # 屏幕宽度（在接口中，由前端传入后台屏幕宽度关键字）
UPN_SCREEN_HEIGHT = "s-h"  # 屏幕高度（在接口中，由前端传入后台屏幕高度关键字）
UPN_MENU_ID = "menu-id"  # 菜单ID
UPN_TOP_ID = "menu-top-id"  # 头部菜单ID
UPN_LEFT_ID = "menu-left-id"  # 左边菜单ID
UPN_MENU_MODE = "menu-mode"
UPN_APP_NAME = "app-name"  # APP名称
UPN_MODEL_NAME = "model-name"  # model名称
UPN_OBJECT_ID = "object-id"
UPN_RELATED_APP = "related-app"  # 关联的app名称
UPN_RELATED_MODEL = "related-model"  # 关联的model名称
UPN_RELATED_FIELD = "related-field"  # 外键关联的字段名称
UPN_RELATED_TO_FIELD = "related-to-field"  # 外键关联的model to_field
UPN_RELATED_ID = "related-id"  # 外键关联的父对象ID
UPN_DISPLAY_MODE = "display-mode"  # 显示方式参数
UPN_PREV_ID = "prev-id"
UPN_NEXT_ID = "next-id"
UPN_ORDER_ID = "order-id"
UPN_WIDGET_ID = "widget-id"  # 组件ID，前端分配
UPN_STEPS_IDX = "steps-idx"
UPN_PAGE_SIZE = "page-size"
UPN_DEL_SECTION = "del-section"
UPN_CALLBACK_SCRIPT = "c-s"
UPN_PDF_2_IMAGE = "p-2-i"
# 显示模式
# http://192.168.2.106/vadmin/#v_change_list/case/widget/?s-m=none # 不显示顶部和左边菜单
# http://192.168.2.106/vadmin/#v_change_list/case/widget/?s-m=top # 显示顶部
# http://192.168.2.106/vadmin/#v_change_list/case/widget/?s-m=left # 显示左边
UPN_SHOW_MODE = "s-m"  # 显示模式
UPN_REDIRECT_URL = "r-url"  # 跳转URL

# 组件名称
WN_TOP = "v_top"  # 头部区域
WN_CONTENT = "g_c"  # 内容区域名称
WN_CONTENT_FILTER = "g_f"  # 内容区域过滤区域名称
WN_CONTENT_LEFT = "left_menu"  # 左边内容区域名称
WN_CONTENT_RIGHT = "c_r"  # 右边内容区域名称
WN_CONTENT_RIGHT_FILTER = "c-r-f"  # 右边内容过滤区域名称
WN_CONTENT_FILTER_FOLD = "c-r-flod"  # 折叠按钮
WN_CONTENT_HIDE = "c_h"  # 内容区域隐藏组件名称（是否只修改内容区域）
WN_MENU_LEFT = "left_menu"  # 左边菜单名称
WN_MENU_TOP = "top_menu"  # 顶部菜单名称
WN_SEARCH = "search-%s-%s"  # 列表界面搜索输入框组件名称
WN_TABLE = "table-%s-%s"  # 列表界面表格名称
WN_FIELDSET = "table-%s-%s-%s"  # 列表区域名称
WN_TREE = "tree-%s"  # 删除树的名称
WN_FORM_TABS = "tabs-%s"  # 表单界面tabs组件名称
WN_CHANGE_LIST = "list-%s-%s"  # 列表界面区域名称
WN_PAGINATION = "p-%s"  # 分页名称
WN_COUNT_TEXT = "c-%s"  # 条数名称
WN_SELECT_ALL = "select_all"  # 全部选择框名称
WN_PART_LOAD = "p_l"  # 局部加载
WN_TITLE = "v-title"
WN_LOGO = "v-logo"
WN_BOX_INPUT = "box_input"
WN_BOX_SELECT = "box_select"
WN_FILTER_KEY = "fk-"  # 过滤关键字，避免子表中过滤字段和form字段同名的情况

# 组件操作
OPERA_TABLE_ROW_DEL = "table_row_del"
OPERA_TABLE_ROW_ADD = "table_row_add"
OPERA_TABLE_ROW_EDIT = "table_row_edit"
OPERA_TABLE_ROW_UPDATE = "table_row_update"
OPERA_TABLE_ROW_SAVE = "table_row_save"
OPERA_TABLE_SELECT_ALL = "table_select_all"
OPERA_TREE_NODE_UPDATE = "tree_node_update"
OPERA_TREE_NODE_ADD = "tree_node_add"
OPERA_TREE_NODE_DEL = "tree_node_del"
OPERA_TREE_NODE_ORDER = "tree_node_order"

######################################## URL 接口 ############################################
URL_LOGIN = "v_login/"
URL_INDEX_VIEW = "v_index_view/"
URL_HOME_VIEW = "v_home_view/"
URL_UPDATE_PWD = "v_update_pwd/"
URL_UPDATE_PWD_OTHER_USER = "v_update_pwd_other_user/"
URL_UPLOAD_FILE = "v_upload_file/"
URL_UPLOAD_FILE_MODEL = "v_upload_file_by_model/%s/%s/%s/"
URL_UPLOAD_FILE_RESUME = "v_update_file_resume/%s"
URL_UPLOAD_UEDITOR = "v_upload_ueditor/%s/%s/%s/"
# URL_SELECT_CHANGE = "v_select_change/%s/%s/%s/"

URL_HOME = "v_home/"
URL_TOP = "v_top/"
URL_LEFT = "v_left"
URL_LIST = "v_list/%s/%s/"
# CHANGE_LIST_LOADING = "v_list_loading/%s/%s/"
URL_LIST_DEL_VIEW = "v_list_del_view/%s/%s/"
URL_LIST_DEL = "v_list_del/%s/%s/"
URL_LIST_SAVE = "v_list_save/%s/%s/"
URL_LIST_ORDER = "v_list_order/%s/%s/"
URL_LIST_OPERA = "v_list_opera/%s/%s/%s/"
URL_LIST_EXPORT = "v_list_export/%s/%s/"
URL_LIST_POPUP = "v_list_popup/%s/%s/"
URL_LIST_FILTER = "v_list_filter/%s/%s/"
URL_LIST_SELECT_CLOSE = "v_list_select_close/%s/%s/"
URL_LIST_DELETE_CLOSE = "v_list_delete_close/%s/%s/"
URL_LIST_ROW_SAVE = "v_list_row_save/%s/%s/"
URL_LIST_TREE_LOAD = "v_list_tree_load/%s/%s/%s/"
URL_INLINE_DEL = "v_inline_del/%s/%s/%s/%s/"
CHANGE_INLINE_SAVE = "v_inline_save/%s/%s/%s/"


URL_FORM = "v_form/%s/%s/"
URL_FORM_ADD = "v_form_add/%s/%s/"
URL_FORM_COPY_ADD = "v_form_copy_add/%s/%s/"

URL_FORM_POPUP = "v_form_popup/%s/%s/"
URL_FORM_CHILD_POPUP = "v_form_child_popup/%s/%s/"
URL_FORM_SAVE = "v_form_save/%s/%s/"
URL_FORM_SAVE_EDIT = "v_form_save_edit/%s/%s/"
URL_FORM_SAVE_CLOSE = "v_form_save_close/%s/%s/"
URL_FORM_SAVE_ADD = "v_form_save_add/%s/%s/?id=%s"
URL_FORM_SAVE_COPY_ADD = "v_form_save_copy_add/%s/%s/?id=%s"
URL_FORM_DEL_VIEW = "v_form_del_view/%s/%s/?id=%s"
URL_FORM_FIELD_CHANGE = "v_form_field_change/%s/%s/%s/?id=%s"

# URL_FORM_DEL = "v_change_form_del/%s/%s/%s/"
URL_TREE_OPERA = "v_tree_opera/%s/%s/%s/"
# TREE_NODE_DEL = "v_tree_node_del/%s/%s/%s/"
# TREE_NODE_UPDATE = "v_tree_node_update/%s/%s/%s/"
# TREE_NODE_ORDER = "v_tree_node_order/%s/%s/%s/"
URL_RUN_SCRIPT = "v_run/%s"
URL_SELECT_SEARCH = "v_select_search/"
URL_EXPORT_WORD = "v_export_word/"
URL_IMPORT_WORD = "v_import_word/"
ASC = "asc"  # 升序
DESC = "desc"  # 降序

USE_TEMPLATE = "template"

############################
SUBMIT_WIDGET = 'widget_data'  # 提交的组件数据，返回{}
SUBMIT_HIDE = 'hide_data'  # 提交的隐藏数据，返回[]
SUBMIT_OPERA = 'opera_data'  # 提交的操作数据，返回[]
SUBMIT_EVENT = 'event_data'  # 提交的事件数据

# POST_CONTENT = "content"  # POST提交的内容关键字
INLINE_DISPLAY_TABULAR = "tabular"  # 子表表格显示
INLINE_DISPLAY_STACKED = "stacked"  # 子表叠加显示
INLINE_DISPLAY_LIST = "list"  # 子表change_list显示

DM_FORM_LINK = "form-link"  # 链接显示
DM_FORM_POPUP = "form-popup"  # 弹出显示
DM_LIST_CHILD = "list-child"  # form下面的子表
DM_LIST_SELECT = "list_select"  # 弹出旋转

######################################### form 中效果     ###################################
COLOR_LINK = "#0088CC"  # 链接颜色
COLOR_LINK_FOCUS = common.calc_focus_color(COLOR_LINK)  # 链接焦点颜色
COLOR_SUCCESS = "#699FE9"  # 成功样式
COLOR_ERROR = "#E75E60"  # 失败颜色
COLOR_PROCESS = "#FFA359"  # 处理过程颜色
COLOR_CANCEL = "#A7A9AC"  # 取消颜色

COLOR_RANDOM = [
    "#880015", "#ED1C24", "#FF7F27", "#FFF200", "#22B14C", "#00A2E8", "#3F48CC", "#A349A4",
    "#B97A57", "#FFAEC9", "#FFC90E", "#EFE4B0", "#B5E61D", "#99D9EA", "#7092BE", "#C8BFE7",

    "#C00000", "#FF0000", "#FFC000", "#FFFF00", "#7030A0",
    "#FFFF00", "#00B050", "#00B050", "#0070C0", "#002060",

    # "#938953", "#494429", "#1D1B10",
    # "#548DD4", "#17365D", "#0F243E",
    # "#95B3D7", "#366092", "#244061",
    # "#D99694", "#953734", "#632423",
    # "#C3D69B", "#76923C", "#4F6128",
    # "#B2A2C7", "#5F497A", "#3F3151",
    # "#92CDDC", "#31859B", "#205867",
    # "#FAC090", "#E46D0A", "#974806",
]

PWD_LENGTH = 12
PWD_VALIDATION_MSG = "密码检查错误信息:{{\n}}%s{{row.20}}密码组成规则:{{\n}}1、密码不能和用户名相似{{\n}}2、密码长度最少需要%s位{{\n}}3、密码不能是常用密码，必须是大小写字母+数字混合"
FONT_FAMILY = [
    ("SimSun", "宋体"),
    ("NSimSun", "新宋体"),
    ("SimHei", "黑体"),
    ("KaiTi", "楷体"),
    ("Microsoft YaHei", "微软雅黑"),
    ("Microsoft JhengHei", "微软正黑体"),
    # ("SimSun-ExtB", "扩展宋体"),

]

BOOL_CHINESE = collections.OrderedDict(((True, "是"), (False, "否")))
CACHE_KEY_GROUP_ID = "group-id"
CACHE_KEY_GROUP_KEY = "group-key"
CACHE_KEY_GROUP_NAME = "group-name"

#######################################  msg ##################################################
