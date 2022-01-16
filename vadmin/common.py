# !/usr/bin/python
# -*- coding=utf-8 -*-
# import ctypes
import base64
import random
import time
import hashlib
import os
import datetime
from ctypes import *
from urllib import parse
from platform import platform

if 'windows' in platform().lower():
    lib = CDLL('./vadmin/vadmin_api_win.so')
elif "mac" in platform().lower():
    lib = CDLL('./vadmin/vadmin_api_mac.so')
else:
    lib = CDLL('./vadmin/vadmin_api.so')


# class StrPointer(Structure):
#     _fields_ = [("p", c_char_p), ("n", c_longlong)]
#
#
# def go_make_url():
#     make_url = lib.make_url
#     make_url.argtypes = [ctypes.c_wchar_p, ]
#     make_url.restype = StrPointer
#     str = make_url('aa')
#     print(str.p[:str.n])
#
#
# def get_list(area_code):
#     parsecode = lib.make_url
#     parsecode.argtype = ctypes.c_char_p
#     parsecode.restype = ctypes.c_char_p
#     result = lib.parsecode(area_code.encode("utf-8"))
#     return result.decode("utf-8").split(",")

class Map(Structure):
    _fields_ = [
        ("k", c_char_p),
        ("v", c_char_p)
    ]


def translate_map(dict_param):
    lst_map = []
    for k, v in dict_param.items():
        obj = Map(c_char_p(str(k).encode("utf-8")), c_char_p(str(v).encode("utf-8")))
        lst_map.append(pointer(obj))

    return lst_map


def translate_list(lst_param):
    lst = []
    for v in lst_param:
        lst.append(c_char_p(str(v).encode("utf-8")))

    return lst


def translate_param_2_c(**kwargs):
    lst_param = []
    for k, v in kwargs.items():
        if isinstance(v, (tuple, list)):
            v = translate_list(v)
            v_len = len(v)
            lst_param.extend(((c_char_p * v_len)(*v), v_len))
        elif isinstance(v, dict):
            v = translate_map(v)
            v_len = len(v)
            lst_param.extend(((type(pointer(Map())) * v_len)(*v), v_len))
        elif isinstance(v, str):
            lst_param.append(c_char_p(v.encode("utf-8")))

    return lst_param


def translate_param(**kwargs):
    lst_param = []
    for k, v in kwargs.items():
        if isinstance(v, (tuple, list)):
            p = c_char_p(str(v or []).replace("'", '"').encode("utf-8"))
            lst_param.append(p)
        elif isinstance(v, dict):
            p = c_char_p(str(v or {}).replace("'", '"').encode("utf-8"))
            lst_param.append(p)
        elif isinstance(v, str):
            lst_param.append(c_char_p(v.encode("utf-8")))

    return lst_param


# 不要使用，太慢
# def call_golang(method_name, **kwargs):
#     p = translate_param(**kwargs)
#
#     lst_cmd = ["lib.%s" % method_name.__name__, "("]
#     for i in range(0, len(p)):
#         lst_cmd.append("p[%s]," % i)
#
#     lst_cmd.append(")")
#     cmd = "".join(lst_cmd)
#     r = eval(cmd)
#     return r


# def make_url(url, request=None, param=None, filter=None, only=None):
#     request_param = {}
#     for k, v in request.GET.items():
#         request_param[k] = v
#
#     make_url = lib.make_url
#     make_url.restype = c_char_p
#     p = translate_param(url=url, request_param=request_param,
#                         param=param or {}, filter=filter or [], only=only or [])
#
#     r = make_url(p[0], p[1], p[2], p[3], p[4])
#     return r.decode("utf-8")

def make_url(url, request=None, param=None, filter=None, only=None):
    """
    构造url
    param > request > url
    """
    if not url:
        return None

    param = param or {}
    filter = filter or []
    only = only or []

    dict_para = dict()
    if "?" in url:
        url_path, url_param = url.split("?", 1)
        dict_para = dict([item.split("=", 1) for item in url_param.split("&")])
    else:
        url_path = url

    if request:
        for k, v in request.GET.items():
            if k not in dict_para:
                dict_para[k] = v

    if param:
        dict_para.update(param)

    # 删除不增加的
    add_para = {}
    if only:
        for k, v in dict_para.items():
            if k not in only:
                continue

            if v is None:
                v = ""

            add_para[k] = "%s=%s" % (k, v)

    elif filter:
        for k, v in dict_para.items():
            if k in filter:
                continue

            if v is None:
                v = ""

            add_para[k] = "%s=%s" % (k, v)
    else:
        for k, v in dict_para.items():
            if v is None:
                v = ""

            add_para[k] = "%s=%s" % (k, v)

    if add_para:
        new_url = url_path.rstrip("/\\") + "/?" + "&".join(add_para.values())
    else:
        new_url = url_path
    return new_url


