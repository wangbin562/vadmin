# !/usr/bin/python
# -*- coding=utf-8 -*-
"""
ueditor模板 支持百度的富文本编辑器
"""
import datetime
import random
import os
import urllib.request
from django.conf import settings

# 工具栏样式，可以添加任意多的模式
TOOLBARS_SETTINGS = {
    "besttome": [
        ['source', 'undo', 'redo', 'bold', 'italic', 'underline', 'forecolor', 'backcolor', 'superscript', 'subscript', "justifyleft",
         "justifycenter", "justifyright", "insertorderedlist", "insertunorderedlist", "blockquote", 'formatmatch', "removeformat",
         'autotypeset', 'inserttable', "pasteplain", "wordimage", "searchreplace", "map", "preview", "fullscreen"],
        ['insertcode', 'paragraph', "fontfamily", "fontsize", 'link', 'unlink', 'insertimage', 'insertvideo', 'attachment', 'emotion',
         "date", "time"]],
    "mini": [
        ['source', '|', 'undo', 'redo', '|', 'bold', 'italic', 'underline', 'formatmatch', 'autotypeset', '|', 'forecolor', 'backcolor',
         '|', 'link', 'unlink', '|', 'simpleupload', 'attachment']],
    "normal": [
        ['source', '|', 'undo', 'redo', '|', 'bold', 'italic', 'underline', 'removeformat', 'formatmatch', 'autotypeset', '|', 'forecolor',
         'backcolor', '|', 'link', 'unlink', '|', 'simpleupload', 'emotion', 'attachment', '|', 'inserttable', 'deletetable',
         'insertparagraphbeforetable', 'insertrow', 'deleterow', 'insertcol', 'deletecol', 'mergecells', 'mergeright', 'mergedown',
         'splittocells', 'splittorows', 'splittocols']]
}

# 默认的Ueditor设置，请参见ueditor.config.js
UEditorSettings = {
    "toolbars": TOOLBARS_SETTINGS["normal"],
    "autoFloatEnabled": False,
    "defaultPathFormat": "%(basename)s_%(datetime)s_%(rnd)s.%(extname)s"  # 默认保存上传文件的命名方式
}
# 请参阅php文件夹里面的config.json进行配置
UEditorUploadSettings = {
    # 上传图片配置项
    "imageActionName": "uploadimage",  # 执行上传图片的action名称
    "imageMaxSize": 10485760,  # 上传大小限制，单位B,10M
    "imageFieldName": "upfile",  # * 提交的图片表单名称 */
    "imageUrlPrefix": "",
    "imagePathFormat": "",
    "imageAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # 上传图片格式显示

    # 涂鸦图片上传配置项 */
    "scrawlActionName": "uploadscrawl",  # 执行上传涂鸦的action名称 */
    "scrawlFieldName": "upfile",  # 提交的图片表单名称 */
    "scrawlMaxSize": 10485760,  # 上传大小限制，单位B  10M
    "scrawlUrlPrefix": "",
    "scrawlPathFormat": "",

    # 截图工具上传 */
    "snapscreenActionName": "uploadimage",  # 执行上传截图的action名称 */
    "snapscreenPathFormat": "",
    "snapscreenUrlPrefix": "",

    # 抓取远程图片配置 */
    "catcherLocalDomain": ["127.0.0.1", "localhost", "img.baidu.com"],
    "catcherPathFormat": "",
    "catcherActionName": "catchimage",  # 执行抓取远程图片的action名称 */
    "catcherFieldName": "source",  # 提交的图片列表表单名称 */
    "catcherMaxSize": 10485760,  # 上传大小限制，单位B */
    "catcherAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # 抓取图片格式显示 */
    "catcherUrlPrefix": "",
    # 上传视频配置 */
    "videoActionName": "uploadvideo",  # 执行上传视频的action名称 */
    "videoPathFormat": "",
    "videoFieldName": "upfile",  # 提交的视频表单名称 */
    "videoMaxSize": 102400000,  # 上传大小限制，单位B，默认100MB */
    "videoUrlPrefix": "",
    "videoAllowFiles": [
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid"],  # 上传视频格式显示 */

    # 上传文件配置 */
    "fileActionName": "uploadfile",  # controller里,执行上传视频的action名称 */
    "filePathFormat": "",
    "fileFieldName": "upfile",  # 提交的文件表单名称 */
    "fileMaxSize": 204800000,  # 上传大小限制，单位B，200MB */
    "fileUrlPrefix": "",  # 文件访问路径前缀 */
    "fileAllowFiles": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp",
        ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
        ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml", ".py", ".conf", ".bat"
    ],  # 上传文件格式显示 */

    # 列出指定目录下的图片 */
    "imageManagerActionName": "listimage",  # 执行图片管理的action名称 */
    "imageManagerListPath": "",
    "imageManagerListSize": 30,  # 每次列出文件数量 */
    "imageManagerAllowFiles": [".png", ".jpg", ".jpeg", ".gif", ".bmp"],  # 列出的文件类型 */
    "imageManagerUrlPrefix": "",  # 图片访问路径前缀 */

    # 列出指定目录下的文件 */
    "fileManagerActionName": "listfile",  # 执行文件管理的action名称 */
    "fileManagerListPath": "",
    "fileManagerUrlPrefix": "",
    "fileManagerListSize": 30,  # 每次列出文件数量 */
    "fileManagerAllowFiles": [
        ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tif", ".psd"
                                                         ".flv", ".swf", ".mkv", ".avi", ".rm", ".rmvb", ".mpeg", ".mpg",
        ".ogg", ".ogv", ".mov", ".wmv", ".mp4", ".webm", ".mp3", ".wav", ".mid",
        ".rar", ".zip", ".tar", ".gz", ".7z", ".bz2", ".cab", ".iso",
        ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".pdf", ".txt", ".md", ".xml",
        ".exe", ".com", ".dll", ".msi"
    ]  # 列出的文件类型 */
}


