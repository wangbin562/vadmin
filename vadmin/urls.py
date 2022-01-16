# !/usr/bin/python
# -*- coding=utf-8 -*-

from django.conf.urls import url
from vadmin import views


urlpatterns = [
    url(r'^$', views.v_index),
    url(r'^v_index_view/$', views.v_index_view),
    url(r'^v_login/$', views.v_login),
    url(r'^v_logout/$', views.v_logout),
    url(r'^v_update_pwd/$', views.v_update_pwd),
    url(r'^v_update_pwd_other_user/$', views.v_update_pwd_other_user),
    # url(r'^v_menu_list/$', views.v_menu_list),
    url(r'^v_theme_view/$', views.v_theme_view),
    url(r'^v_theme_submit/$', views.v_theme_submit),
    url(r'^v_license_change/$', views.v_license_change),
    url(r'^v_home_view/$', views.v_home_view),
    # url(r'^v_home_add_common_view/$', views.v_home_add_common_view),
    # url(r'^v_home_add_common_submit/$', views.v_home_add_common_submit),
    # url(r'^v_user_add_view/$', views.v_user_add_view),
    # url(r'^v_user_add/$', views.v_user_add),
    url(r'^v_select_search/$', views.v_select_search),
    # url(r'^v_input_search/((?P<app_label>.*)/(?P<model_name>.*)/(?P<search_field>.*))/$',
    #     views.v_input_search),
    url(r'^v_upload_file_by_model/(?P<app_label>.*)/(?P<model_name>.*)/(?P<field_name>.*)/$',
        views.v_upload_file_by_model),
    # url(r'^v_upload_ueditor/(?P<app_label>.*)/(?P<model_name>.*)/(?P<field_name>.*)/$', views.v_upload_ueditor),
    url(r'^v_upload_file/(?P<callback>.*)/', views.v_upload_file),
    url(r'^v_upload_file/', views.v_upload_file),

    url(r'^v_update_file_resume/(?P<callback>.*)/', views.v_update_file_resume),
    url(r'^v_update_file_resume/', views.v_update_file_resume),
    url(r'^v_word/', views.v_word),
    url(r'^v_word_template/', views.v_word_template),
    url(r'^v_word_template_save/', views.v_word_template_save),
    url(r'^v_word_info/', views.v_word_info),
    url(r'^v_generate_file_id/', views.v_generate_file_id),
    url(r'^v_get_word_url/', views.v_get_word_url),
    url(r'^v_export_word/', views.v_export_word),
    url(r'^v_document_2_page/', views.v_document_2_page),
    url(r'^v_import_word/', views.v_import_word),
    # url(r'^v_export_excel/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_export_excel),
    url(r'^v_home/$', views.v_home),
    url(r'^v_top/$', views.v_top),
    url(r'^v_left/$', views.v_left),
    url(r'^v_right/$', views.v_right),
    url(r'^v_list/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list),
    url(r'^v_list_popup/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_popup),
    url(r'^v_list_filter/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_filter),

    # url(r'^v_change_list_no_left_menu/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_change_list_no_left_menu),
    # url(r'^v_change_list_href/$', views.v_change_list_href),
    url(r'^v_list_save/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_save),
    url(r'^v_list_del_view/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_del_view),
    url(r'^v_list_del/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_del),
    url(r'^v_list_order/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_order),
    url(r'^v_list_export/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_export),
    url(r'^v_list_export_async/$', views.v_list_export_async),
    # url(r'^v_change_list_opera/(?P<app_label>.*)/(?P<model_name>.*)/(?P<action_name>.*)/$', views.v_change_list_opera),
    # url(r'^v_change_list_loading/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_change_list_loading),  # 加载更多
    url(r'^v_list_select_close/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_select_close),  # 弹出选择
    url(r'^v_list_delete_close/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_delete_close),  # 弹出提示框删除
    url(r'^v_list_row_save/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_list_row_save),
    url(r'^v_list_tree_load/(?P<app_label>.*)/(?P<model_name>.*)/(?P<parent_field>.*)/$', views.v_list_tree_load),

    url(r'^v_form/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form),
    url(r'^v_form_popup/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_popup),
    url(r'^v_form_child_popup/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_child_popup),
    # url(r'^v_form_save_edit/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_save_edit),
    url(r'^v_form_add/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_add),
    url(r'^v_form_copy_add/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_add),
    url(r'^v_form_save/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_save),
    url(r'^v_form_save_edit/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_save_edit),
    url(r'^v_form_save_close/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_save_close),
    # url(r'^v_change_form_close/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_change_form_close),
    url(r'^v_form_save_add/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_save_add),
    # url(r'^v_change_form_save_copy_add/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_change_form_save_copy_add),
    url(r'^v_form_del_view/(?P<app_label>.*)/(?P<model_name>.*)/$', views.v_form_del_view),
    # url(r'^v_form_del/(?P<app_label>.*)/(?P<model_name>.*)/(?P<object_id>.*)/$', views.v_form_del),
    url(r'^v_form_field_change/(?P<app_label>.*)/(?P<model_name>.*)/(?P<field_name>.*)/$', views.v_form_field_change),

    # url(r'^v_change_inline_save/(?P<app_label>.*)/(?P<model_name>.*)/(?P<inline_name>.*)/$', views.v_change_inline_save),
    url(r'^v_inline_del/(?P<app_label>.*)/(?P<model_name>.*)/(?P<related_app_label>.*)/(?P<related_model_name>.*)/$',
        views.v_inline_del),
    # url(r'^v_home_add_common_edit_submit/$', views.v_home_add_common_edit_submit),
    # url(r'^v_select_change_filter/(?P<object_id>.*)/(?P<model_name>.*)/$', views.v_select_change_filter),

    # url(r'^v_image_search/(?P<page_index>.*)/(?P<search_term>.*)/(?P<type>.*)/$', views.v_image_search),
    # url(r'^v_image_search/(?P<page_index>.*)/(?P<search_term>.*)/$', views.v_image_search),
    # url(r'^v_image_search/(?P<page_index>.*)/$', views.v_image_search),
    # url(r'^v_image_search/$', views.v_image_search),
    # url(r'^v_image_select/(?P<field_name>.*)/(?P<object_id>.*)/$', views.v_image_select),
    url(r'^v_tree_opera/(?P<app_label>.*)/(?P<model_name>.*)/(?P<field_name>.*)/$',
        views.v_tree_opera),
    #
    # url(r'^v_report/(?P<interface>.*)/$', views.v_report),  # 自定义报表统一接口
    # url(r'^v_report_export/(?P<interface>.*)/$', views.v_report_export),  # 自定义报表导出
    url(r'^v_run/(?P<script>.*)$', views.v_run_script),  # 执行python脚本，返回步骤
    # url(r'^v_go_home/', views.v_go_home),
    # url(r'^v_app_home/', views.v_go_home),
    # url(r'^!', views.v_index),
]

# for model, model_admin in admin.site._registry.items():
#     urlpatterns += [
#         url(r'^%s/%s/' % (model._meta.app_label, model._meta.model_name), v_change_list),
#         url(r'^%s/%s/id/' % (model._meta.app_label, model._meta.model_name), v_change_from)
#     ]

# if django.VERSION[:2] < (1, 8):
#     from django.conf.urls import patterns

# urlpatterns = patterns('', *urlpatterns)
