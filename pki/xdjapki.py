from pki.pkisys import PKI
from pki.sdk import v2x_pki
import random

class XdjaPKI(PKI):
    """xdjaPKI系统, 包含数据签名, 验签功能

    """

    def __init__(self,vass_root_path,itsAid):
        """初始化PKI系统
            1. 初始化安全服务
            2. 加载证书
            3. 加载私钥

        Args:
            vass_root_path (str): VASS服务程序目录路径
            itsAid (int): 应用ID
        """
        # 注册应用ID
        self.itsAid = v2x_pki.c_int(itsAid)
        #初始化安全服务
        self.vass_root_path = vass_root_path.encode("utf-8")
        v2x_pki.DS_InitSecurityService(self.vass_root_path)

        #加载证书
        index = random.randint(0, 19)
        self.ckpath = f"{vass_root_path}/pccerts/pc_{index}/"
        cert_path = self.ckpath+"pc.oer"
        self.cert, self.certlen = v2x_pki.load_cert(cert_path)

        #加载私钥

        prikey_path = self.ckpath+"sign.privatekey"
        self.prikey = v2x_pki.load_prikey(prikey_path)
    

    def sign(self, message,sign_type=0):
        plain = message.encode("utf-8")
        plainLen = len(plain)
        plainLen = v2x_pki.c_int(plainLen)
        sign_type = v2x_pki.c_int(sign_type)
        # 创建缓冲区
        secure_message = v2x_pki.create_string_buffer(1024)
        secure_message_len = v2x_pki.c_int(1024)
        # 签名
        if(v2x_pki.DS_SignEx(self.cert,self.certlen,self.prikey,sign_type,self.itsAid,plain,plainLen,secure_message,secure_message_len) == 0 ):
            sign_message = secure_message[:secure_message_len.value]
            return sign_message,secure_message_len.value
        else:
            return None, None 
    

    def verify(self, message):
        message_len = len(message)
        message_len = v2x_pki.c_int(message_len)
        # 创建缓冲区
        plain = v2x_pki.create_string_buffer(1024)
        plainLen = v2x_pki.c_int(1024)
        # 签名
        if(v2x_pki.DS_VerifySigned(self.itsAid,message,message_len,plain,plainLen) == 0 ):
            plain_message = plain[:plainLen.value]
            return plain_message,plainLen.value
        else:
            return None, None