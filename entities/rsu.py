# Author: 1181110317 <1181110317@qq.com>

import uuid
import time
from typing import List, Dict, Union, Tuple
from entities.vehicle import Vehicle
from entities.entity import Entity

# RSU可以看作带有OBU的静止不动的车辆

class RSU(Entity):
    def __init__(self, rsu_id: str = None, location: Tuple[float, float] = (0.0, 0.0, 0.0), communication_range: float = 100.0):
        """
        初始化RSU（道路侧设备）的属性，设定默认值。
        
        参数:
            rsu_id (str, optional): RSU的ID，默认为None。如果未提供，将自动生成一个唯一的UUID。
            location (Tuple[float, float], optional): RSU的位置，默认为(0.0, 0.0)。
            communication_range (float, optional): RSU的通信范围，默认为100.0米。
        """
        super().__init__(rsu_id, entity_type="rsu")
        # RSU基本信息
        self.id = rsu_id if rsu_id else str(uuid.uuid4())
        # RSU位置 (x, y)
        self.x = location[0]
        self.y = location[1]
        self.z = location[2]
        self.communication_range = communication_range  # RSU的通信范围（单位：米）
        self.nearby_vehicles: List[Vehicle] = []  # 与该RSU周围的车辆列表
        self.status = 'active'  # RSU状态（'active', 'inactive'）

    def update_status(self, status: str):
        """更新RSU的状态"""
        valid_statuses = ['active', 'inactive']
        if status not in valid_statuses:
            raise ValueError(f"无效的状态: {status}. 必须为 {valid_statuses} 中的一个.")
        self.status = status

    def add_vehicle(self, vehicle: Vehicle):
        """将附近的车辆添加到RSU管理的车辆列表中"""
        if self._is_vehicle_within_range(vehicle):
            self.nearby_vehicles.append(vehicle)

    def remove_vehicle(self, vehicle: Vehicle):
        """从RSU管理的车辆列表中移除车辆"""
        if vehicle in self.nearby_vehicles:
            self.nearby_vehicles.remove(vehicle)

    def _is_vehicle_within_range(self, vehicle: Vehicle) -> bool:
        """判断车辆是否在RSU的通信范围内"""
        distance = ((self.location[0] - vehicle.x) ** 2 + (self.location[1] - vehicle.y) ** 2) ** 0.5
        return distance <= self.communication_range

    def broadcast_message(self, message: str):
        """广播消息给所有在范围内的车辆"""
        if self.status == 'active':
            print(f"RSU {self.id} 广播消息: {message}")
            for vehicle in self.nearby_vehicles:
                vehicle.receive_message(message)
        else:
            print(f"RSU {self.id} 当前不可用，无法广播消息。")

    def check_vehicle_collisions(self):
        """检测所有在范围内的车辆的碰撞情况"""
        for vehicle in self.nearby_vehicles:
            if vehicle.sensors_data['collision'] > 0:
                print(f"RSU {self.id} 检测到车辆 {vehicle.id} 碰撞！")

    def get_rsu_info(self) -> Dict:
        """获取RSU的基本信息"""
        return {
            'id': self.id,
            'location': (self.x, self.y, self.z),
            'status': self.status,
            'communication_range': self.communication_range,
            'nearby_vehicles': [vehicle.id for vehicle in self.nearby_vehicles]
        }

    def get_nearby_vehicles_info(self) -> List[Dict]:
        """获取所有附近车辆的信息"""
        return [vehicle.get_vehicle_info() for vehicle in self.nearby_vehicles]

