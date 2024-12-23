from pki.xdjapki import *
import pytest


def test_xdjaapi():
    vassRootPath = "pki/sdk/data"
    pkisys = XdjaPKI(vassRootPath,-111)

    message = "sadasda"
    sign_type = 0


    # 返回签名后消息(字节串bytes)与消息长度
    s_m,sl = pkisys.sign(message,sign_type)
    s_m2,sl2 = pkisys.sign(message,sign_type)

    # 返回明文消息(字节串bytes)与消息长度
    p_m,pl = pkisys.verify(s_m)
    print(p_m)

    # 验证消息解析是否正确
    print(p_m.decode("utf-8") == message)