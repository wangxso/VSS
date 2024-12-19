# Author: 1181110317 <1181110317@qq.com>

import math
from typing import List, Dict, Tuple, Union
from vehicle import Vehicle

# 区域化消息池，按区域存储消息
MESSAGE_REGIONS = {}

class OBU:
    def __init__(self, vehicle: Vehicle, communication_range: float):
        """
        初始化OBU对象。

        参数:
            vehicle (Vehicle): 绑定的车辆对象。
            communication_range (float): 通信范围（单位：米）。
        """
        self.vehicle = vehicle
        self.communication_range = communication_range  # 通信范围
        self.received_messages = []  # 存储接收到的V2X消息

    def send_v2x_message(self, message: Dict):
        """
        发送V2X消息。

        参数:
            message (Dict): 要发送的V2X消息。
        """
        message['sender_id'] = self.vehicle.id
        message['sender_position'] = (self.vehicle.x, self.vehicle.y)
        region = self._get_region(self.vehicle.x, self.vehicle.y)
        if region not in MESSAGE_REGIONS:
            MESSAGE_REGIONS[region] = []
        MESSAGE_REGIONS[region].append(message)  # 将消息存入对应区域的消息池
        print(f"车辆 {self.vehicle.id} 发送消息: {message}")                                                                                                                                                                                                                                     

    def receive_v2x_message(self, message: Dict):
        """
        接收V2X消息。

        参数:
            message (Dict): 接收到的V2X消息。
        """
        self.received_messages.append(message)
        print(f"车辆 {self.vehicle.id} 接收到消息: {message}")

    def detect_devices_in_range(self, devices: List[Vehicle]) -> List[Vehicle]:
        """
        检测通信范围内的设备。

        参数:
            devices (List[Vehicle]): 当前场景中的所有车辆对象。

        返回:
            List[Vehicle]: 在通信范围内的设备。
        """
        devices_in_range = []
        for other_vehicle in devices:
            if other_vehicle.id != self.vehicle.id:  # 不包含自身
                distance = self._calculate_distance(
                    (self.vehicle.x, self.vehicle.y), (other_vehicle.x, other_vehicle.y)
                )
                if distance <= self.communication_range:
                    devices_in_range.append(other_vehicle)
        print(f"车辆 {self.vehicle.id} 检测到通信范围内设备: {[v.id for v in devices_in_range]}")
        return devices_in_range

    def process_region_messages(self):
        """
        从区域消息池中提取通信范围内的消息，包括覆盖多个区域。
        """
        current_region = self._get_region(self.vehicle.x, self.vehicle.y)
        # 获取当前区域及其周围相邻区域
        adjacent_regions = self._get_adjacent_regions(current_region)

        for region in adjacent_regions:
            if region in MESSAGE_REGIONS:
                for message in MESSAGE_REGIONS[region]:
                    distance = self._calculate_distance(
                        (self.vehicle.x, self.vehicle.y), message['sender_position']
                    )
                    if distance <= self.communication_range and message['sender_id'] != self.vehicle.id:
                        self.receive_v2x_message(message)


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
        region_size = 100  # 每个区域的大小
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
