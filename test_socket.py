# Author: 1181110317 <1181110317@qq.com>

import socket

PORT = 10086  # 与服务器端保持一致

def _get_message_address(region):
    """
    根据区域索引生成唯一的消息地址，避免生成保留的 IP 地址（如 .0 和 .255）。
    """
    x, y = region
    
    # 确保生成的地址在有效范围内，避免使用 .0 和 .255
    ip_segment_3 = (x % 254) + 1  # 避免 x.0 和 x.255
    ip_segment_4 = (y % 254) + 1  # 避免 x.x.0 和 x.x.255
    
    ip = f"192.168.{ip_segment_3}.{ip_segment_4}"
    port = PORT + (x * 31 + y * 17) % (65535 - PORT)
    
    return ip, port


def send_and_receive():
    # 目标地址
    message_address = '127.0.0.1'  # 本地测试，使用 127.0.0.1
    message_port = PORT
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 发送消息
    sock.sendto("Hello, Server!fsadfsladfjklsadfjlkasdjfklsaljkfdjlaskfljkasljkflaskjfjlkasdlkfklasdjfsadlkfjklasd;asasasasasasasasasasasasasasasasasasasasasasas".encode(), (message_address, message_port))
    print(f"消息已发送到 {(message_address, message_port)}")

    # 接收响应消息
    try:
        message, addr = sock.recvfrom(1024)
        print(f"接收到来自 {addr} 的响应: {message.decode()}")
    except socket.timeout:
        print("接收超时，没有响应。")

# 启动客户端
if __name__ == "__main__":
    send_and_receive()
