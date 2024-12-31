
# V2X应用 FCW 前向碰撞预警
from loguru import logger
import math
from utils import cal_ttc, mmap_sender
from .appsys import V2XApplication
'''
vehicle:
    id: 1
    x: 0
    y: 0
    z: 0
    yaw: 0
    speed: 0
    acceleration: 0
    jerk: 0
    steer: 0
    throttle: 0
    brake: 0
    lane: 0
    lane_change: 0
'''
class FCW(V2XApplication):
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.name = 'FCW'
    

    def proc(self, message_list):
        ego_x =  self.vehicle.x
        ego_y =  self.vehicle.y
        ego_speed = self.vehicle.speed
        ego_yaw = self.vehicle.yaw
        logger.error(f"FCW start {message_list}")
        # # 1. 接收消息（BSM、RSM）
        # for msg in message_list:
        #     if msg['type'] == 'BSM':
        #         obj_x = msg['x']
        #         obj_y = msg['y']
        #         obj_yaw = msg['yaw']
        #         obj_speed = msg['speed']
        #         longitudinal_offset = abs(ego_x-obj_x)
        #         lateral_offset = abs(ego_y-obj_y)
        #         distance = math.sqrt(math.pow(longitudinal_offset,2)+math.pow(lateral_offset,2))
        #         #把traffic的坐标转成主车ego坐标
        #         obj_yaw = (360-obj_yaw+90)
        #         if obj_yaw>=360:
        #             obj_yaw -= 360  
        #         y_axle_speed_offset = ego_speed*math.sin(ego_yaw) - obj_speed*math.sin(obj_yaw/180*3.14159)
        #         x_axle_speed_offset = ego_speed*math.cos(ego_yaw) - obj_speed*math.cos(obj_yaw/180*3.14159)
        #         V_error = math.sqrt(math.pow(y_axle_speed_offset,2)+math.pow(x_axle_speed_offset,2))
        #         TTC = distance/V_error
        #         if  distance < 30 and abs(ego_yaw*180/3.14159-obj_yaw)<15:#判断同向车道的车辆位置、车灯状态
        #             if (3 < TTC < 5):
        #                 throttle = 0
        #                 brake = 2.5
        #                 logger.warning(f'FCW: {TTC}')
        #             elif TTC < 3:
        #                 throttle = 0
        #                 brake = 15
        #                 logger.warning(f'FCW: {TTC}')
        # control_command = {
        #     'command': 'traffic_control',
        #     'throttle': throttle,
        #     'brake': brake,
        #     'steer': 0,
        #     'lane_change': 0
        # }    
        # mmap_sender(control_command)

if __name__ == "__main__":
    print('hello')