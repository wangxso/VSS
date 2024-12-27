# Author: 1181110317 <1181110317@qq.com>

from typing import Dict, List, Union, Tuple
from manager.v2x_manager import V2XManager
from manager.world_manager import  CavWorld

import matplotlib.pyplot as plt

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.vehicle import Vehicle  # Vehicle 类已经定义
from entities.obu import OBU
from perception.perception_manager import PerceptionManager
from loguru import logger



class TrafficVehicleManager:
    def __init__(self, vehicle: Vehicle, cav_world: CavWorld, config_yaml: Dict):
        """
        初始化车辆管理类，管理单个车辆的状态和操作。

        参数:
            vehicle (Vehicle): 需要管理的车辆对象。
        """
        self.vehicle = vehicle  # 管理的车辆
        self.vehicle_id = vehicle.id  # 车辆的ID，直接从车辆对象获取

        self.perception_manager = PerceptionManager(vehicle, cav_world)

        self.obu = None
        self.v2x_manager = None
        if config_yaml:
            v2x_config = config_yaml.get('v2x', {})
        else:
            v2x_config = None

        if len(v2x_config) > 0:
            self.v2x_manager = V2XManager(self, 0, vehicle.id, cav_world, config_yaml=v2x_config)
            self.v2x_manager.ego_car = 0
            self.obu = OBU(self.v2x_manager, vehicle, cav_world=cav_world, config_yaml=v2x_config)

        self.cav_world = cav_world
        self.cav_world.add_traffic_vehicle_manager(self)


    def update_vehicle_state(self, position: Tuple[float, float, float] = None,
                             orientation: Tuple[float, float, float] = None, speed: float = None,
                             acceleration: float = None, control_commands: Dict[str, float] = None,
                             sensors_data: Dict[str, Union[float, bool, Dict]] = None, sim_time: float = None):
        """更新车辆状态"""
        self.vehicle.manual_update_state(position, orientation, speed, acceleration, control_commands, sensors_data, sim_time)
        self.v2x_manager.update_info([self.vehicle.x,self.vehicle.y,self.vehicle.yaw],self.vehicle.speed)
        logger.info(f"车辆 {self.vehicle.id} 的状态已更新。")

    def apply_control(self, throttle: float = 0, brake: float = 0, steer: float = 0):
        """为车辆应用控制命令"""
        self.vehicle.apply_control(throttle, brake, steer)
        # logger.info(f"为车辆 {self.vehicle.id} 应用控制命令：油门={throttle}, 刹车={brake}, 转向={steer}")

    def update_position(self, delta_time: float):
        """模拟车辆运动"""
        self.vehicle.update_position(delta_time)
        self.v2x_manager.update_info([self.vehicle.x,self.vehicle.y,self.vehicle.yaw],self.vehicle.speed)

    def detect_collision(self, collision_force: float):
        """为车辆检测碰撞"""
        self.vehicle.detect_collision(collision_force)
        logger.info(f"车辆 {self.vehicle.id} 检测到碰撞，碰撞力={collision_force}")

    # def logger.info_vehicle_history(self, limit: int = 5):
    #     """打印车辆的历史记录"""
    #     self.vehicle.logger.info_history(limit)

    def plot_vehicle_trajectory(self):
        """绘制车辆的轨迹"""
        self.vehicle.plot_trajectory()
        logger.info(f"车辆 {self.vehicle.id} 的轨迹已绘制并保存为图片。")

    def get_vehicle_info(self) -> Dict:
        """获取车辆的当前信息"""
        return self.vehicle.get_vehicle_info()

    def save_vehicle_history(self, file_path: str):
        """将车辆的历史记录保存到JSON文件"""
        self.vehicle.save_history(file_path)
        logger.info(f"车辆 {self.vehicle.id} 的历史记录已保存到 {file_path}")

    def get_vehicle_id(self) -> str:
        """获取车辆的唯一ID"""
        return self.vehicle_id

# 测试代码
if __name__ == "__main__":
    # 创建车辆对象
    vehicle = Vehicle()
    cav_world = CavWorld()


    # 创建车辆管理实例
    manager = EgoVehicleManager(vehicle, cav_world=cav_world)

    # 更新车辆状态
    manager.update_vehicle_state(position=(10, 20, 0), speed=15.0, acceleration=3.0, sim_time=10.0)

    # 应用控制命令
    manager.apply_control(throttle=0.5, brake=0.0, steer=0.1)

    # 检测碰撞
    manager.detect_collision(collision_force=0.8)

    # 打印车辆历史记录
    manager.logger.info_vehicle_history(limit=3)

    # 绘制车辆轨迹
    manager.plot_vehicle_trajectory()

    # 获取车辆信息
    vehicle_info = manager.get_vehicle_info()
    logger.info(f"车辆信息： {vehicle_info}")

    # 获取车辆ID
    vehicle_id = manager.get_vehicle_id()
    logger.info(f"车辆的ID是： {vehicle_id}")

    # 保存车辆历史记录
    manager.save_vehicle_history('vehicle_history.json')
