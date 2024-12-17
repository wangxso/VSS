class V2XApplication:
    def __init__(self, comm_system, pki_system):
        self.comm_system = comm_system
        self.pki_system = pki_system
    
    def generate_message(self, data):
        # 根据应用逻辑生成消息
        message = {'type': 'warning', 'data': data}
        return message
    
    def send_message(self, message, recipient):
        # 签名消息，保证数据完整性和身份验证
        signed_message = self.pki_system.sign(message)
        # 通过通信系统发送消息
        self.comm_system.send_message(signed_message, recipient)