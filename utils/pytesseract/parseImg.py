#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
@version: V1.0
@author: Coffen
@license: HuiYu Licence
@file: parseImg
@time: 2018/10/22 10:57
"""
from PIL import Image

""" 读取图片 """
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()


def baidu_api():

    # import Image
    import pytesseract
    import pytesser3
    #上面都是导包，只需要下面这一行就能实现图片文字识别
    text = pytesseract.image_to_string(Image.open('./1.jpg'), lang='chi_sim')
    text_data = pytesseract.image_to_data(Image.open('./1.jpg'), lang='chi_sim')

    # text = pytesser3.image_file_to_string('./denggao.jpg', graceful_errors=True)
    # text = pytesser3.image_file_to_string('./test.png', graceful_errors=True)
    # text = pytesser3.image_file_to_string('./test-european.jpg', graceful_errors=True)
    # print("Using image_file_to_string():")
    # print(text)
    # print(text_data)

    from aip import AipImageClassify, AipOcr

    """ 你的 APPID AK SK """
    APP_ID = '11626285'
    API_KEY = 'AXqQSnqEpurGFdf1LER79L6F'
    SECRET_KEY = 'nHpPn8WRAaKNc5U2feqnVAPnSRgcpYMo'

    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)

    image = get_file_content('2.jpg')

    """ 调用通用文字识别（高精度版） """
    # client.basicAccurate(image)

    """ 如果有可选参数 """
    options = {}
    # options["detect_direction"] = "true"
    # options["probability"] = "true"
    templateSign = "d887d97a29903cf105bc4894ef007b01"

    """ 带参数调用通用文字识别（高精度版） """
    # res = client.basicAccurate(image, options)
    res = client.custom(image, templateSign, options)
    # print(res)
    print(res)
    print(res.get('words_result'))


def blur_img():
    """
    BLUR

    ImageFilter.BLUR为模糊滤波，处理之后的图像会整体变得模糊。

    例子：
    """

    from PIL import ImageFilter

    im =Image.open("imgtest.png")

    im_filter = im.filter(ImageFilter.BLUR)

    print(im.mode, im.size, im.format)

    im_filter.save('blur.png')


def change_size_img(im):
    box = (100, 100, 100, 100)
    region = im.crop(box)

if __name__ == '__main__':
    blur_img()