def make_request_url(request, param=None, filter=None):
    param = param or {}
    filter = filter or []

    # if url_para:
    #     for sig_para in url_para.split("&"):
    #         k, v = sig_para.split("=", 1)
    #         dict_para[k] = v

    mutable = request.GET._mutable
    request.GET._mutable = True

    if param:
        request.GET.update(param)

    for k in filter:
        if k in request.GET:
            del request.GET[k]

    lst_para = list()
    for k, v in request.GET.items():
        lst_para.append("%s=%s" % (k, v))

    request.META['QUERY_STRING'] = "&".join(lst_para)
    request.GET._mutable = mutable


def parse_url_param(url):
    dict_param = {}
    if "?" in url:
        url_path, url_param = url.split("?", 1)
        dict_param = dict([item.split("=", 1) for item in url_param.split("&")])

    return dict_param


def format_file_size(size):
    """
    计算文件大小
    size:大小（字节）
    """
    if size < 1024:
        value = "%s字节" % size
    elif size < (1024 * 1024):
        value = "%skb" % round(size / 1024, 2)
    elif size < (1024 * 1024 * 1024):
        value = "%sMB" % round(size / (1024 * 1024), 2)
    else:
        value = "%sGB" % round(size / (1024 * 1024 * 1024), 2)

    return value


def allocate_id(size=6):
    now = time.time()
    s = str(now).replace(".", "")[-1 * (size - 1):]
    i_len = len(s)
    if i_len < size:
        s = "%s%s" % ("".join(random.sample("abcdeefghijklmnopqrstuvwxyz", size - i_len)), s)

    return s


def allocate_int_id(size=6):
    return int(allocate_id(size))


def transform_choices(db_field, value):
    if value in ["", None]:
        return ""

    lst_text = []
    dict_data = dict(db_field.choices)

    try:
        lst_value = value.split(",")
        for v in lst_value:
            if v in dict_data:
                lst_text.append(dict_data[v])

        if lst_text:
            return ",".join(lst_text)

        return ""

    except (BaseException,):
        return dict_data.get(value, value)


def parse_encrypt_pwd(pwd):
    """
    解析加密密码
    :param pwd:
    :return:
    """
    try:
        new_pwd = base64.b64decode(pwd)
        new_pwd = new_pwd.decode('utf-8')
        new_pwd = new_pwd[6:-6]
    except (BaseException,):
        new_pwd = pwd

    return new_pwd


def get_choices_value(choices, value):
    """根据字段内choices数据类型判断值的数据类型，value有前端传入（在url上默认是str类型）"""
    data = list(choices)
    if value not in ["", None]:
        try:
            value = eval(value)
        except (BaseException,):
            if isinstance(data[0][0], (int,)):
                value = int(value)

    return value


def collector_nested_2_tree_data(collector_data, tree_data):
    for data in collector_data:
        if isinstance(data, dict):
            tree_data.append(data)
        else:
            tree_data[-1]["children"] = []
            collector_nested_2_tree_data(data, tree_data[-1]["children"])


def format_tree(deleted_objects):
    root = []
    object_num = len(deleted_objects)
    for i, obj in enumerate(deleted_objects):
        if not obj:
            object_num -= 1
            continue

        if isinstance(obj, dict):
            root.append(obj)
            if (i + 1 < object_num) and isinstance(deleted_objects[i + 1], (list, tuple)):
                root[-1]["children"] = format_tree(deleted_objects[i + 1])
        else:
            if root:
                root[-1]["children"] = format_tree(obj)
    return root


