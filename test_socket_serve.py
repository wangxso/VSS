import socket

PORT = 10086  # 固定端口号，用于监听消息

def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_sock.bind(('0.0.0.0', PORT))  # 绑定到所有可用的网络接口   print(f"服务器已启动，正在监听端口 {PORT}...")

    while True:
        data, addr = server_sock.recvfrom(1024)  # 接收数据
        print(f"接收到来自 {addr} 的消息: {data}")

        # 发送响应消息
        server_sock.sendto(b"ACK: " + data, addr)

# 启动服务器
if __name__ == "__main__":
    start_server()