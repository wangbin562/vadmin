# !/usr/bin/python
# -*- coding: utf-8 -*-
"""
django文件扩展
"""

import base64
import os
from datetime import datetime

from PIL import Image
from django.conf import settings
from django.core.exceptions import SuspiciousOperation
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from django.utils.encoding import force_text


class Storage(FileSystemStorage):
    """
    Storage
    """

    def __init__(self, location=settings.MEDIA_ROOT, base_url=settings.MEDIA_URL):
        """__init__"""
        FileSystemStorage.__init__(self, location, base_url)

    @property
    def maxsize(self):
        """maxsize"""
        return 5 * 1024 * 1024

    @property
    def filetypes(self):
        """filetypes"""
        return []

    def delete(self, name):
        FileSystemStorage.delete(self, name)


class FileStorage(Storage):
    """
    FileStorage
    """

    # def generate_filename(self, filename):
    #     return filename

    @property
    def maxsize(self):
        return 200 * 1024 * 1024

    @property
    def filetypes(self):
        return ['fasta', 'hla', 'final', 'apk', 'ipa']

    def _save(self, name, content):
        """
        _save
        :param name:
        :param content:
        :return:
        """
        # ext = name.split(".")[-1]
        # 类型判断
        # if self.filetypes != '*':
        #     if ext.lower() not in self.filetypes:
        #         raise SuspiciousOperation('file type error!')

        # 大小判断
        if content.size > self.maxsize:
            raise SuspiciousOperation('file size error!')

        return super(FileStorage, self)._save(name, content)

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")

        if (name.find(settings.MEDIA_URL) == 0) or (name.find("[") == 0):
            return name

        return super().url(name)


class ImageStorage(Storage):
    """ImageStorage"""

    # def generate_filename(self, filename):
    #     return filename

    @property
    def maxsize(self):
        return 5 * 1024 * 1024

    @property
    def filetypes(self):
        return ['jpg', 'jpeg', 'png', 'gif']

        # def _save(self, name, content):
        #     ext = name.split(".")[-1]
        #     #类型判断
        #     if self.filetypes != '*':
        #         if ext.lower() not in self.filetypes:
        #             raise SuspiciousOperation(const.IMAGES_EXT_ERROR_CODE)
        #
        #     #大小判断
        #     if content.size > self.maxsize:
        #         raise SuspiciousOperation(const.IMAGES_SIZE_ERROR_CODE)
        #
        #     return super(ImageStorage, self)._save(name, content)

    def url(self, name):
        if self.base_url is None:
            raise ValueError("This file is not accessible via a URL.")

        if (name.find(settings.MEDIA_URL) == 0) or (name.find("[") == 0):
            return name

        return super().url(name)


class ThumbStorage(ImageStorage):

    def generate_filename(self, filename):
        return filename

    def save(self, name, content, max_length=None):
        """
        Save new content to the file specified by name. The content should be
        a proper File object or any Python file-like object, ready to be read
        from the beginning.
        """
        # Get the proper name for the file, as it will actually be saved.
        if name is None:
            name = content.name

        if not hasattr(content, 'chunks'):
            content = File(content, name)

        # name = self.get_available_name(name, max_length=max_length)
        return self._save(name, content)

    def _save(self, name, content):
        image = Image.open(content)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')

        width, height = image.size
        size = 100
        if width > size:
            delta = width / size
            height = int(height / delta)
            image.thumbnail((size, height), Image.ANTIALIAS)
            path, name1 = os.path.split(name)
            tmp_name, suffix = os.path.splitext(name1)
            name = os.path.normpath(os.path.join(path, "%s_thumb%s" % (tmp_name, suffix)))
            # image.save(new_path, suffix)
            # full_path = self.path(name)
            name = self.get_available_name(name)
            full_path = self.path(name)
            image.save(full_path, 'JPEG')

            return force_text(name.replace('\\', '/'))

        return None
