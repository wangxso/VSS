# Author: 1181110317 <1181110317@qq.com>

from collections import deque
import weakref
import numpy as np

communication_range = 500
from entities.rsu import RSU
from entities.vehicle import Vehicle


class V2XManager:
    """
    V2X模块管理器，支持车队控制、协作感知等功能。

    参数
    ----------
    vehicle_manager : object
        所属车辆管理器。

    config_yaml : dict
        V2X模块的配置字典。

    vid : str
        车辆管理器的唯一标识符。

    属性
    ----------
    cav_nearby : dict
        通信范围内的CAV字典。

    platooning_plugin : object
        用于车队通信的插件。

    ego_pos : deque
        车辆位置缓存。

    ego_spd : deque
        车辆速度缓存。
    """

    def __init__(self, entity_manager, type, id, cav_world, config_yaml=None, apply_plat=False):
        
        self.id = id
        self.cav_world = cav_world
        self.ego_car = 0

        # 初始化缓存
        self.cav_nearby = {}
        self.cav_nearby_comm = {}
        self._received_buffer = {}
        self.ego_pos = deque(maxlen=100)  # 存储位置的缓存队列
        self.ego_spd = deque(maxlen=100)  # 存储速度的缓存队列
        self.ego_dynamic_trace = deque()

        if type == 0:
            self.vehicle_manager = weakref.ref(entity_manager)()
            # 初始化
            self.ego_pos.append([self.vehicle_manager.vehicle.x,self.vehicle_manager.vehicle.y,self.vehicle_manager.vehicle.yaw])
            self.ego_spd.append(self.vehicle_manager.vehicle.speed)
            self.ego_dynamic_trace.append((
                [self.vehicle_manager.vehicle.x,self.vehicle_manager.vehicle.y,self.vehicle_manager.vehicle.yaw], self.vehicle_manager.vehicle.yaw, self.cav_world.global_clock
            ))

        
        if type == 1:
            self.rsu_manager = weakref.ref(entity_manager)()
            # 初始化
            self.ego_pos.append([self.rsu_manager.rsu.x,self.rsu_manager.rsu.y,self.rsu_manager.rsu.yaw])
            self.ego_spd.append(self.rsu_manager.rsu.speed)
            self.ego_dynamic_trace.append((
                [self.rsu_manager.rsu.x,self.rsu_manager.rsu.y,self.rsu_manager.rsu.yaw], self.rsu_manager.rsu.yaw, self.cav_world.global_clock
            ))


        

        # 初始化通信噪声与延迟配置
        if config_yaml:
            self.communication_range = config_yaml.get('communication_range', communication_range)
            self.loc_noise = config_yaml.get('loc_noise', 0.0)
            self.yaw_noise = config_yaml.get('yaw_noise', 0.0)
            self.speed_noise = config_yaml.get('speed_noise', 0.0)
            self.lag = config_yaml.get('lag', 0)
        else:
            self.communication_range = communication_range
            self.loc_noise = 0
            self.yaw_noise = 0
            self.speed_noise = 0
            self.lag = 0

    def update_info(self, ego_pos, ego_spd):
        """
        更新当前车辆位置信息，并刷新通信模块。
        参数：
        ego_pos: [x, y, yaw] 车辆位置列表
        ego_spd: float 车辆速度
        """
        self.ego_pos.append(ego_pos)
        self.ego_spd.append(ego_spd)
        self.ego_dynamic_trace.append((
            ego_pos, ego_spd, self.cav_world.global_clock
        ))
        self.cav_nearby = {}
        self.search_nearby_vehicles()

    def get_ego_pos(self):
        """
        获取当前车辆的位置，可选择是否加入噪声和延迟。
        返回：包含噪声的(x, y, yaw)
        """
        if not self.ego_pos:
            return None

        # 加入延迟
        ego_pos = self.ego_pos[0] if len(self.ego_pos) < self.lag else \
            self.ego_pos[-1 - int(abs(self.lag))]

        # 加入噪声
        x_noise = np.random.normal(0, self.loc_noise) + ego_pos[0]
        y_noise = np.random.normal(0, self.loc_noise) + ego_pos[1]
        yaw_noise = np.random.normal(0, self.yaw_noise) + ego_pos[2]

        return (x_noise, y_noise, yaw_noise)

    def get_ego_speed(self):
        """
        获取当前车辆的速度，可选择是否加入噪声和延迟。
        返回：包含噪声的速度值
        """
        if not self.ego_spd:
            return None

        # 加入延迟
        ego_speed = self.ego_spd[0] if len(self.ego_spd) < self.lag else \
            self.ego_spd[-1 - int(abs(self.lag))]

        # 加入噪声
        return np.random.normal(0, self.speed_noise) + ego_speed

    def search_nearby_vehicles(self):
        """
        搜索通信范围内的所有其他车辆。
        """

        self.cav_nearby = {}
        
        
        vehicle_manager_dict = self.cav_world.get_all_vehicle_managers()

        temp_dict = vehicle_manager_dict['ego']
        temp_dict.update(vehicle_manager_dict['traffic'])

        for vid, vm in temp_dict.items():
            if not vm.v2x_manager.get_ego_pos():
                continue

            if vid == self.id:
                continue

            ego_pos = self.ego_pos[-1]
            target_pos = vm.v2x_manager.ego_pos[-1]

            distance = self.compute_distance((ego_pos[0], ego_pos[1]), (target_pos[0], target_pos[1]))

            if distance < self.communication_range:
                self.cav_nearby.update({vid: vm})

    def search_nearby_vehicles_comm(self):
        """
        搜索通信范围内的所有可通信的其他车辆。
        """
        self.cav_nearby_comm = {}
        
        vehicle_manager_dict = self.cav_world.get_all_vehicle_managers()

        temp_dict = vehicle_manager_dict['ego']
        temp_dict.update(vehicle_manager_dict['traffic'])

        for vid, vm in temp_dict.items():
            if not vm.v2x_manager.get_ego_pos():
                continue
            
            if vid == self.id:
                continue

            if vm.obu == None:
                continue

            ego_pos = self.ego_pos[-1]
            target_pos = vm.v2x_manager.ego_pos[-1]

            distance = self.compute_distance((ego_pos[0], ego_pos[1]), (target_pos[0], target_pos[1]))

            if distance < self.communication_range:
                self.cav_nearby_comm.update({vid: vm})

    def compute_distance(self, location_1, location_2):
        """
        计算两点之间的欧几里得距离。
        """
        x = location_2[0] - location_1[0]
        y = location_2[1] - location_1[1]
        z = 0  # 假设高度为0，因为我们只考虑平面上的距离
        norm = np.linalg.norm([x, y, z]) + np.finfo(float).eps
        return norm


    '''
    =====================================================车队接口，暂时不需要=====================================================

    '''

    
    # def set_platoon(self, in_id, platooning_object=None, platooning_id=None, leader=False):
    #     """
    #     设置车队状态。

    #     参数
    #     ----------
    #     in_id : int
    #         在车队中的位置，例如0表示队长，1表示第二个车辆。

    #     platooning_object : object
    #         车队的管理对象，包含所有车队信息。

    #     platooning_id : int
    #         当前车辆所属车队的ID。

    #     leader : bool
    #         是否是车队的队长。
    #     """
    #     self.platooning_plugin.set_platoon(
    #         in_id, platooning_object, platooning_id, leader)

    # def set_platoon_status(self, status):
    #     """
    #     设置车队中的状态。

    #     参数
    #     ----------
    #     status : str
    #         当前车辆的车队状态。
    #     """
    #     self.platooning_plugin.set_status(status)

    # def get_platoon_status(self):
    #     """
    #     获取当前车辆的车队状态。

    #     返回
    #     ----------
    #     status : str
    #         当前车辆的车队状态。
    #     """
    #     return self.platooning_plugin.status

    # def match_platoon(self):
    #     """
    #     匹配最佳位置加入车队。

    #     返回
    #     ----------
    #     match_result : dict
    #         匹配结果。
    #     """
    #     return self.platooning_plugin.match_platoon(self.cav_nearby)

    # def in_platoon(self):
    #     """
    #     检查当前车辆是否在车队中。

    #     返回
    #     ----------
    #     flag : bool
    #         当前车辆是否在车队中。
    #     """
    #     return self.platooning_plugin.in_id is not None

    # def get_platoon_manager(self):
    #     """
    #     获取车队管理器对象及车辆在车队中的位置。

    #     返回
    #     ----------
    #     platoon_object : object
    #         车队管理器对象。

    #     in_id : int
    #         当前车辆在车队中的位置。
    #     """
    #     return self.platooning_plugin.platooning_object, self.platooning_plugin.in_id

    # def get_platoon_front_rear(self):
    #     """
    #     获取当前车辆在车队中的前后车辆。

    #     返回
    #     ----------
    #     front_vehicle : object
    #         当前车辆前方的车辆。

    #     rear_vehicle : object
    #         当前车辆后方的车辆。
    #     """
    #     return self.platooning_plugin.front_vehicle, self.platooning_plugin.rear_vehicle




# 测试代码
if __name__ == "__main__":
    # 执行测试
   v2x_manage = V2XManager()