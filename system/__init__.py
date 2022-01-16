# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
1.0.1
1、支持padding计算功能
2、修改相关bug
3、增加自定义模板功能

1.0.2
1、增加一个model定义多个左边菜单功能
2、增加tabs功能
3、增加子表可以在字段中间显示功能
4、增加menu、button、tabs支持图片功能
5、自定义模板中增加自定义头部功能
6、增加自定义chang_list功能
7、修改相关bug
8、增加外键过滤（v_foreign_key_filter接口，可以重载）
9、增加v_change_list_config配置

1.0.3
1、增加Badge组件
2、增加文件组件多文件上传功能
3、增加关闭弹出层步骤

1.0.4
1、增加航道局案例模板
2、增加table固定列
3、修改部分bug
4、增加menu显示图片
5、增加查询条件内批量导出

1.0.5
1、修改部分BUG
2、主页显示对齐
3、菜单文件颜色（根据背景色自动计算黑色或白色文字颜色）
4、自定义搜索框提示信息
5、增加Inline字段v_change_list_config配置
6、v_change_list_config配置优化，列使用field名称
7、增加change_list自定义列名称
8、自定义常用组件
9、菜单使用model时，没有定义label，自动使用model名称

1.0.6
1、增加富文本编辑器（rich组件）
2、文件字段支持多文件定义
3、子表子段自定义
4、自定义样式（style参数）
5、修改部分bug
6、select组件增加本地过滤,filter参数

1.0.7
1、修改相关bug
2、多个过滤项换行显示
3、增加UEditorField、ColorField自定义字段
4、修改保存调用save_model函数

1.0.8
1、修改部分bug
2、优化显示效果

1.0.9
1、修改部分bug
2、增加change_list中显示外键字段,增加list_v_display配置
3、在没有配置fieldsets情况下，支持inlines，匹配django配置
4、增加inline自定义字段样式
5、增加CheckboxField， SelectField自定义字段

1.10.0
1、修改部分bug

1.10.1
1、修改部分bug
2、优化代码

1.10.2
1、增加CharCheckField、ImitateForeignKey两个自定义字段
2、修改部分bug

1.10.3
1、修改浏览器兼容问题
2、修改部分bug

1.10.4
1、权限管理
2、bug修改
3、增加悬浮功能
4、增加menu组件横向显示
5、增加模拟外键字段使用self

1.10.5
1、增加匹配字符串主键
2、修改bug
3、增加Decimal字段小数位数判断
4、增加char最大长度判断

1.10.6
1、增加折叠面板（Collapse）
2、图片管理器，图片统一管理(使用ImageManagerField字段）
3、增加事件select组件change事件
4、增加keydown事件（目前只支持input组件，登录界面已修改)
5、增加树形权限控制
6、panel增加border_color属性
7、可以自定义一级url，如:vadmin修改成admin（配置V_BASE_URL）
8、增加保存前调用函数v_save_before， 保存后调用函数v_save_after，增加自定返回总提示信息
9、增加自定义菜单模板样式
10、增加用户表修改用户密码功能
11、增加自定义删除页面、自定义用户增加页面、自定义菜单
12、增加过滤器级联功能（使用SelectCascadeFilterField字段或自定义）
13、菜单实现完整刷新或区域刷新（自动完成，不需要配置）
14、修改list_v_display 两级显示choice值或对应外键obj值
15、修改左边菜单显示隐藏
16、保存界面和新增界面不是同一个模板，不支持"保存并复制增加一个"
17、登录页面重写方式
18、增加部分功能操作
19、修改部分BUG
20、新增一套界面样式（style_sleek）
21、支持upload使用时间格式生成路径（upload_to='images/%Y-%m-%d'）

1.10.7
1、增加margin属性
2、修改upload、rich上传接口可以自定义
3、修改panel悬浮方式，窗口内不需要滑动
4、修改widget_update步骤，增加update_method参数(局部更新还是全量更新）
5、修改超级管理员，第一次没有权限的BUG
6、修改ie兼容性问题(部分，前端还需要继续优化)
7、增加树修改(拖动排序功能没有完成）
8、修改弹出窗样式
9、form保存后动态更新，不再通过url查询
10、修改部分bug
11、新建的obj不初始化, 自定义字段不用判断obj.pk is None，而是判断obj is None

1.10.8
2、增加工作流
4、案例代码清理，说明常用功能案例代码出处
11、Timeline 时间轴 支持显示图例，支持step
12、增加一套表格样式
16、排序使用model处理，不使用sql语句，兼容不同的数据库
9、表格增加纵向显示
13、增加枚举字典
14、增加APP下载更新配置

1.10.9
1、增加动态操作
20、案例代码清理，说明常用功能案例代码出处
21、增加多套样式模板
"""

VERSION = '1.10.7'


def init_vadmin_settings():
    import vadmin.settings as vadmin_settings
    from django.conf import settings as django_settings

    for key in dir(vadmin_settings):
        if key.find("V_") == 0 and not hasattr(django_settings, key):
            setattr(django_settings, key, getattr(vadmin_settings, key))


init_vadmin_settings()
