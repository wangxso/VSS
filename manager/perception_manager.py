# Author: 1181110317 <1181110317@qq.com>

import numpy as np

# 现在只有获取模拟器数据的方法
class PerceptionManager:
    def __init__(self, vehicle, cav_world):
        """
        初始化 Perception 管理类
        """
        self.camera = None
        self.lidar = None
        self.use_model = False

        self.vehicle = vehicle
        self.cav_world = cav_world

    def detect(self):
        objects = []
        if self.use_model:
            objects = self.use_model_detect(objects)

        else:
            objects = self.use_server_information(objects, detect_range=50)

        print(f'检测到的障碍物列表：{objects}')
        return objects
    
    def use_server_information(self, objects, detect_range=100):


        vehicle_manager_dict = self.cav_world.get_all_vehicle_managers()

        temp_dict = vehicle_manager_dict['ego']
        temp_dict.update(vehicle_manager_dict['traffic'])

        for vid, vm in temp_dict.items():

            if vid == self.vehicle.id:
                continue

            ego_pos = [self.vehicle.x, self.vehicle.y]
            target_pos = [vm.vehicle.x, vm.vehicle.y]

            distance = self.compute_distance((ego_pos[0], ego_pos[1]), (target_pos[0], target_pos[1]))

            if distance < detect_range:
                obstacle_info = self.get_3d_obstacle_info(vm)
                objects.append(obstacle_info)

        return objects


    def compute_distance(self, location_1, location_2):
        """
        计算两点之间的欧几里得距离。
        """
        x = location_2[0] - location_1[0]
        y = location_2[1] - location_1[1]
        z = 0  # 假设高度为0，因为我们只考虑平面上的距离
        norm = np.linalg.norm([x, y, z]) + np.finfo(float).eps
        return norm
    
    def get_3d_obstacle_info(self, vehicle_manager):
        vehicle_info = vehicle_manager.get_vehicle_info()
        obstacle_info = {
            "id": vehicle_info["id"],
            "position": vehicle_info["position"],  # [x, y, z]
            "size": vehicle_info["size"],  # {'length': , 'width': , 'height': }
            "orientation": vehicle_info["orientation"],  # [yaw, pitch, roll]
            "lights_status": vehicle_info["lights_status"],
            "speed": vehicle_info["speed"],
            "acceleration": vehicle_info["acceleration"],
         }
        # 返回的格式符合3D目标检测的要求
        return obstacle_info
        
    def use_model_detect(self, objects):
        return None