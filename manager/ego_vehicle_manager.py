# Author: 1181110317 <1181110317@qq.com>

import uuid
from typing import Dict, List, Union, Tuple
from manager.v2x_manager import V2XManager
from manager.world_manager import  CavWorld

import time
import json
import matplotlib.pyplot as plt

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.vehicle import Vehicle  # Vehicle 类已经定义
from entities.obu import OBU
from perception.perception_manager import PerceptionManager

# class EGOVehicleManager:
#     """
#     通用车辆管理类，用于整合车辆的各个模块（感知、控制、行为规划等）。
#     """

#     def __init__(self, vehicle: Vehicle, config_yaml: Dict, application: List[str], current_time='', data_dumping=False):
#         """
#         初始化方法，整合车辆管理各模块。

#         参数
#         ----------
#         vehicle : Vehicle
#             车辆对象。

#         config_yaml : dict
#             配置字典。

#         application : list
#             应用类别。

#         current_time : str
#             仿真开始时间。

#         data_dumping : bool
#             是否导出数据。
#         """
#         self.vehicle = vehicle
#         self.vid = vehicle.id

#         # 获取模块配置
#         map_config = config_yaml.get('map_manager', {})
#         v2x_config = config_yaml.get('v2x', {})
#         behavior_config = config_yaml.get('behavior', {})
#         control_config = config_yaml.get('controller', {})
#         safety_config = config_yaml.get('safety_manager', {})
#         localization_config = config_yaml.get('localization', {})
#         perception_config = config_yaml.get('perception', {})

#         # 初始化感知模块
#         self.perception_manager = self._init_perception_manager(perception_config)

#         # 初始化安全管理模块
#         self.safety_manager = self._init_safety_manager(safety_config)

#         # 初始化行为规划代理
#         self.agent = self._init_behavior_agent(application, behavior_config)

#         # 初始化控制模块
#         self.controller = self._init_control_manager(control_config)

#         # 初始化地图管理模块
#         self.map_manager = self._init_map_manager(map_config)

#         # 初始化定位模块
#         self.localization_manager = self._init_localization_manager(localization_config)

#         # 初始化V2X模块
#         self.v2x_manager = self._init_v2x_manager(v2x_config)

#         # 如果需要数据导出，初始化数据导出器
#         self.data_dumper = self._init_data_dumper(data_dumping, current_time)

#     def _init_map_manager(self, config: Dict):
#         """初始化地图管理模块"""
#         return MapManager(config)  # 示例类，需具体实现

#     def _init_localization_manager(self, config: Dict):
#         """初始化定位模块"""
#         return LocalizationManager(config)  # 示例类，需具体实现

#     def _init_v2x_manager(self, config: Dict):
#         """初始化V2X模块"""
#         return V2XManager(config)  # 示例类，需具体实现

#     def _init_perception_manager(self, config: Dict):
#         """初始化感知模块，具体实现可以根据需求扩展"""
#         return None

#     def _init_safety_manager(self, config: Dict):
#         """初始化安全管理模块，具体实现可以根据需求扩展"""
#         return None

#     def _init_behavior_agent(self, application: List[str], config: Dict):
#         """初始化行为规划代理，具体实现可以根据需求扩展"""
#         if 'platooning' in application:
#             return PlatooningBehaviorAgent(config)
#         return BehaviorAgent(config)

#     def _init_control_manager(self, config: Dict):
#         """初始化控制模块"""
#         return ControlManager(config)

#     def _init_data_dumper(self, data_dumping: bool, current_time: str):
#         """初始化数据导出器"""
#         if data_dumping:
#             return DataDumper(self.vehicle, save_time=current_time)
#         return None

#     def set_destination(self, start_location: Tuple[float, float], end_location: Tuple[float, float], clean=False, end_reset=True):
#         """
#         设置全局路线。
#         """
#         if self.agent:
#             self.agent.set_destination(start_location, end_location, clean, end_reset)

#     def update_info(self):
#         """
#         调用感知模块获取周围信息，并更新车辆状态。
#         """
#         # 定位与感知
#         ego_pos = self.localization_manager.get_position() if self.localization_manager else None
#         ego_spd = self.vehicle.get_vehicle_info()['speed']

#         if self.perception_manager:
#             objects = self.perception_manager.detect(ego_pos)
#         else:
#             objects = []

#         # 地图管理更新
#         if self.map_manager:
#             self.map_manager.update(ego_pos)

#         # V2X通信
#         if self.v2x_manager:
#             self.v2x_manager.update_info(ego_pos, ego_spd)
#             v2x_data = self.v2x_manager.get_ego_pos()
#         else:
#             v2x_data = None

#         # 安全管理更新
#         if self.safety_manager:
#             self.safety_manager.update_info({'ego_pos': ego_pos, 'ego_speed': ego_spd, 'objects': objects, 'v2x_data': v2x_data})

#         # 行为代理更新
#         if self.agent:
#             self.agent.update_information(ego_pos, ego_spd, objects)

