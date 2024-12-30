from ctypes import cdll, c_char_p, c_int, POINTER, create_string_buffer, byref, WinDLL, c_char, c_long,c_ubyte
import os


# 加载sdk
pki_path = os.path.abspath(__file__)
directory = os.path.dirname(pki_path) + "\\bin"
os.environ['PATH'] += os.pathsep + directory
# os.environ['PATH'] += os.pathsep + 'pki/sdk/bin'
lib = WinDLL('libdatasec.dll')


# 设置DS_InitSecurityService函数参数类型和返回类型
lib.DS_InitSecurityService.argtypes = [c_char_p]
lib.DS_InitSecurityService.restype = c_int
'''
    * @brief 初始化安全服务
    *
    * @param[in]  vassRootPath       VASS服务程序目录路径,如/opt/vass
    *
    * @return 错误码
    * @retval 0-成功 其他-错误
'''
def DS_InitSecurityService(vassRootPath):
    res = lib.DS_InitSecurityService(vassRootPath)
    return res


# 设置DS_SignEx函数参数类型和返回类型
lib.DS_SignEx.argtypes = [
    c_char_p, c_int, c_char_p, c_int, c_long, c_char_p, c_int,
    c_char_p, POINTER(c_int)
]
lib.DS_SignEx.restype = c_int
'''
    * @brief 基于安全消息的数据签名(扩展)
    *
    * @param[in]  cert,              证书数据(16进制数组-OER编码后的证书)
    * @param[in]  certlen,           证书长度
    * @param[in]  prikey,            证书配套私钥(32字节)
    * @param[in]  signerType         签名者类型：0 证书hashId8，1 证书
    * @param[in]  itsAid             应用ID
    * @param[in]  plain              待签明文数据
    * @param[in]  plainLen           待签明文数据长度
    * @param[out] secureMessage      签名后安全消息数据
    * @param[out] secureMessageLen   签名后安全消息数据长度
    *
    * @return 错误码
    * @retval 0-成功 其他-错误
'''
def DS_SignEx(cert, certlen, prikey, signerType, itsAid, plain, plainLen,
    secureMessage, secureMessageLen):
    res = lib.DS_SignEx(
    cert, certlen, prikey, signerType, itsAid, plain, plainLen,
    secureMessage, byref(secureMessageLen)
)
    return res


# 设置DS_VerifySigned函数参数类型和返回类型
lib.DS_VerifySigned.argtypes = [
    c_long,POINTER(c_char),c_int,POINTER(c_char),POINTER(c_int)
]
lib.DS_SignEx.restype = c_int
'''
    * @brief 验证数据签名
    *
    * @param[in]  itsAid            应用ID
    * @param[in] securedMessage      签名安全消息数据
    * @param[in] securedMessageLen   签名安全消息数据长度
    * @param[out] plain      明文数据
    * @param[out] plainLen   明文数据长度指针
    * @return 错误码
    * @retval 0-成功其他-错误
'''
def DS_VerifySigned(itsAid,securedMessage,securedMessageLen,plain,plainLen):
    # res = lib.DS_VerifySigned(
    # itsAid, securedMessage, securedMessageLen, plain, byref(plainLen))
    res = lib.DS_VerifySigned(
    itsAid, securedMessage, securedMessageLen, plain, byref(plainLen))
    return res



def load_cert(cert_path):
    try:
        newCert = None
        with open(cert_path, "rb") as fp:
            # 读取文件内容
            newCert = fp.read(1024)
            certlen = len(newCert)
            if certlen <= 0:
                print("cert open failed")
            else:
                print("[BUFF]: certlen = %d" % certlen)
    except FileNotFoundError:
        print("oer open failed")
    except Exception as e:
        print(f"An error occurred: {e}")
    return newCert, c_int(certlen)


def load_prikey(key_path):
    try:
        newPrikey = None
        with open(key_path, "rb") as fp:
            # 读取文件内容
            newPrikey = fp.read(1024)
            keylen = len(newPrikey)
            if keylen <= 0:
                print("prikey open failed")
            else:
                print("[BUFF]: keylen = %d" % keylen)
    except FileNotFoundError:
        print("oer open failed")
    except Exception as e:
        print(f"An error occurred: {e}")
    return newPrikey