class FileSize(object):
    """
    # 文件大小类
    """
    SIZE_UNIT = {"Byte": 1, "KB": 1024, "MB": 1048576, "GB": 1073741824, "TB": 1099511627776}

    def __init__(self, size):
        self.size = int(FileSize.format(size))

    @staticmethod
    def format(size):
        import re
        if isinstance(size, int):
            return size
        else:
            if not isinstance(size, str):
                return 0
            else:
                o_size = size.lstrip().upper().replace(" ", "")
                pattern = re.compile(r"(\d*\.?(?=\d)\d*)(byte|kb|mb|gb|tb)", re.I)
                match = pattern.match(o_size)
                if match:
                    m_size, m_unit = match.groups()
                    if m_size.find(".") == -1:
                        m_size = int(m_size)
                    else:
                        m_size = float(m_size)
                    if m_unit != "BYTE":
                        return m_size * FileSize.SIZE_UNIT[m_unit]
                    else:
                        return m_size
                else:
                    return 0

    # # 返回字节为单位的值
    # @property
    # def size(self):
    #     return self.size
    #
    # @size.setter
    # def size(self, new_size):
    #     try:
    #         self.size = int(new_size)
    #     except (BaseException,):
    #         self.size = 0

    # 返回带单位的自动值
    @property
    def friend_value(self):
        if self.size < FileSize.SIZE_UNIT["KB"]:
            unit = "Byte"
        elif self.size < FileSize.SIZE_UNIT["MB"]:
            unit = "KB"
        elif self.size < FileSize.SIZE_UNIT["GB"]:
            unit = "MB"
        elif self.size < FileSize.SIZE_UNIT["TB"]:
            unit = "GB"
        else:
            unit = "TB"

        if (self.size % FileSize.SIZE_UNIT[unit]) == 0:
            return "%s%s" % ((self.size / FileSize.SIZE_UNIT[unit]), unit)
        else:
            return "%0.2f%s" % (round(float(self.size) / float(FileSize.SIZE_UNIT[unit]), 2), unit)

    def __str__(self):
        return self.friend_value

    # 相加
    def __add__(self, other):
        if isinstance(other, FileSize):
            return FileSize(other.size + self.size)
        else:
            return FileSize(FileSize(other).size + self.size)

    def __sub__(self, other):
        if isinstance(other, FileSize):
            return FileSize(self.size - other.size)
        else:
            return FileSize(self.size - FileSize(other).size)

    def __gt__(self, other):
        if isinstance(other, FileSize):
            if self.size > other.size:
                return True
            else:
                return False
        else:
            if self.size > FileSize(other).size:
                return True
            else:
                return False

    def __lt__(self, other):
        if isinstance(other, FileSize):
            if other.size > self.size:
                return True
            else:
                return False
        else:
            if FileSize(other).size > self.size:
                return True
            else:
                return False

    def __ge__(self, other):
        if isinstance(other, FileSize):
            if self.size >= other.size:
                return True
            else:
                return False
        else:
            if self.size >= FileSize(other).size:
                return True
            else:
                return False

    def __le__(self, other):
        if isinstance(other, FileSize):
            if other.size >= self.size:
                return True
            else:
                return False
        else:
            if FileSize(other).size >= self.size:
                return True
            else:
                return False


