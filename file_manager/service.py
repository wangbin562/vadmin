# !/usr/bin/python
# -*- coding=utf-8 -*-

import logging
import os
import shutil

from django.conf import settings

from vadmin import step

logger = logging.getLogger(__name__)


def add_dir(request):
    base_url = request.GET["base_url"]
    dir = request.GET["dir"]
    # lst_dir = dir.split("/")

    base_path = os.path.join(settings.MEDIA_ROOT, base_url)
    path = os.path.join(base_path, dir)
    path = os.path.abspath(path)
    if os.path.exists(path):
        return step.Msg(text="路径已存在！")

    try:
        os.makedirs(path)
    except BaseException as e:
        return step.Msg(text=str(e.args))

    return step.OperaSuccess()


def update(request):
    base_url = request.GET["base_url"]
    dir = request.GET["dir"]
    new_name = request.GET["new_name"]

    base_path = os.path.join(settings.MEDIA_ROOT, base_url)
    old_path = os.path.abspath(os.path.join(base_path, dir))
    new_path = os.path.join(os.path.split(old_path)[0], new_name)
    if os.path.exists(new_path):
        return step.Msg(text="修改后的名称已存在！")

    try:
        os.rename(old_path, new_path)
    except BaseException as e:
        return step.Msg(text=str(e.args))

    return step.OperaSuccess()


def upload_file(request):
    base_url = request.GET["base_url"]
    dir = request.GET.get("dir", "")
    base_path = os.path.join(settings.MEDIA_ROOT, base_url)
    path = os.path.abspath(os.path.join(base_path, dir))
    o_file = request.FILES["file"]
    file_name = o_file.name
    file_path = os.path.abspath(os.path.join(path, file_name))
    name, suffix = os.path.splitext(o_file.name)

    try:
        count = 1
        while True:
            if os.path.exists(file_path):
                file_name = "%s（%s）%s" % (name, count, suffix)
                file_path = os.path.abspath(os.path.join(path, file_name))
                count += 1
            else:
                break

        f = open(file_path, 'wb')
        for chunk in o_file.chunks():
            f.write(chunk)
        f.close()
    except BaseException as e:
        return step.Msg(text=str(e.args))

    return file_name


def search(request):
    import time
    from django.conf import settings
    base_url = request.GET["base_url"]
    dir = request.GET.get("dir", "")
    key = request.GET.get("key", "").lower()
    base_path = os.path.join(settings.MEDIA_ROOT, base_url, dir)

    def add_item(path, children):
        last_time = None
        for name in os.listdir(path):
            if key not in name.lower():
                continue

            path_name = os.path.join(path, name)
            if os.path.isfile(path_name):
                size = os.path.getsize(path_name)
                mtime = os.stat(path_name).st_mtime
                update_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
                if last_time is None or update_time > last_time:
                    last_time = update_time
                children.append({"name": name, "size": size, "date": update_time})
            else:
                sub = []
                last_time = add_item(path_name, sub)
                children.append({"name": name, "children": sub, "date": last_time})
        return last_time

    data = []
    add_item(base_path, data)
    return data


def download(request):
    """单个和批量下载"""
    base_url = request.GET["base_url"]
    dir = request.GET.get("dir", "")
    base_path = os.path.join(settings.MEDIA_ROOT, base_url)
    path = os.path.join(base_path, dir)
    if os.path.isdir(path):
        # 压缩下载
        pass

    return os.path.abspath(os.path.join(base_url, dir))


def delete(request):
    base_url = request.GET["base_url"]
    dir = request.GET["dir"]
    base_path = os.path.join(settings.MEDIA_ROOT, base_url)
    path = os.path.join(base_path, dir)
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return step.Msg(text="路径不存在！")

    try:
        if os.path.isfile(path):
            os.remove(path)
        else:
            shutil.rmtree(path)

    except BaseException as e:
        return step.Msg(text=str(e.args))

    return step.OperaSuccess()


def preview(request):
    """预览"""
    base_url = request.GET["base_url"]
    dir = request.GET["dir"]
