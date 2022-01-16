# !/usr/bin/python
# -*- coding=utf-8 -*-
"""settings"""

import os
from platform import platform

if 'centos' in platform():
    DEBUG = False
else:
    DEBUG = True

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
SECRET_KEY = 'sg%paa6(4tw@(%z3kxjlq-+kd=zo8akpl_s^z=4qs=mv+c*4gc'
ALLOWED_HOSTS = ['*', '127.0.0.1', '192.168.1.215', '47.93.250.243', '*.*.*.*']

INSTALLED_APPS = (
    'vadmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'timed_task',
    'vadmin_standard',
    'file_manager',
    'user',
    'case',
    'provincial_case',
    'mark',
    'system',
    'help',
    'workflow',
)

MIDDLEWARE = MIDDLEWARE_CLASSES = (
    # MIDDLEWARE_CLASSES = (
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.admindocs.middleware.XViewMiddleware',
    # 'debug_toolbar.middleware.DebugToolbarMiddleware',
    # 'django.middleware.gzip.GZipMiddleware',

)

# 新建和修改密码要检查
# AUTH_PASSWORD_VALIDATORS = [
#     {
#         # 检验和用户信息的相似度
#         'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
#     },
#     {
#         # 校验密码最小长度
#         'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
#     },
#     {
#         # 校验是否为过于简单（容易猜）密码
#         'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
#     },
#     {
#         # 校验是否为纯数字
#         'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
#     },
# ]

ROOT_URLCONF = 'hmi.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # 'django.template.context_processors.debug',
                # 'django.template.context_processors.request',
                # 'django.template.context_processors.i18n',
                # 'django.template.context_processors.media',
                # 'django.template.context_processors.static',
                # 'django.template.context_processors.tz',
                'django.contrib.auth.context_processors.auth',
                # 'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'hmi.wsgi.application'
if "mac" in platform():
    HOST = '127.0.0.1'
    DB_NAME = 'vadmin_v3'
    DB_USER = 'root'
    DB_PWD = '12345678'
elif DEBUG:
    HOST = '127.0.0.1'
    DB_NAME = 'vadmin_v3'
    DB_USER = 'root'
    DB_PWD = '123456'
else:
    HOST = '127.0.0.1'
    DB_NAME = 'vadmin_v3'
    DB_USER = 'root'
    DB_PWD = 'ZHONGshi8'

DATABASES = {
    'default': {
        # 'ENGINE': 'django.db.backends.sqlite3',
        # 'NAME': os.path.join(BASE_DIR, 'hmi.sqlite3'),
        'ENGINE': 'django.db.backends.mysql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PWD,
        'HOST': HOST,
        'PORT': '3306',
        # 'OPTIONS': {
        #     "init_command": "SET foreign_key_checks = 0;",
        # },
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
        'TIMEOUT': 60 * 15,  # 缓存超时时间（默认300秒，None表示永不过期，0表示立即过期）
    }
}

# CACHES = {
#     'default': {
#         'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#         'LOCATION': 'localhost:11211',
#         'TIMEOUT': 500,  # 缓存超时时间（默认300秒，None表示永不过期，0表示立即过期）
#         'OPTIONS': {
#         }}
# }

SITE_ID = 1
LANGUAGE_CODE = 'zh-hans'
TIME_ZONE = 'Asia/Shanghai'
USE_I18N = True
USE_L10N = True
USE_TZ = False
DATE_FORMAT = 'Y-m-d'
DATETIME_FORMAT = 'Y-m-d H:i'
TIME_FORMAT = 'H:i'
STATIC_URL = '/static/'
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
X_FRAME_OPTIONS = 'SAMEORIGIN'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(threadName)s:%(thread)d] [%(name)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    'filters': {
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler',
            'include_html': True,
        },
        'default': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR + '/logs/', 'request.log'),
            'maxBytes': 1024 * 1024 * 2,  # 2 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'console': {  # 输出到控制台
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'standard'
        },
        'request_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR + '/logs/', 'hmi.log'),
            'maxBytes': 1024 * 1024 * 2,  # 2 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
        'scripts_handler': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR + '/logs/', 'hmi.log'),
            'maxBytes': 1024 * 1024 * 2,  # 2 MB
            'backupCount': 10,
            'formatter': 'standard',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': False
        },
        '': {
            'handlers': ['default', 'console'],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.server': {
            'handlers': ['default', ],
            'level': 'DEBUG',
            'propagate': True
        },
        'django.request': {
            'handlers': ['request_handler'],
            'level': 'DEBUG',
            'propagate': False
        },
        'scripts': {
            'handlers': ['scripts_handler'],
            'level': 'INFO',
            'propagate': False
        },
    }
}

