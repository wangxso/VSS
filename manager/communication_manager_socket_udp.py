# Author: 1181110317 <1181110317@qq.com>

import math
import socket
import time
from typing import List, Dict, Tuple, Union
from entities.vehicle import Vehicle
from manager.v2x_manager import V2XManager
from manager.world_manager import CavWorld
from message.BSM import BasicSafetyMessage
import random
import struct

# 默认通信范围
communication_range = 500
PORT = 10086  # 通信端口

class CommunicationManagerSocketUdp:
    def __init__(self, cav_world, config_yaml=None):
        """
        初始化通信管理器。

        参数:
            cav_world (CavWorld): 用于管理区域消息池的世界对象。
            config (Dict): 配置字典，用于设置通信参数。
        """
        self.cav_world = cav_world
        self.connections = {}  # 存储当前连接的设备或基础设施信息
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # 使用 UDP 套接字

        # 随机ip和端口
        self.ip = 'localhost'
        self.port = 10086

        self.received_messages = []
    
        
        # 设置套接字的超时和地址
        self.sock.settimeout(1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 65536)

        if config_yaml:
            self.communication_range = config_yaml.get('communication_range', communication_range)
            self.loc_noise = config_yaml.get('loc_noise', 0.0)
            self.yaw_noise = config_yaml.get('yaw_noise', 0.0)
            self.speed_noise = config_yaml.get('speed_noise', 0.0)
            self.lag = config_yaml.get('lag', 0)
            self.message_tolerate = config_yaml.get('message_tolerate', 0)
            self.save_latest = config_yaml.get('save_latest', True)
            self.use_sim = config_yaml.get('use_sim', True)
        else:
            self.communication_range = communication_range
            self.loc_noise = 0
            self.yaw_noise = 0
            self.speed_noise = 0
            self.lag = 0
            self.message_tolerate = 0
            self.save_latest = True
            self.use_sim = True

    def send_v2x_bsm_message(self, vehicle: Vehicle, v2x_manager: V2XManager, objets, config_yaml: Dict = None):
        """
        发送V2X消息。
        """
        add_noise_x, add_noise_y, add_noise_yaw = v2x_manager.get_ego_pos()
        add_noise_speed = v2x_manager.get_ego_speed()

        bsm_message = BasicSafetyMessage()
        bsm_message.vehicle_id = vehicle.id
        bsm_message.timestamp = time.time()
        bsm_message.sim_time = vehicle.sim_time
        bsm_message.latitude = add_noise_x / 1e-7
        bsm_message.longitude = add_noise_y / 1e-7
        bsm_message.elevation = vehicle.z / 0.1
        bsm_message.speed = add_noise_speed / 0.02

        if add_noise_yaw < 0:
            add_noise_yaw += 360
        if add_noise_yaw > 359.9875:
            add_noise_yaw = 359.9875
        heading = round(add_noise_yaw / 0.0125)

        bsm_message.heading = int(heading)
        bsm_message.length = vehicle.length / 0.1
        bsm_message.width = vehicle.width / 0.1
        bsm_message.acceleration = vehicle.acceleration / 0.1
        bsm_message.lights_status = vehicle.lights_status

        if objets is None:
            objets = "未感知到障碍物"

        bsm_message.perception = str(objets)
        bsm_message = bsm_message.encode()

        message_length = len(bsm_message)
    
        # 将消息长度转换为字节（大端字节序，4 字节）
        length_header = struct.pack('!I', message_length)

        # 获取区域并发送消息
        region = self._get_region(add_noise_x, add_noise_y)


        if region not in self.cav_world.MESSAGE_REGIONS_UDP:
            self.cav_world.MESSAGE_REGIONS_UDP[region] = self.cav_world.find_free_port()
            self.cav_world.add_port(self.cav_world.MESSAGE_REGIONS_UDP[region])

        message_address, message_port = self._get_message_address(region)

        self.sock.sendto(bsm_message, (message_address, message_port))

        print(f"车辆 {vehicle.id} 发送消息: {bsm_message}")

    def receive_v2x_message(self, message: Dict):
        """
        接收V2X消息。

        参数:
            message (Dict): 接收到的V2X消息。
            save_latest (bool): 是否保存最新的消息。如果为False，则保存符合时间容忍度的消息。
        """

        if self.save_latest:
            sender_id = message['vehicle_id']
            self.received_messages = {msg['vehicle_id']: msg for msg in self.received_messages}  # 转换为字典，按sender_id存储
            self.received_messages[sender_id] = message  # 更新或新增最新消息
            self.received_messages = list(self.received_messages.values())  # 转回列表存储
        else:
            self.received_messages.append(message)


    def process_region_messages(self, vehicle: Vehicle):
        """
        从区域消息池中提取通信范围内的消息。
        """

        current_region = self._get_region(vehicle.x, vehicle.y)
        adjacent_regions = self._get_adjacent_regions(current_region)


        # 恶心人的写法，现在没有划分通信区域 直接在整个地址搜素 速度慢 ！！！！！！！！！！！
        adjacent_regions = [self._get_region(vehicle.x, vehicle.y)]
        
        for region in adjacent_regions:
            message_address, message_port = self._get_message_address(region)
            try:
                # 接收来自相邻区域的消息
                # self.sock.sendto(b"REQUEST", (message_address, message_port))
                
                
                message, _ = self.sock.recvfrom(4096)
                message = message.decode('utf-8')[5:]
                message = message.encode('utf-8')

                message = BasicSafetyMessage.decode(message)

                # 检查时间有效性
                if self.use_sim:
                    current_time = vehicle.sim_time
                    if current_time - message['sim_time'] > self.message_tolerate:
                        continue
                else:
                    current_time = vehicle.current_time
                    if current_time - message['timestamp'] > self.message_tolerate:
                        continue
                if message['vehicle_id'] in self.connections:
                    self.receive_v2x_message(message)

            except socket.timeout:
                print(f"未接收到来自区域 {region} 的消息")

        return self.received_messages

    def _get_message_address(self, region: Tuple[int, int]) -> Tuple[str, int]:
        """
        根据区域索引生成唯一的消息地址。

        参数:
            region (Tuple[int, int]): 区域索引 (x, y)。

        返回:
            Tuple[str, int]: 用于通信的 (IP 地址, 端口)。
        """

        # x, y = region
        # # 使用区域的 x 和 y 生成唯一的 IP 地址
        # ip = f"192.168.{(x % 256)}.{(y % 256)}"

        # # 根据区域生成唯一的端口号，确保在有效范围内 (1024-65535)
        # port = PORT + (x * 31 + y * 17) % (65535 - PORT)  # 基于区域计算偏移量

        # return ip, port

        return 'localhost', self.cav_world.MESSAGE_REGIONS_UDP[region]


    def connect(self, target_id, connection_type):
        """
        建立与目标设备或基础设施的连接。
        """
        if target_id in self.connections:
            # print(f"已经与目标 {target_id} 建立了连接。")
            return False

        # 模拟建立连接的逻辑
        self.connections[target_id] = connection_type
        # print(f"成功建立与目标 {target_id} 的 {connection_type} 连接。")
        return True

    def disconnect(self, target_id):
        """
        断开与目标设备或基础设施的连接。

        """
        if target_id not in self.connections:
            # print(f"未找到与目标 {target_id} 的连接。")
            return False

        # 模拟断开连接的逻辑
        del self.connections[target_id]
        # print(f"已断开与目标 {target_id} 的连接。")
        return True

    def list_connections(self):
        """
        列出当前所有的连接。
        """
        # print("当前连接：")
        # for target_id, connection_type in self.connections.items():
        #     print(f"目标 ID: {target_id}, 连接类型: {connection_type}")
        return self.connections

    def broadcast_message(self, vehicle: Vehicle, v2x_manager: V2XManager, perception_manager, config_yaml: Dict = None, message_type: str = 'bsm'):
        """
        向当前通信范围内的所有设备广播消息。
        """
        if message_type == 'bsm':
            self.send_v2x_bsm_message(vehicle, v2x_manager, perception_manager)

    def update_connections(self, nearby_vehicles: Dict, connection_type: str):
        """
        更新当前的连接，根据通信范围内的附近车辆动态调整连接。

        参数:
            nearby_vehicles (List[Vehicle]): 附近车辆的列表。
        """
        # 获取当前的连接类型信息
        current_connections = set(
            target_id for target_id, conn_type in self.connections.items() if conn_type == connection_type
        )
        updated_connections = set()

        for vehicle in nearby_vehicles.keys():
            # 如果车辆在通信范围内，更新连接
            updated_connections.add(vehicle)
            if vehicle not in current_connections:
                self.connect(vehicle, connection_type)

        # 清理不在范围内的连接
        for target_id in current_connections - updated_connections:
            self.disconnect(target_id)

    '''
    ===================================工具===================================
    '''
    def _get_adjacent_regions(self, region: Tuple[int, int]) -> List[Tuple[int, int]]:
        """
        获取当前区域及其相邻区域。

        参数:
            region (Tuple[int, int]): 当前区域的索引。

        返回:
            List[Tuple[int, int]]: 包括当前区域和周围相邻区域的列表。
        """
        x, y = region
        adjacent = [
            (x - 1, y - 1), (x, y - 1), (x + 1, y - 1),
            (x - 1, y),     (x, y),     (x + 1, y),
            (x - 1, y + 1), (x, y + 1), (x + 1, y + 1)
        ]

        return adjacent

    def _calculate_distance(self, pos1: Tuple[float, float], pos2: Tuple[float, float]) -> float:
        """
        计算两点之间的欧几里得距离。
        """
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def _get_region(self, x: float, y: float) -> Tuple[int, int]:
        """
        根据坐标获取区域索引。
        """
        region_size = self.communication_range  # 每个区域的大小
        return int(x // region_size), int(y // region_size)

    def _get_center(self, region: Tuple[int, int]) -> Tuple[float, float]:
        """
        获取区域的中心点。
        """
        x, y = region
        return x * self.communication_range + self.communication_range / 2, y * self.communication_range + self.communication_range / 2