def compare_param(src, dst, include=True):
    if src == dst:
        return True

    if (src is None) or (dst is None):
        return False

    o_src = parse.urlparse(src, allow_fragments=True)
    dict_param_src = parse.parse_qs(o_src.query)

    o_dst = parse.urlparse(dst, allow_fragments=True)
    dict_param_dst = parse.parse_qs(o_dst.query)

    if not include:
        if o_dst.path.find(o_src.path) == 0:
            return True

    if o_src.path.strip("/\\") != o_dst.path.strip("/\\"):
        return False

    if not dict_param_src and dict_param_dst:
        return False

    if include:
        for k, v in dict_param_src.items():
            if k not in dict_param_dst:
                return False

            elif v != dict_param_dst[k]:
                return False

        return True

    return dict_param_src == dict_param_dst


def calc_focus_color(color):
    """
    计算焦点色
    """
    if color in [None, "transparent"]:
        return color

    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)

    threshold = 180
    step = 30
    if r > threshold or g > threshold or b > threshold:
        r -= step
        g -= step
        b -= step
        r = 255 if r > 255 else r
        r = 0 if r < 0 else r
        g = 255 if g > 255 else g
        g = 0 if g < 0 else g
        b = 255 if b > 255 else b
        b = 0 if b < 0 else b
    else:
        r += step
        g += step
        b += step
        r = 255 if r > 255 else r
        r = 0 if r < 0 else r
        g = 255 if g > 255 else g
        g = 0 if g < 0 else g
        b = 255 if b > 255 else b
        b = 0 if b < 0 else b

    return "#%02x%02x%02x" % (r, g, b)


def calc_hover_color(color):
    return calc_focus_color(color)


def calc_light_color(color):
    """计算对应颜色的浅色"""
    if color in [None, "transparent"]:
        return color

    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    v = min([r, g, b])
    if v == r:
        r = 251
        g = 255
        b = 255

    elif v == g:
        r = 255
        g = 251
        b = 255

    elif v == b:
        r = 255
        g = 255
        b = 251

    return "#%02x%02x%02x" % (r, g, b)


def calc_black_white_color(color):
    """
    计算颜色灰度，返回对应相反颜色（黑或白）
    """
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    gray_level = r * 0.299 + g * 0.587 + b * 0.114
    # if gray_level >= 192:
    if gray_level >= 170:
        return "#909399"

    # return "#D7D8D7"  # 白色
    return "#FFFFFF"  # 白色


def get_export_path(file_name=None, path_key="export", suffix=None):
    from django.conf import settings
    now = datetime.datetime.now()
    now_date = now.strftime("%Y-%m-%d")
    export_path = os.path.normpath(os.path.join(settings.MEDIA_ROOT, path_key, now_date))
    if not os.path.exists(export_path):
        os.makedirs(export_path)

    if suffix:
        suffix = "." + suffix.strip(".")

    if file_name is None:
        if suffix:
            file_name = now.strftime("%Y%m%d%H%M%S") + suffix
        else:
            file_name = now.strftime("%Y%m%d%H%M%S") + ".tmp"

    elif suffix:
        file_name = os.path.splitext(file_name)[0] + suffix

    file_path = os.path.normpath(os.path.join(export_path, file_name))
    if os.path.exists(file_path):
        name, suffix2 = os.path.splitext(file_name)
        if suffix:
            file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix)
        else:
            file_name = "%s-%s%s" % (name, now.strftime("%H%M%S%f"), suffix2)
        file_path = os.path.normpath(os.path.join(export_path, file_name))

    return file_path


def get_download_url(file_path):
    from django.conf import settings
    url = file_path.replace(settings.MEDIA_ROOT, "", 1)
    url = url.replace(settings.MEDIA_URL, "", 1)
    url = os.path.join(settings.MEDIA_URL, url.replace('\\', '/').strip('/'))
    return url


def get_file_path(path):
    from django.conf import settings
    if path.find(settings.MEDIA_URL) == 0:
        file_path = os.path.join(settings.MEDIA_ROOT, path.replace(settings.MEDIA_URL, ""))
    elif path.find(settings.settings.MEDIA_ROOT) == 0:
        file_path = path
    else:
        file_path = os.path.join(settings.MEDIA_ROOT, path.lstrip("/"))
    return file_path


def get_md5(file):
    """获取文件MD5"""
    m = hashlib.md5()
    with open(file, 'rb') as f:
        for line in f:
            m.update(line)
    md5code = m.hexdigest()
    return md5code