#         # 控制模块更新
#         if self.controller:
#             self.controller.update_info(ego_pos, ego_spd)

#     def run_step(self, target_speed=None):
#         """
#         执行一步导航。
#         """
#         target_speed, target_pos = None, None
#         if self.agent:
#             target_speed, target_pos = self.agent.run_step(target_speed)
#         control = self.controller.run_step(target_speed, target_pos) if self.controller else {}

#         # 导出数据
#         if self.data_dumper:
#             self.data_dumper.run_step(self.vehicle, self.agent)

#         return control



class EgoVehicleManager:
    def __init__(self, vehicle: Vehicle, cav_world: CavWorld, config_yaml: Dict = None):
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
            self.v2x_manager = V2XManager(self, vehicle.id, cav_world, config_yaml=v2x_config)
            self.v2x_manager.ego_car = 1
            self.obu = OBU(self.v2x_manager, vehicle, cav_world=cav_world, config_yaml=v2x_config)

        
        self.cav_world = cav_world
        self.cav_world.set_ego_vehicle_manager(self)


    def update_vehicle_state(self, position: Tuple[float, float, float] = None,
                             orientation: Tuple[float, float, float] = None, speed: float = None,
                             acceleration: float = None, control_commands: Dict[str, float] = None,
                             sensors_data: Dict[str, Union[float, bool, Dict]] = None, sim_time: float = None):
        """更新车辆状态"""
        self.vehicle.manual_update_state(position, orientation, speed, acceleration, control_commands, sensors_data, sim_time)
        self.v2x_manager.update_info([self.vehicle.x,self.vehicle.y,self.vehicle.yaw],self.vehicle.speed)
        print(f"车辆 {self.vehicle.id} 的状态已更新。")

    def apply_control(self, throttle: float = 0, brake: float = 0, steer: float = 0):
        """为车辆应用控制命令"""
        self.vehicle.apply_control(throttle, brake, steer)
        # print(f"为车辆 {self.vehicle.id} 应用控制命令：油门={throttle}, 刹车={brake}, 转向={steer}")

    def update_position(self, delta_time: float):
        """模拟车辆运动"""
        self.vehicle.update_position(delta_time)
        self.v2x_manager.update_info([self.vehicle.x,self.vehicle.y,self.vehicle.yaw],self.vehicle.speed)

    def detect_collision(self, collision_force: float):
        """为车辆检测碰撞"""
        self.vehicle.detect_collision(collision_force)
        print(f"车辆 {self.vehicle.id} 检测到碰撞，碰撞力={collision_force}")

    def print_vehicle_history(self, limit: int = 5):
        """打印车辆的历史记录"""
        self.vehicle.print_history(limit)

    def plot_vehicle_trajectory(self):
        """绘制车辆的轨迹"""
        self.vehicle.plot_trajectory()
        print(f"车辆 {self.vehicle.id} 的轨迹已绘制并保存为图片。")

    def get_vehicle_info(self) -> Dict:
        """获取车辆的当前信息"""
        return self.vehicle.get_vehicle_info()

    def save_vehicle_history(self, file_path: str):
        """将车辆的历史记录保存到JSON文件"""
        self.vehicle.save_history(file_path)
        print(f"车辆 {self.vehicle.id} 的历史记录已保存到 {file_path}")

    def get_vehicle_id(self) -> str:
        """获取车辆的唯一ID"""
        return self.vehicle_id
    

    # def update(self, delta_time=0.1):
        
    #     print('===========================================================================================================================================================')
        

    #     # 仿真
    #     # self.update_vehicle_state()

    #     # 模拟车辆运行
    #     self.update_position(delta_time)

    #     # 获取感知数据
    #     objects = self.perception_manager.detect()

    #     # 更新v2x连接
    #     self.obu.update()

    #     # 获取v2x连接图
    #     list_connections = self.obu.get_list_connections()

    #     print(len(self.v2x_manager.cav_nearby))
    #     print(f"当前连接数量：{len(list_connections)}")
    #     for target_id, connection_type in list_connections.items():
    #         print(f"目标 ID: {target_id}, 连接类型: {connection_type}")

    #     # 发送v2x消息到信道
    #     self.obu.send_v2x_message(objets=objects)

    #     # 读取收到的v2x消息
    #     self.obu.process_region_messages()

    #     # 根据消息进行处理等
    #     self.obu.process_received_messages()

    #     print('===========================================================================================================================================================')



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
    manager.print_vehicle_history(limit=3)

    # 绘制车辆轨迹
    manager.plot_vehicle_trajectory()

    # 获取车辆信息
    vehicle_info = manager.get_vehicle_info()
    print(f"车辆信息： {vehicle_info}")

    # 获取车辆ID
    vehicle_id = manager.get_vehicle_id()
    print(f"车辆的ID是： {vehicle_id}")

    # 保存车辆历史记录
    manager.save_vehicle_history('vehicle_history.json')
