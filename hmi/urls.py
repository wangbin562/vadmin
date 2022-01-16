# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
url配置模块
"""
import os
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic.base import RedirectView
from django.views.static import serve
from hmi import views
from vadmin import views as vadmin_views
from hmi import views as hmi_views

urlpatterns = [
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^%s' % settings.V_URL_BASE, include('vadmin.urls')),
    # url(settings.V_URL_BASE, include('help.urls')),
    url(r'^%s' % settings.V_URL_BASE, include('workflow.urls')),
    url(r'^', include('vadmin_standard.urls')),
    url(r'^%s' % settings.V_URL_BASE, include('file_manager.urls')),
    # 第一个页面请求"vadmin/v_index_view/"在前端固定，如果V_BASE_URL不等于vadmin，在工程url中要增加如下一行
    # 登录页面可以重写v_index_view函数
    url(r'^%sv_index_view/$' % settings.V_URL_BASE, vadmin_views.v_index_view),
    url(r'^v_app_index_view/$', hmi_views.v_app_index_view),

    url(r'^%scustom/$' % settings.V_URL_BASE, views.custom),
    url(r'^custom_menu_template/$', views.custom_menu_template),
    url(r'^test_row_del/$', views.test_row_del),
    url(r'^test_row_save/$', views.test_row_save),
    url(r'^%stest_button_list/$' % settings.V_URL_BASE, views.test_button_list),
    url(r'^test_update_province/$', views.test_update_province),
    url(r'^unit_change_list/$', views.unit_change_list),
    url(r'^mark_dynamic_change_form/(?P<app_label>.*)/(?P<model_name>.*)/$', views.mark_dynamic_change_form),
    url(r'^bing_mark/$', views.bing_mark),
    url(r'^unbing_mark/$', views.unbing_mark),
    url(r'^code_view/$', views.code_view),
    url(r'^repair_total_view/$', views.repair_total_view),
    url(r'^repair_view/$', views.repair_view),
    url(r'^repair_order_desc_view/$', views.repair_order_desc_view),
    url(r'^test_widget/$', views.test_widget),
    url(r'^test_file_manager/$', views.test_file_manager),
    url(r'^test_template_2_vadmin/$', views.test_template_2_vadmin),
    # url(r'^test_word_2_vadmin/$', views.test_word_2_vadmin),
    url(r'^%stest_swipe/$' % settings.V_URL_BASE, views.test_swipe),
    url(r'^%stest_carousel/$' % settings.V_URL_BASE, views.test_carousel),
    url(r'^%stest_tabs/$' % settings.V_URL_BASE, views.test_tabs),
    url(r'^%stest_timeline/$' % settings.V_URL_BASE, views.test_timeline),
    url(r'^%stest_collapse/$' % settings.V_URL_BASE, views.test_collapse),
    # url(r'^v_upload_file/$', views.v_upload_file),
    url(r'^update_code_view/(?P<file_path>.*)/$', views.update_code_view),
    url(r'^%sword_view/$' % settings.V_URL_BASE, views.word_view),
    # url(r'^zcgl_view/', zcgl_views.zcgl_view),
]

# 第2个静态目录
urlpatterns += [
    url(r'^vadmin/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'vadmin'), }),
]

# urlpatterns += [
#     url(r'^static_vue/(?P<path>.*)$', serve, {'document_root': os.path.join(settings.BASE_DIR, 'static_vue'), }),
# ]

urlpatterns += (
    url(r'^favicon.ico$', RedirectView.as_view(url=r'static/favicon.ico')),
)


urlpatterns += staticfiles_urlpatterns()
if settings.DEBUG:
    from django.views.static import serve

    urlpatterns += [
        url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
    ]

    # import debug_toolbar
    #
    # urlpatterns += [
    #     url(r'^__debug__/', include(debug_toolbar.urls)),
    # ]