def get_ueditor_settings(request):
    return UEditorUploadSettings


def get_output_path(request, path_format, path_format_var):
    # 取得输出文件的路径
    output_path_format = (request.GET.get(path_format, UEditorSettings["defaultPathFormat"]) % path_format_var).replace("\\", "/")
    # 分解OutputPathFormat
    output_path, output_file = os.path.split(output_path_format)
    now = datetime.datetime.now()
    output_path = os.path.join(settings.MEDIA_ROOT, "%04d%02d%02d" % (now.year, now.month, now.day), output_path)
    if not output_file:  # 如果OutputFile为空说明传入的OutputPathFormat没有包含文件名，因此需要用默认的文件名
        output_file = UEditorSettings["defaultPathFormat"] % path_format_var
        output_path_format = os.path.join(output_path_format, output_file)
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    return [output_path_format, output_path, output_file]


def catcher_remote_image(request):
    """远程抓图，当catchRemoteImageEnable:true时，
        如果前端插入图片地址与当前web不在同一个域，则由本函数从远程下载图片到本地
    """
    # state = "SUCCESS"

    allow_type = list(request.GET.get("catcherAllowFiles", UEditorUploadSettings.get("catcherAllowFiles", "")))
    # max_size = int(request.GET.get("catcherMaxSize", UEditorUploadSettings.get("catcherMaxSize", 0)))

    remote_urls = request.POST.getlist("source[]", [])
    catcher_infos = []
    path_format_var = {
        "time": datetime.datetime.now().strftime("%H%M%S"),
        "date": datetime.datetime.now().strftime("%Y%m%d"),
        "datetime": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "rnd": random.randrange(100, 999)
    }
    for remote_url in remote_urls:
        # 取得上传的文件的原始名称
        remote_file_name = os.path.basename(remote_url)
        remote_original_name, remote_original_ext = os.path.splitext(remote_file_name)
        # 文件类型检验
        if remote_original_ext in allow_type:
            path_format_var.update({
                "basename": remote_original_name,
                "extname": remote_original_ext[1:],
                "filename": remote_original_name
            })
            # 计算保存的文件名
            o_path_format, o_path, o_file = get_output_path(request, "catcherPathFormat", path_format_var)
            o_filename = os.path.join(o_path, o_file).replace("\\", "/")
            # 读取远程图片文件
            try:
                remote_image = urllib.request.urlopen(remote_url)
                # 将抓取到的文件写入文件
                try:
                    f = open(o_filename, 'wb')
                    f.write(remote_image.read())
                    f.close()
                    state = "SUCCESS"
                except (BaseException,):
                    state = u"写入抓取图片文件错误!"

            except (BaseException,):
                state = u"抓取图片错误!"

            now = datetime.datetime.now()
            catcher_infos.append({
                "state": state,
                "url": settings.MEDIA_URL + "%04d%02d%02d/" % (now.year, now.month, now.day) + o_path_format,
                "size": os.path.getsize(o_filename),
                "title": os.path.basename(o_file),
                "original": remote_file_name,
                "source": remote_url
            })

    return_info = {
        "state": "SUCCESS" if len(catcher_infos) > 0 else "ERROR",
        "list": catcher_infos
    }

    return return_info


