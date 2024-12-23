class PKI:
    """PKI系统
    
    """
    def __init__(self,vass_root_path,itsAid):
        pass
        

    def sign(self, message, sign_type):
        """数据签名

        Args:
            message (str): 待签明文数据
            sign_type (int): 签名者类型: 0 证书hashId8, 1 证书

        Returns:
            bytes: 签名后安全消息数据
            int: 签名后安全消息数据长度
        """
        pass 
        
    
    def verify(self, message):
        """验证数据签名

        Args:
            message (bytes): 签名安全消息数据

        Returns:
            bytes: 明文数据
            int: 明文数据长度
        """
        pass