AUTH_USER_MODEL = 'user.User'  # 自定义
# AUTH_USER_MODEL = 'auth.User' # 系统
V_URL_BASE = "admin/"
V_LOGO = "login.jpg"
V_TITLE = "综合业务服务管理系统"
# 自定义
# from vadmin import widgets
#
# V_TOP_ADD_ITEMS = [{"icon": "fa-question-circle", "label": "帮助", "url": "/v_help_view/"},
#                    {"icon": "el-icon-video-camera-solid", "label": "组件测试", "url": "/test_widget/"},
#                    {"icon": "el-icon-menu", "label": "维修报修统计", "url": "/repair_total_view/"},
#                    {"icon": "el-icon-menu", "label": "维修报修", "url": "/repair_view/"},
#                    widgets.TimedRefresh(text="定时刷新({})", width=100, height=30, round=8, second=100,
#                                         text_color="#FFFF00",
#                                         background_color="#FF0000")]
# V_DEFAULT_PWD = "123456"
V_TOP_THEME = True
from vadmin import widgets
from vadmin import step
from vadmin import const

url = const.URL_RUN_SCRIPT % "help.views.v_help_view"
o_icon = widgets.Button(icon="v-export-pdf", tooltip="帮助",
                        step=step.Get(url=url, jump=True, new_window=True, unique=True))
V_TOP_ADD_ITEMS = [o_icon]

