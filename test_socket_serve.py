# Author: 1181110317 <1181110317@qq.com>

import socket
import threading

def handle_client(port):
    """监听指定端口的 UDP 请求"""
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('localhost', port))
    print(f"服务器在端口 {port} 启动，等待连接...")

    while True:
        data, addr = server_socket.recvfrom(1024)  # 接收数据
        print(f"来自 {addr} 的消息: {data.decode()}")
        server_socket.sendto("消息已收到", addr)  # 向客户端发送回应

# 启动服务器监听不同端口
ports = [12345, 12346]  # 监听多个端口
for port in ports:
    threading.Thread(target=handle_client, args=(port,)).start()

