import socket
import threading
import time
import random


class UDP:
    def __init__(self):
        self.used_ports = set()
        self.lock = threading.Lock()

    def find_free_port(self):
        while True:
            port = random.randint(1024, 65535)
            with self.lock:
                if port not in self.used_ports:
                    try:
                        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        temp_socket.bind(('localhost', port))
                        temp_socket.close()
                        self.used_ports.add(port)
                        print(f"Allocated port: {port}")
                        return port
                    except OSError:
                        continue


class CommunicationManagerSocketUdp:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        self.ip = '127.0.0.1'
        self.udp = UDP()
        self.port = self.udp.find_free_port()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1)
        self.received_messages = []
        self.running = True

        self.receive_thread = threading.Thread(target=self._receive_messages)
        self.receive_thread.start()
        print(f"Vehicle {vehicle_id} listening on {self.ip}:{self.port}")

    def ppp(self):
        print(123)

    def _receive_messages(self):
        while self.running:
            try:
                message, addr = self.sock.recvfrom(4096)
                # print(f"Vehicle {self.vehicle_id} received from {addr}: {message.decode('utf-8')}")
                self.received_messages.append(message.decode('utf-8'))
                self.ppp()
            except socket.timeout:
                continue
            except Exception as e:
                print(f"Vehicle {self.vehicle_id} error while receiving: {e}")

    def send_message(self, target_ip, target_port, message):
        try:
            self.sock.sendto(message.encode('utf-8'), (target_ip, target_port))
            print(f"Vehicle {self.vehicle_id} sent message to {target_ip}:{target_port}")
        except Exception as e:
            print(f"Vehicle {self.vehicle_id} error while sending: {e}")

    def stop(self):
        self.running = False
        self.receive_thread.join()
        self.sock.close()

# for i in range(100):
# 测试代码
vehicle1 = CommunicationManagerSocketUdp(vehicle_id=1)
vehicle2 = CommunicationManagerSocketUdp(vehicle_id=2)

# time.sleep(1)  # 等待线程初始化

# 车辆1发送消息给车辆2
for i in range(100):
    vehicle1.send_message(vehicle2.ip, vehicle2.port, f"Hello from Vehicle"*60 + '111' +str(i))

    # 等待接收
    time.sleep(0.001)

    # 检查车辆2的接收到的消息
    print(f"Vehicle 2 messages: {vehicle2.received_messages[0].split('111')[-1]}")

    vehicle2.received_messages = []

# 停止线程
vehicle1.stop()
vehicle2.stop()
