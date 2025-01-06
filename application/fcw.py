
# V2X应用 FCW 前向碰撞预警
import json
import time
from loguru import logger
import math
from utils import cal_ttc, mmap_sender
from .appsys import V2XApplication
from db import send_command
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
    def __init__(self):
        self.name = 'FCW'
    

    def proc(self, message_list, vehicle):
        bsm_list = message_list['BSM']
        rsm_list = message_list['RSM']

        vehicle = vehicle.vehicle
        ego_x = vehicle.x
        ego_y = vehicle.y
        ego_yaw = vehicle.yaw
        ego_speed = vehicle.speed
        throttle = 0
        brake = 0
        # logger.error(f"Vehicle {vehicle.id} position: {ego_x}, {ego_y}, {ego_yaw}, {ego_speed}")
        # 1. 接收消息（BSM、RSM）
        for msg in bsm_list:
            obj_y = msg['lat']
            obj_x = msg['long']
            obj_yaw = msg['heading']
            obj_speed = msg['speed']
            x_offset = abs(obj_x - ego_x)
            y_offset = abs(obj_y - ego_y)

            distance = math.sqrt(math.pow(x_offset,2)+math.pow(y_offset,2))
            # logger.warning(f'ego id {vehicle.id} to traffic {msg["id"]} x_offset {x_offset}  y_offset {y_offset} distance: {distance}')
            #把traffic的坐标转成主车ego坐标
            obj_yaw = (360-obj_yaw+90)
            if obj_yaw>=360:
                obj_yaw -= 360  
            y_axle_speed_offset = ego_speed*math.sin(ego_yaw) - obj_speed*math.sin(obj_yaw/180*3.14159)
            x_axle_speed_offset = ego_speed*math.cos(ego_yaw) - obj_speed*math.cos(obj_yaw/180*3.14159)
            V_error = math.sqrt(math.pow(y_axle_speed_offset,2)+math.pow(x_axle_speed_offset,2))
            TTC = distance/V_error
            if  distance < 30:#判断同向车道的车辆位置、车灯状态
                if (3 < TTC < 5):
                    throttle = 0
                    brake = 100
                    logger.warning(f'egoid {vehicle.id} to vehicle {int(msg["id"].decode("utf-8"))} FCW: TTC {TTC}')
                    break
                elif TTC < 3:
                    throttle = 0
                    brake = 100
                    logger.warning(f'egoid {vehicle.id} to vehicle {int(msg["id"].decode("utf-8"))} FCW: TTC {TTC}')
                    break
        control_command = {
            'command': 'traffic_control',
            'throttle': throttle,
            'brake': brake,
            'steer': 0,
        }
        send_command(r'C:\PanoSimDatabase\Plugin\Agent\commands.db', control_command)

if __name__ == "__main__":
    print('hello')