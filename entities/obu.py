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
from message.bsm import BasicSafetyMessage
from manager.perception_manager import PerceptionManager

# 区域化消息池，按区域存储消息
communication_range = 500

class OBU:
    def __init__(self, v2x_manager: V2XManager, vehicle: Vehicle, cav_world: CavWorld, perception_manager: PerceptionManager, config_yaml: Dict = None):
        """
        初始化OBU对象。

        参数:
            vehicle (Vehicle): 绑定的车辆对象。
            communication_range (float): 通信范围（单位：米）。
        """
        self.vehicle = vehicle
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
        self.received_messages = []  # 存储接收到的V2X消息
        self.v2x_manager = v2x_manager
        self.cav_world = cav_world
        self.perception_manager = perception_manager

        

    def send_v2x_message(self, message: Dict = None):
        """
        发送V2X消息。

        参数:
            message (Dict): 要发送的V2X消息。
        """

        add_noise_x, add_noise_y, add_noise_yaw = self.v2x_manager.get_ego_pos()
        add_noise_speed = self.v2x_manager.get_ego_speed()

        bsm_message = BasicSafetyMessage()
        bsm_message.vehicle_id = self.vehicle.id
        bsm_message.timestamp = time.time()
        bsm_message.sim_time = self.vehicle.sim_time
        bsm_message.latitude = add_noise_x / 1e-7
        bsm_message.longitude = add_noise_y / 1e-7
        bsm_message.elevation = self.vehicle.z / 0.1
        bsm_message.speed = add_noise_speed / 0.02

        if add_noise_yaw < 0:
            add_noise_yaw += 360
        if add_noise_yaw > 359.9875:
            add_noise_yaw =359.9875 
        heading = round(add_noise_yaw / 0.0125)

        bsm_message.heading = int(heading)
        bsm_message.length = self.vehicle.length / 0.1
        bsm_message.width = self.vehicle.width / 0.1
        bsm_message.acceleration = self.vehicle.acceleration  / 0.1
        bsm_message.lights_status = self.vehicle.lights_status

        try:
            perception = str(self.perception_manager.detect())
            if perception == None:
                perception = "未感知到障碍物"
        except:
            perception = "未感知到障碍物"

        bsm_message.perception = perception


        bsm_message = bsm_message.encode()

        region = self._get_region(add_noise_x, add_noise_y)
        if region not in self.cav_world.MESSAGE_REGIONS:
            self.cav_world.MESSAGE_REGIONS[region] = []
        self.cav_world.MESSAGE_REGIONS[region].append(bsm_message)  # 将消息存入对应区域的消息池
        print(f"车辆 {self.vehicle.id} 发送消息: {bsm_message}")                                                                                                                                                                                                                                     

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

    def detect_devices_in_range(self) -> List[Vehicle]:
        """
        检测通信范围内的设备, RSU或者带有OBU的车辆。
        """
        return self.v2x_manager.search_nearby_vehicles_comm()

    def process_region_messages(self):
        """
        从区域消息池中提取通信范围内的消息，包括覆盖多个区域。
        """
        current_region = self._get_region(self.vehicle.x, self.vehicle.y)
        adjacent_regions = self._get_adjacent_regions(current_region)

        for region in adjacent_regions:
            if region in self.cav_world.MESSAGE_REGIONS:
                for message in self.cav_world.MESSAGE_REGIONS[region]:
                    message = BasicSafetyMessage.decode(message)

                    # 检查时间有效性
                    if self.use_sim:
                        current_time = self.vehicle.sim_time
                        if current_time - message['sim_time'] > self.message_tolerate:
                            continue
                    else:
                        current_time = self.vehicle.current_time
                        if current_time - message['timestamp'] > self.message_tolerate:
                            continue
                    
                    distance = self._calculate_distance(
                        (self.vehicle.x, self.vehicle.y), [message['latitude']*1e-7, message['longitude']*1e-7]
                    )
                    if distance <= self.communication_range and message['vehicle_id'] != self.vehicle.id:
                        self.receive_v2x_message(message)


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
        print(f"车辆 {self.vehicle.id} 正在处理接收到的消息...")
        for message in self.received_messages:
            print(f"处理消息: {message}")
        # 清空消息队列
        self.received_messages.clear()

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

        参数:
            pos1 (Tuple[float, float]): 第一个位置的坐标。
            pos2 (Tuple[float, float]): 第二个位置的坐标。

        返回:
            float: 两点之间的距离。
        """
        return math.sqrt((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2)

    def _get_region(self, x: float, y: float) -> Tuple[int, int]:
        """
        根据坐标获取区域索引。

        参数:
            x (float): x坐标。
            y (float): y坐标。

        返回:
            Tuple[int, int]: 区域索引。
        """
        region_size = self.communication_range  # 每个区域的大小
        return int(x // region_size), int(y // region_size)

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
