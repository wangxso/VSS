import math
import socket
import json
import random
from loguru import logger
def path_loss(distance, frequency=5.9e9):
    """简化的自由空间路径损耗模型"""
    c = 3e8  # 光速
    wavelength = c / frequency
    loss = 20 * math.log10(distance) + 20 * math.log10(frequency) - 147.55
    return loss

class CommunicationSystem:
    def __init__(self, host, port, tx_power=10, threshold=-100):
        """初始化通信系统
        tx_power: 发射功率（单位 dBm）
        threshold: 最低接收功率阈值（单位 dBm），低于此阈值认为信号丢失
        """
        self.host = host
        self.port = port
        self.sock = None
        self.tx_power = tx_power  # 发射功率，单位 dBm
        self.distance = 100  # 信号传输距离，单位米
        self.threshold = threshold  # 最低接收功率阈值，单位 dBm

    def establish_channel(self):
        """建立信道"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((self.host, self.port))

    def close_channel(self):
        """关闭信道"""
        if self.sock:
            self.sock.close()

    def calculate_received_power(self, distance, frequency=5.9e9):
        """根据路径损耗模型计算接收功率"""
        loss = path_loss(distance, frequency)
        # 接收功率（单位dBm） = 发射功率（单位dBm） - 路径损耗
        received_power = self.tx_power - loss
        return received_power

    def is_message_received(self, received_power):
        """根据接收功率判断消息是否接收到"""
        # 如果接收功率低于阈值，认为数据丢失
        if received_power < self.threshold:
            return False  # 数据丢失
        else:
            return True  # 数据接收成功

    def send_message(self, message, recipient):
        """序列化消息并发送"""
        serialized_message = json.dumps(message).encode()
        # 计算接收功率
        received_power = self.calculate_received_power(self.distance)
        logger.info(f"Sending message to {recipient} with received power: {received_power} dBm")
        
        # 判断接收端是否能接收到数据
        if self.is_message_received(received_power):
            self.sock.sendall(serialized_message)
            logger.info("Message sent successfully.")
        else:
            logger.info("Message lost due to low signal power.")
            # 你可以在这里进行重发或者其他操作

    def receive_message(self):
        """接收并反序列化消息"""
        data = self.sock.recv(1024)
        received_power = self.calculate_received_power(self.distance)
        
        # 判断接收到的信号强度，决定是否丢失数据
        if self.is_message_received(received_power):
            return json.loads(data.decode())
        else:
            logger.info("Message reception failed due to low signal power.")
            return None  # 模拟丢失消息