def get_file_type(path):
    import os
    # (1, "文档"), (2, "音频"), (3, "视频"), (4, "图片"), (5, "其它")
    suffix = os.path.splitext(path)[1].lower()
    file_type = 5
    duration = None
    if suffix in [".jpg", '.jpeg', ".png", ".gif", ".bmp", ".svg"]:
        file_type = 4  # 图片
    elif suffix in [".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".pdf"]:
        file_type = 1  # 文档

    elif suffix in [".mp3", ".aac", ".ac3", ".acm", ".amr", ".ape", ".caf",
                    ".flac", ".m4a", ".ra", ".wav", ".wma"]:  # 、wma、avi、rm、rmvb、flv、mpg、mov、mkv:
        file_type = 2
        duration = 0
        try:
            import eyed3
            voice_file = eyed3.load(path)
            # 获取音频时长
            secs = int(voice_file.info.time_secs)
            if secs > 0.5:
                file_type = 2
                duration = secs
        except (BaseException,):
            pass

    # "3gp", "asf", "avi", "dat", "dv", "flv", "f4v", "gif", "m2t", "m3u8", "m4v", "mj2", "mjpeg", "mkv", "mov",
    #     "mp4", "mpe", "mpg", "mpeg", "mts", "ogg", "qt", "rm", "rmvb", "swf", "ts", "vob", "wmv", "webm"
    elif suffix in [".3gp", ".asf", ".avi", ".dat", ".dv", ".flv", ".f4v", ".gif", ".m2t", ".m3u8",
                    ".m4v", ".mj2", ".mjpeg", ".mkv", ".mov",
                    ".mp4", ".mpe", ".mpg", ".mpeg", ".mts", ".ogg", ".qt", ".rm", ".rmvb", ".swf", ".ts", ".vob",
                    ".wmv", ".webm"]:
        file_type = 3
        duration = 0
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(path)
            if clip.duration > 0.5:
                file_type = 3
                duration = clip.duration
        except (BaseException,):
            pass

    elif suffix:
        try:
            from moviepy.editor import VideoFileClip
            clip = VideoFileClip(path)
            if clip.duration > 0.5:
                file_type = 3
                duration = clip.duration
        except (BaseException,):
            pass

    return file_type, duration


def is_phone_terminal(request):
    user_agent = request.META["HTTP_USER_AGENT"].lower()
    if ("android" in user_agent) or ("iphone" in user_agent):
        return True

    return False


def format_file_name(name):
    name = name.replace(" ", "").replace("+", "").replace(",", "")
    return name


def get_license():
    CheckLicense = lib.CheckLicense
    CheckLicense.argtypes = [c_char_p, c_longlong, c_char_p]
    CheckLicense.restype = c_char_p
    from vadmin_standard.models import License
    obj = License.objects.filter(del_flag=False).first()
    if obj and obj.license and obj.domain and obj.port:
        license = CheckLicense(bytes(obj.domain, encoding='utf-8'), int(obj.port),
                               bytes(obj.license, encoding='utf-8'))
        license = license.decode()

        return license, obj.domain, obj.port, obj.expire_date

    return "", "", 0, ""


if __name__ == '__main__':
    # import time

    # lib = ctypes.CDLL('./sum.so')
    # lib.sum.restype = ctypes.c_int32
    # print(lib.sum(1, 2))
    # unicode = lib.unicode
    # unicode.restype = c_char_p
    # 调用函数返回的也是一个字节，我们需要再使用utf-8转回来
    # print(lib.unicode(c_char_p("我永远喜欢".encode("utf-8"))).decode("utf-8"))  # 我永远喜欢古明地觉

    b = time.time()
    # param = {}
    # for i in range(1, 1000):
    #     param[str(i)] = i
    #
    # for i in range(0, 10000):
    #     # url = make_url("aa/?x=1&y=2&z=3&a=1&b=2&c=3&d=4&e=5&f=6",
    #     #                param=param, filter=["x", "y"])
    #
    #     r = make_url("aa/?x=1&y=2&z=3&a=1&b=2&c=3&d=4&e=5&f=6",
    #                  param=param, filter=["x", "y"])
    #     # print(r)
    #     # break
    print(get_md5(r"C:\Users\wangbin\Desktop\zhongtie.sql"))
    e = time.time()

    print(e - b)
