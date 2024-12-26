# Author: 1181110317 <1181110317@qq.com>

import uuid
import time
import json
from typing import List, Tuple, Dict, Union
import matplotlib.pyplot as plt
import math
from entities.entity import Entity

class Vehicle(Entity):
    def __init__(self, vehicle_id: str = None, throttle_acceleration: float = 2.0, brake_deceleration: float = 5.0):
        """
        初始化车辆的属性，设定默认值。

        参数:
            vehicle_id (str, optional): 车辆ID，默认为None，如果未提供，自动生成一个唯一的UUID作为ID。
            throttle_acceleration (float): 油门加速度因子。
            brake_deceleration (float): 刹车减速度因子。
        """
        super().__init__(vehicle_id, entity_type="vehicle")

        # 车辆运动信息
        self.angular_velocity = 0.0

        # 车辆状态
        self.control_commands = {'throttle': 0.0, 'brake': 0.0, 'steer': 0.0}


        self.direction = 0.0  # 车辆的前进方向，以弧度表示
        self.steering_ratio = 1.0 # 转向比例因子，用于将转向变为方向变化
        self.max_steering_angle = math.radians(30)  # 最大转向角度，单位：弧度

        # 常量配置
        self.throttle_acceleration = throttle_acceleration
        self.brake_deceleration = brake_deceleration

        # 车的长宽 可以更改 这个随意
        self.length = 5              # 车辆长度（单位：1米）
        self.width = 2                # 车辆宽度（单位：1米）
        self.height = 2
        self.lights_status = 0       # 灯光

        # 历史记录与传感器数据
        self.history: List[Dict] = []
        self.sensors_data: Dict[str, Union[float, Tuple]] = {
            'collision': 0.0,
            'lane_invasion': False,
            'gps': (self.x, self.y, self.z),
            'imu': {'acceleration': 0.0, 'angular_velocity': 0.0}
        }

    def update_status(self, status: str):
        """更新车辆状态"""
        valid_statuses = ['active', 'inactive', 'maintenance']
        if status not in valid_statuses:
            raise ValueError(f"无效的状态: {status}. 必须为 {valid_statuses} 中的一个.")
        self.status = status

    def set_size(self, length: float, width: float):
        """改车辆尺寸"""
        self.length = length
        self.width = width

    def apply_control(self, throttle: float, brake: float, steer: float):
        """应用车辆控制命令"""
        if not (0.0 <= throttle <= 1.0):
            raise ValueError("油门值必须在 [0.0, 1.0] 范围内")
        if not (0.0 <= brake <= 1.0):
            raise ValueError("刹车值必须在 [0.0, 1.0] 范围内")
        if not (-1.0 <= steer <= 1.0):
            raise ValueError("转向值必须在 [-1.0, 1.0] 范围内")
        
        self.control_commands['throttle'] = throttle
        self.control_commands['brake'] = brake
        self.control_commands['steer'] = steer

    def manual_update_state(self, position: Tuple[float, float, float] = None,
                            orientation: Tuple[float, float, float] = None,
                            speed: float = None,
                            acceleration: float = None,
                            control_commands: Dict[str, float] = None,
                            sensors_data: Dict[str, Union[float, bool, Dict]] = None,
                            sim_time: float = None):
        """手动导入车辆的状态信息"""
        if position is not None:
            self.x, self.y, self.z = position
        if orientation is not None:
            self.yaw, self.pitch, self.roll = orientation
        if speed is not None:
            self.speed = speed
        if acceleration is not None:
            self.acceleration = acceleration
        if control_commands is not None:
            self.apply_control(**control_commands)
        if sensors_data is not None:
            self.sensors_data.update(sensors_data)

        self.sim_time = sim_time if sim_time is not None else time.time()

        self.current_time = time.time()

        self._update_sensors()
        self._record_history()


    def update_position(self, delta_time: float):
        """更新车辆位置，模拟车辆的运动"""
        self.sim_time += delta_time
        self.acceleration = self.control_commands['throttle'] * self.throttle_acceleration - \
                            self.control_commands['brake'] * self.brake_deceleration
        self.speed = max(0.0, self.speed + self.acceleration * delta_time)

        # 计算转向角，限制最大转向角
        steering_angle = self.clamp(self.control_commands['steer'] * self.steering_ratio, -self.max_steering_angle, self.max_steering_angle)

        # 更新车辆的前进方向
        self.direction += self.speed * math.tan(steering_angle) * delta_time

        # 根据速度和方向计算x和y的位移
        self.x += self.speed * math.cos(self.direction) * delta_time
        self.y += self.speed * math.sin(self.direction) * delta_time

        self.current_time = time.time()

        self._update_sensors()
        self._record_history()

    def clamp(self, value, min_value, max_value):
        return max(min_value, min(max_value, value))

    def detect_collision(self, collision_force: float):
        """模拟碰撞检测"""
        self.sensors_data['collision'] = collision_force
        if collision_force > 0.0:
            self.status = 'inactive'

    def lane_invasion(self, invaded: bool):
        """模拟车道线入侵检测"""
        self.sensors_data['lane_invasion'] = invaded

    def get_vehicle_info(self) -> Dict:
        """获取当前车辆的所有信息，包括尺寸、灯光状态等"""
        return {
            'id': self.id,
            'position': (self.x, self.y, self.z),
            'orientation': (self.yaw, self.pitch, self.roll),
            'speed': self.speed,
            'acceleration': self.acceleration,
            'status': self.status,
            'control_commands': self.control_commands,
            'sensors': self.sensors_data,
            'size': {'length': self.length, 'width': self.width, 'height': self.height},  # 添加尺寸信息
            'lights_status': self.lights_status  # 添加灯光状态信息
        }


    def get_history(self) -> List[Dict]:
        """获取车辆的历史记录"""
        return self.history

    def save_history(self, file_path: str):
        """将历史记录保存到JSON文件"""
        with open(file_path, 'w') as f:
            json.dump(self.history, f, indent=4)

    def print_history(self, limit: int = 5):
        """打印最近的历史记录"""
        print(f"\n最近 {limit} 条历史记录:")
        for record in self.history[-limit:]:
            print(record)

    def _record_history(self):
        """记录当前车辆的历史数据"""
        self.history.append({
            'time': self.sim_time,
            'position': (self.x, self.y, self.z),
            'orientation': (self.yaw, self.pitch, self.roll),
            'speed': self.speed,
            'acceleration': self.acceleration,
            'control': self.control_commands.copy(),
            'sensors': self.sensors_data.copy(),
            'lights_status': self.lights_status  # 添加灯光状态信息
        })

    def _update_sensors(self):
        """同步传感器数据"""
        self.sensors_data['gps'] = (self.x, self.y, self.z)
        self.sensors_data['imu'] = {'acceleration': self.acceleration, 'angular_velocity': self.angular_velocity}

    def receive_message(self, message: str):
        """接收来自RSU的消息"""
        print(f"车辆 {self.id} 收到来自RSU的消息: {message}")

    
    def plot_trajectory(self):
        """绘制轨迹"""
        positions = [(record['position'][0], record['position'][1]) for record in self.history]
        x_vals, y_vals = zip(*positions)

        plt.figure(figsize=(10, 6))
        plt.plot(x_vals, y_vals, label="轨迹")
        plt.scatter(x_vals[0], y_vals[0], color='green', label="起点")  # 起点
        plt.scatter(x_vals[-1], y_vals[-1], color='red', label="终点")   # 终点
        plt.title("车辆轨迹")
        plt.xlabel("X 位置")
        plt.ylabel("Y 位置")
        plt.legend()
        plt.grid(True)
        # plt.show()
        plt.savefig('vehicle_trajectory.png')

# 测试代码
if __name__ == "__main__":
    vehicle = Vehicle()
    print("初始车辆信息:", vehicle.get_vehicle_info())

    # 模拟车辆控制与移动
    import random

    for i in range(1000):
        vehicle.apply_control(throttle=random.uniform(0, 1), brake=random.uniform(0, 1), steer=random.uniform(-1, 1))
        vehicle.update_position(delta_time=0.01)
        print(f"第 {i+1} 次更新: ", vehicle.get_vehicle_info())

    # 模拟碰撞与车道入侵
    vehicle.detect_collision(50.0)
    vehicle.lane_invasion(True)
    print("\n发生碰撞与车道入侵后的车辆信息:")
    print(vehicle.get_vehicle_info())

    # 输出历史记录
    vehicle.print_history()
    vehicle.save_history("vehicle_history.json")

    vehicle.plot_trajectory()