def save_scrawl_file(request, filename):
    import base64
    try:
        content = request.POST.get(UEditorUploadSettings.get("scrawlFieldName", "upfile"))
        f = open(filename, 'wb')
        f.write(base64.b64decode(content))
        f.close()
        state = "SUCCESS"
    except (BaseException,):
        state = "写入图片文件错误!"
    return state


# 保存上传的文件
def save_upload_file(post_file, file_path):
    f = None
    try:
        f = open(file_path, 'wb')
        for chunk in post_file.chunks():
            f.write(chunk)
    except (BaseException,):
        if f:
            f.close()
        return u"写入文件错误!"

    if f:
        f.close()
    return u"SUCCESS"


def upload_file(request):
    """上传文件"""

    state = "SUCCESS"
    action = request.GET.get("action")
    # 上传文件
    upload_field_name = {
        "uploadfile": "fileFieldName", "uploadimage": "imageFieldName",
        "uploadscrawl": "scrawlFieldName", "catchimage": "catcherFieldName",
        "uploadvideo": "videoFieldName",
    }

    # 上传涂鸦，涂鸦是采用base64编码上传的，需要单独处理
    file = None
    if action == "uploadscrawl":
        upload_file_name = "scrawl.png"
        upload_file_size = 0
    else:
        # 取得上传的文件
        field_name = request.GET.get(upload_field_name[action], UEditorUploadSettings.get(action, "upfile"))
        file = request.FILES.get(field_name, None)
        if file is None:
            return u"{'state:'ERROR'}"

        upload_file_name = file.name
        upload_file_size = file.size

    # 取得上传的文件的原始名称
    upload_original_name, upload_original_ext = os.path.splitext(upload_file_name)

    # 文件类型检验
    upload_allow_type = {
        "uploadfile": "fileAllowFiles",
        "uploadimage": "imageAllowFiles",
        "uploadvideo": "videoAllowFiles"
    }
    if action in upload_allow_type:
        allow_type = list(request.GET.get(upload_allow_type[action], UEditorUploadSettings.get(upload_allow_type[action], "")))
        if upload_original_ext not in allow_type:
            state = u"服务器不允许上传%s类型的文件。" % upload_original_ext

    # 大小检验
    upload_max_size = {
        "uploadfile": "filwMaxSize",
        "uploadimage": "imageMaxSize",
        "uploadscrawl": "scrawlMaxSize",
        "uploadvideo": "videoMaxSize"
    }
    max_size = int(request.GET.get(upload_max_size[action], UEditorUploadSettings.get(upload_max_size[action], 0)))
    if max_size != 0:
        o_file_size = FileSize(max_size)
        if upload_file_size > o_file_size.size:
            state = u"上传文件大小不允许超过%s。" % o_file_size.friend_value

    # 检测保存路径是否存在,如果不存在则需要创建
    upload_path_format = {
        "uploadfile": "filePathFormat",
        "uploadimage": "imagePathFormat",
        "uploadscrawl": "scrawlPathFormat",
        "uploadvideo": "videoPathFormat"
    }

    path_format_var = {
        "basename": upload_original_name,
        "extname": upload_original_ext[1:],
        "filename": upload_file_name,
        "time": datetime.datetime.now().strftime("%H%M%S"),
        "datetime": datetime.datetime.now().strftime("%Y%m%d%H%M%S"),
        "rnd": random.randrange(100, 999)
    }
    # 取得输出文件的路径
    output_path_format, output_path, output_file = get_output_path(request, upload_path_format[action], path_format_var)

    # 所有检测完成后写入文件
    if state == "SUCCESS":
        if action == "uploadscrawl":
            state = save_scrawl_file(request, os.path.join(output_path, output_file))
        else:
            # 保存到文件中，如果保存错误，需要返回ERROR
            state = save_upload_file(file, os.path.join(output_path, output_file))

    # 返回数据
    now = datetime.datetime.now()
    return_info = {
        'url': settings.MEDIA_URL + "%04d%02d%02d/" % (now.year, now.month, now.day) + output_path_format,  # 保存后的文件名称
        'original': upload_file_name,  # 原始文件名
        'type': upload_original_ext,
        'state': state,  # 上传状态，成功时返回SUCCESS,其他任何值将原样返回至图片上传框中
        'size': upload_file_size
    }
    return return_info
