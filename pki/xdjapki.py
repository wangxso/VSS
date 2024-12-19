from pkisys import PKI



class XdjaPKI(PKI):
    """xdjaPKI系统, 包含数据签名, 验签功能

    """

    def __init__(self,vass_root_path,itsAid):
        super().__init__(vass_root_path,itsAid)
    

    def sign(self, message,sign_type):
        return super().sign(message,sign_type)
    

    def verify(self, message):
        return super().verify(message)