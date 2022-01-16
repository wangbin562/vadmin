# !/usr/bin/python
# -*- coding=utf-8 -*-

'''
/**
* AES加密字符串
*
* @param string data 加密的串
* @param string key 密钥(只能是16、24、32位)
* @param string iv 16位长度向量
* @return string 加密后的结果
*/
'''


def encrypt(data, key=b'www.phperz.com!!', iv=b'www.phperz.com!!', is_quote=False):
    import base64
    import binascii
    from Crypto.Cipher import AES

    if isinstance(data, str):
        data = bytes(data, encoding="utf8")

    if isinstance(key, str):
        key = bytes(key, encoding="utf8")

    if isinstance(iv, str):
        iv = bytes(iv, encoding="utf8")

    length = len(data)
    num = length % 16
    data = data.ljust(length + 16 - num)
    obj = AES.new(key, AES.MODE_CBC, iv)
    result = obj.encrypt(data)
    encrypted = base64.b64encode(result)
    encrypted = binascii.b2a_hex(encrypted)
    encrypted = str(encrypted, encoding="utf8")
    # if is_quote:  # 是否url编码
    #     from urllib.parse import quote
    #     encrypted = quote(encrypted)

    return encrypted


''' 
/**
* AES解密字符串 
* 
* @param string data 待解密的串 
* @param string key 密钥 
* @param string iv 16位长度向量 
* @return string 解密后的结果
*/ 
'''


def decrypt(data, key=b'www.phperz.com!!', iv=b'www.phperz.com!!'):
    import base64
    import binascii
    from Crypto.Cipher import AES
    try:
        if isinstance(data, str):
            data = bytes(data, encoding="utf8")

        if isinstance(key, str):
            key = bytes(key, encoding="utf8")

        if isinstance(iv, str):
            iv = bytes(iv, encoding="utf8")

        encrypted = binascii.a2b_hex(data)
        encrypted = base64.b64decode(encrypted)
        obj = AES.new(key, AES.MODE_CBC, iv)
        result = obj.decrypt(encrypted).rstrip(b" ")
        return str(result, encoding="utf8")
    except (BaseException,):
        return data


def cbc_encrypt(data, key, iv=None):
    """des cbc加密"""
    import base64
    from Crypto.Cipher import AES

    if isinstance(key, str):
        key = bytes(key, encoding="utf8")

    if iv is None:
        iv = key
    elif isinstance(iv, str):
        iv = bytes(iv, encoding="utf8")

    __BLOCK_SIZE_16 = BLOCK_SIZE_16 = AES.block_size
    cipher = AES.new(key, AES.MODE_CBC, iv)
    x = __BLOCK_SIZE_16 - (len(data) % __BLOCK_SIZE_16)
    if x != 0:
        data = data + chr(x) * x

    if isinstance(data, str):
        data = bytes(data, encoding="utf8")

    encrypted = cipher.encrypt(data)
    # msg = base64.urlsafe_b64encode(msg).replace('=', '')
    encrypted = base64.b64encode(encrypted)
    encrypted = str(encrypted, encoding="utf8")
    return encrypted


def cbc_decrypt(data, key, iv=None):
    import base64
    from Crypto.Cipher import AES
    try:
        if isinstance(key, str):
            key = bytes(key, encoding="utf8")

        if iv is None:
            iv = key

        elif isinstance(iv, str):
            iv = bytes(iv, encoding="utf8")

        cipher = AES.new(key, AES.MODE_CBC, iv)
        encrypted = base64.b64decode(data)
        result = cipher.decrypt(encrypted).rstrip(b"\x00").rstrip(b"\n")
        return str(result, encoding="utf8").strip()
    except (BaseException,):
        return data.strip()


