# Author: 1181110317 <1181110317@qq.com>

import uuid
from typing import List, Dict
from entities.vehicle import Vehicle
from entities.rsu import RSU  # 假设 RSU 已经定义

class RSUManager:
    def __init__(self, rsu: RSU):
        """
        初始化 RSU 管理类，只管理一个RSU。
        
        参数:
            rsu (RSU): RSU 实例
        """
        self.rid = rsu.id
        self.rsu = rsu  # 只管理一个RSU

    def add_vehicle(self, vehicle: Vehicle):
        """将车辆添加到RSU管理的车辆列表中"""
        self.rsu.add_vehicle(vehicle)
        print(f"车辆 {vehicle.id} 已添加到 RSU {self.rsu.id}。")

    def remove_vehicle(self, vehicle: Vehicle):
        """从RSU管理的车辆列表中移除车辆"""
        self.rsu.remove_vehicle(vehicle)
        print(f"车辆 {vehicle.id} 已从 RSU {self.rsu.id} 移除。")

    def broadcast_message(self, message: str):
        """向RSU广播消息"""
        self.rsu.broadcast_message(message)

    def check_collisions(self):
        """检查RSU范围内所有车辆的碰撞情况"""
        self.rsu.check_vehicle_collisions()

    def get_rsu_info(self) -> Dict:
        """获取RSU的基本信息"""
        return self.rsu.get_rsu_info()

    def get_nearby_vehicles_info(self) -> List[Dict]:
        """获取RSU范围内所有车辆的信息"""
        return self.rsu.get_nearby_vehicles_info()
