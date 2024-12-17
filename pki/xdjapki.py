from pkisys import PKI
class XdjaPKI(PKI):
    # 重写
    def sign(self, message):
        return super().sign(message)
    
    # 重写
    def verify(self, message, signature):
        return super().verify(message, signature)