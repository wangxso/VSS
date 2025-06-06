# V2X应用 FCW 前向碰撞预警
import json
import time
from loguru import logger
import math
from utils import cal_ttc, mmap_sender
from .appsys import V2XApplication
import os
from db import command


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
        ego_id = vehicle.vehicle_id
        vehicle = vehicle.vehicle
        ego_x = vehicle.x
        ego_y = vehicle.y
        ego_yaw = vehicle.yaw
        ego_speed = vehicle.speed
        throttle = 45
        brake = 0
        # logger.error(f"Vehicle {vehicle.id} position: {ego_x}, {ego_y}, {ego_yaw}, {ego_speed}")
        # 1. 接收消息（BSM、RSM）
        for msg in bsm_list:
            if vehicle.id == 0 or vehicle.id == '0' or int(msg["id"].decode("utf-8")) == 0:
                continue
            obj_x = msg['lat']
            obj_y = msg['long']
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
            V_error = math.sqrt(math.pow(y_axle_speed_offset,2)+math.pow(x_axle_speed_offset,2)) + 1e-17
            TTC = distance/V_error
            if  distance < 30:#判断同向车道的车辆位置、车灯状态
                if (3 < TTC < 5):
                    throttle = 0
                    brake = 50
                    logger.warning(f'egoid {vehicle.id} to vehicle {int(msg["id"].decode("utf-8"))} FCW: TTC {TTC}')
                    break
                elif TTC < 3:
                    throttle = 0
                    brake = 75
                    logger.warning(f'egoid {vehicle.id} to vehicle {int(msg["id"].decode("utf-8"))} FCW: TTC {TTC}')
                    break
        rsm_list.sort(key=lambda rsm: rsm['id'], reverse=True)
        for rsm in rsm_list:
            rsm_id = rsm['id'].decode("utf-8")
            if rsm_id == '00010086':
                throttle = 100
                brake = 0
                break
            participant_list = rsm['participants']
            for participant in participant_list:
                participant_id = participant['id']
                participant_y = participant['position']['lon']
                participant_x = participant['position']['lat']
                participant_yaw = participant['heading']
                participant_speed = participant['speed']
                participant_yaw = (360-participant_yaw+90)
                if participant_yaw>=360:
                    participant_yaw -= 360
                x_offset = abs(participant_x - ego_x)
                y_offset = abs(participant_y - ego_y)
                distance = math.sqrt(math.pow(x_offset,2)+math.pow(y_offset,2))
                #把traffic的坐标转成主车ego坐标
                y_axle_speed_offset = ego_speed*math.sin(ego_yaw) - participant_speed*math.sin(participant_yaw/180*3.14159)
                x_axle_speed_offset = ego_speed*math.cos(ego_yaw) - participant_speed*math.cos(participant_yaw/180*3.14159)
                V_error = math.sqrt(math.pow(y_axle_speed_offset,2)+math.pow(x_axle_speed_offset,2)) + 1e-17
                TTC = distance/V_error
                if  distance < 30:#判断同向车道的车辆位置、车灯状态
                    if (7 < TTC < 10):
                        throttle = 0
                        brake = 50
                        logger.warning(f'egoid {vehicle.id} to participant {int(participant_id.decode("utf-8"))} FCW: TTC {TTC}')
                        break
                    elif TTC < 7:
                        throttle = 0
                        brake = 90
                        logger.warning(f'egoid {vehicle.id} to participant {int(participant_id.decode("utf-8"))} FCW: TTC {TTC}')
                        break
        
        vehicle.apply_control(throttle/100, brake/100, 0)
        vehicle.update_position(0.1)
        dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        # with open(os.path.join(dir, 'command'),'a') as f:
        #     f.write(f'{vehicle.id},{vehicle.speed},{0.1}\n')
        control_command = {
            'command': 'traffic_control',
            'throttle': throttle,
            'brake': brake,
            'steer': 0,
            'speed' : vehicle.speed,
        }

        target_vehicle_id = vehicle.id
        # # logger.error(f"Vehicle {vehicle.id} control command: {control_command}")
        # logger.error(f'Send Command >>>> vehicle {vehicle.id} command: {vehicle.control_commands}, or_speed: {ego_speed}, speed: {vehicle.speed}')
        # vehicle.obu.send_command(target_vehicle_id, control_command)
        command.send_command(vehicle.id, control_command['command'], control_command['throttle'], control_command['brake'], control_command['steer'], control_command['speed'])
