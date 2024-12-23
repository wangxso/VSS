# Author: 1181110317 <1181110317@qq.com>

import math
from typing import List, Dict, Tuple, Union
from entities.vehicle import Vehicle
from manager.v2x_manager import V2XManager
from manager.world_manager import CavWorld
import time

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from message.BSM import BasicSafetyMessage
from manager.perception_manager import PerceptionManager
from manager.communication_manager import CommunicationManager
from manager.communication_manager_socket_udp import CommunicationManagerSocketUdp

# 区域化消息池，按区域存储消息
communication_range = 500

class OBU:
    def __init__(self, v2x_manager: V2XManager, vehicle: Vehicle, cav_world: CavWorld, config_yaml: Dict = None):
        """
        初始化OBU对象。

        参数:
            vehicle (Vehicle): 绑定的车辆对象。
            communication_range (float): 通信范围（单位：米）。
        """
        self.vehicle = vehicle
        self.v2x_manager = v2x_manager
        if cav_world.comm_model == 'sim':
            self.communication_manager = CommunicationManager(cav_world, config_yaml)
        if cav_world.comm_model == 'udp':
            self.communication_manager = CommunicationManagerSocketUdp(cav_world, config_yaml)
            self.ip = self.communication_manager.ip
            self.port = self.communication_manager.port

        self.received_messages = []

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

        

    def send_v2x_message(self, objets: Dict):
        """
        广播发送V2X消息。

        参数:
            message (Dict): 要发送的V2X消息。
        """
        self.communication_manager.broadcast_message(self.vehicle, self.v2x_manager, objets, message_type='bsm')                                                                                                                                                                                               

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

    def detect_vehicles_in_range(self) -> List[Vehicle]:
        """
        检测通信范围内的设备, RSU或者带有OBU的车辆。
        """
        self.v2x_manager.search_nearby_vehicles_comm()
        return self.v2x_manager.cav_nearby_comm

    def process_region_messages(self):
        """
        调用通信管理器处理区域内的消息。
        """
        v2x_message = self.communication_manager.process_region_messages(self.vehicle)
        for i in range(len(v2x_message)):
            self.receive_v2x_message(v2x_message[i])


    def forward_v2x_message(self, received_message: Dict):
        """
        转发已接收的V2X消息。

        参数:
            received_message (Dict): 接收到的V2X消息。
        """
        received_message['forwarder_id'] = self.vehicle.id

        # 预留功能，之后在写


    def process_received_messages(self):
        """
        处理接收到的V2X消息。
        """
        # print(f"车辆 {self.vehicle.id} 正在处理接收到的消息...")
        # for message in self.received_messages:
        #     print(f"处理消息: {message}")
        # 清空消息队列
        self.received_messages.clear()

    
    def update(self):
        nearby_vehicles = self.detect_vehicles_in_range()
        self.communication_manager.update_connections(nearby_vehicles, "V2V")
        self.communication_manager.received_messages = []
        # self.communication_manager.list_connections()

    def get_list_connections(self):
        return self.communication_manager.list_connections()



# 测试代码
if __name__ == "__main__":
    # 创建测试车辆
    vehicle1 = Vehicle()
    vehicle1.id = "vehicle_1"
    vehicle1.x, vehicle1.y = 0, 0

    vehicle2 = Vehicle()
    vehicle2.id = "vehicle_2"
    vehicle2.x, vehicle2.y = 10, 10

    vehicle3 = Vehicle()
    vehicle3.id = "vehicle_3"
    vehicle3.x, vehicle3.y = 150, 150

    # 创建OBU对象
    obu1 = OBU(vehicle1, communication_range=30.0)
    obu2 = OBU(vehicle2, communication_range=30.0)
    obu3 = OBU(vehicle3, communication_range=30.0)

    # 检测通信范围内的设备
    obu1.detect_devices_in_range([vehicle1, vehicle2, vehicle3])

    # 发送消息
    obu1.send_v2x_message({"type": "status_update", "speed": 20})

    # 处理区域消息
    obu2.process_region_messages()
    obu3.process_region_messages()

    # 处理接收到的消息
    obu2.process_received_messages()
    obu3.process_received_messages()