# V_INDEX_PAGE = {'label': u'首页', 'icon': 'fa-home', 'url': 'v_home_view/'}
V_MENU_POSITION = "top"  # 菜单显示位置 "left" or "top"
V_MENU_ITEMS = [
    # {'label': u'首页', 'icon': 'fa-home', 'href': '/vadmin/v_home/'}
    {'label': u'用户管理', 'icon': 'el-icon-setting', "id": "aa", 'children': [
        {'label': u'个人信息', 'model': 'user.user'},
        {'model': 'user.Department'},
        {'model': 'user.Role'},
        {'label': u'权限管理', 'model': 'vadmin.GroupEx'},
        {'label': u'权限子项', 'model': 'vadmin.PermissionEx'},
        # {'label': u'个人信息', 'children': [
        #     {'label': u'权限管理', 'model': 'auth.group'},
        # ]},
    ]},
    {'label': u'维护管理', 'icon': 'el-icon-menu', 'children': [
        {'label': u'航标管理', 'children': [
            {'label': u'航标信息', 'image': STATIC_URL + r'vadmin/hangdao/dynamic-list.png',
             'image_select': STATIC_URL + r'vadmin/hangdao/dynamic-list-hover.png',
             'model': 'mark.MarkInfo'},
            {'label': u'终端信息', 'model': 'mark.MarkTerminal'},
            {'label': u'航标动态', 'model': 'mark.markdynamic'},
        ]},
    ]},
    {'label': u'省检案例', 'icon': 'el-icon-menu', 'children': [
        {'model': 'provincial_case.CheckManage'},
        # {'label': '侦查管理', 'model': 'ajjbxx.Ajjbxx/?m=3'},
        # {'label': '侦查管理', 'model': 'zcgl.Lazcxx'},
    ]},
    {'label': u'WORD案例', 'icon': 'el-icon-document', 'children': [
        {'label': "word转vadmin", 'model': 'case.TemplateExample'},
        {'label': "word转word", 'href': '/test_word_2_vadmin/'},
        {'label': u'html转word', 'model': 'case.Rich'},
        # {'label': "word案例", 'url': '/word_view/'},
        {'label': "word转html word", 'model': 'case.TemplateExample&%s=2' % const.UPN_MENU_MODE},
    ]},
    {'label': u'案例', 'icon': 'el-icon-menu', 'children': [
        {'model': 'case.widget'},
        {'label': u'省', 'model': 'case.province'},
        {'label': u'市', 'model': 'case.city'},
        {'label': u'区', 'model': 'case.area'},
        {'label': u'单位', 'icon': 'el-icon-menu', 'children': [
            {'label': u'单位1', 'model': 'case.unit/?m=1'},
            # {'label': u'单位2', 'url': '/unit_change_list/?m=2'},
            {'label': u'单位3', 'model': 'case.unit/?m=3'},
        ]},
        {'label': "滑动块（swipe）案例", 'url': '/test_swipe/'},
        {'label': "轮播（carousel）案例", 'url': '/test_carousel/'},
        {'label': "标签页（tabs）案例", 'url': '/test_tabs/'},
        {'label': "时间轴（timeline）案例", 'url': '/test_timeline/'},
        {'label': "折叠面板（collapse）案例", 'url': '/test_collapse/'},
        # {'label': u'自定义(使用vadmin)', 'url': '/custom/'},
        # {'label': u'自定义(含菜单使用vadmin)', 'url': '/custom_menu/'},
        # {'label': u'自定义(使用模板)', 'url': '/custom_template/'},
        # {'label': u'自定义(含菜单使用模板)', 'url': '/custom_menu_template/'},
        # {'label': u'自定义(使用vue)', 'url': '/custom_vue/'},
        # {'label': u'自定义(含菜单使用vue)', 'url': '/custom_menu_vue/'},
        {'label': "折叠、图片统一管理器、多级过滤案例", 'model': 'case.CollapseExample'},
        {'model': 'case.TreeExample'},
        {'model': 'case.DateExample'},
        {'model': 'case.FileExample'},
        {'label': u'百度', 'href': 'https://wwww.baidu.com'},
        # {'label': u'文件管理', 'href': '/test_file_manager/'},
        {'label': u'文件管理', 'model': 'file_manager.File'},
        {'label': u'excel模板(转vadmin)', 'href': '/test_template_2_vadmin/'},
        # {'label': u'图片管理', 'model': 'vadmin.Image'},
        {'label': "树表格", 'model': 'case.TreeTable'},
    ]},
    # {'label': u'树表格', 'icon': 'el-icon-menu', 'model': 'case.TreeTable'},
    # {'label': u'网易', 'href': 'https://163.com'},
    # {'label': u'统计报表', 'icon': 'el-icon-menu', 'children': [
    #     {'label': u'分数统计', 'url': 'v_report/case.service.report_test/'},
    # ]},
    {'label': u'帮助配置', 'icon': 'el-icon-menu', 'children': [
        {'model': 'help.HelpMenu'},
        {'model': 'help.HelpMenuLeft'},
        {'model': 'help.HelpContent'},
        # {'label': '帮助', "url": "/v_help_view/"},
    ]},

    # {'label': u'工作流', 'icon': 'el-icon-menu', 'children': [
    #     # {'model': 'workflow.Flow', 'label': u'工作流配置'},
    #     {'label': "发请审批", "url": "/workflow_view/"},
    #     {'label': "代办事项", "url": "/workflow_view/"},
    #     # {'label': "审批列表", 'children': [
    #     #     {'label': '待我审批的', "url": "/workflow_me_approve_view/"},
    #     #     {'label': '我已审批的', "url": "/workflow_me_already_approve_view/"},
    #     #     {'label': '我发起的', "url": "/workflow_me_star_view/"},
    #     #     {'label': '抄送我的', "url": "/workflow_me_cc_view/"},
    #     # ]},
    #     {'label': u'工作流数据', 'icon': 'el-icon-menu', 'children': [
    #         {'model': 'workflow.Flow'},
    #         {'model': 'workflow.FlowNode'},
    #         {'model': 'workflow.FlowData'},
    #         {'model': 'workflow.FlowNodeData'},
    #     ]},
    # ]},
    {'label': u'系统管理', 'icon': 'el-icon-setting', 'children': [
        {'label': '权限组', 'model': 'vadmin.GroupEx'},
        {'label': '权限子项', 'model': 'vadmin.PermissionEx'},
        {'model': 'file_manager.File'},

        {'label': "日志", "children": [
            {'model': 'vadmin_standard.OperationLog'},
            {'model': 'vadmin_standard.ErrorLog'},
            {'model': 'vadmin_standard.DBDataLog'},
        ]},
        {'label': "定时任务", "children": [
            {'model': 'timed_task.TimedTask'},
            {'model': 'timed_task.TimedTaskLog'},
        ]},
        {'model': 'vadmin_standard.AppVersion'},
        {'model': 'vadmin_standard.Dictionary'},
        {'model': 'vadmin_standard.Api'},
        {'model': 'vadmin_standard.Environment'},
        {'model': 'vadmin_standard.DataDump'},
        {'model': 'vadmin_standard.Todo'},
        {'model': 'vadmin_standard.License'},
        {'model': 'vadmin_standard.VersionPatch'},
    ]},
]
