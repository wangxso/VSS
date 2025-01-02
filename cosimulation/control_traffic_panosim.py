import os
import re
import sqlite3
import time
import numpy as np
from TrafficModelInterface import *
# from TrafficModelInterface import *
import math
import queue
from loguru import logger
import json
import traffic_control
import mmap
import msvcrt

calibration_file = r'C:\PanoSimDatabase\Plugin\Agent\cosimulation\calibration_table'
control = traffic_control.trafficControl(calibration_file)

def get_latest_command(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取最新的指令
    cursor.execute('''
        SELECT id, command, throttle, brake, steer, timestamp
        FROM commands
        ORDER BY timestamp DESC
        LIMIT 1
    ''')

    row = cursor.fetchone()
    if row:
        command_data = {
            'id': row[0],
            'command': row[1],
            'throttle': row[2],
            'brake': row[3],
            'steer': row[4],
            'timestamp': row[5]
        }
        conn.close()

        return command_data
    else:
        conn.close()
        return None


def get_target_lane(vehicle_lane, direction):
    if direction == 1:
        return getLeftLane(vehicle_lane)
    elif direction == 2:
        return getRightLane(vehicle_lane)
    else:
        return None



# 仿真实验启动时回调
def ModelStart(userData):
    # 初始化待控制交通车信息
    userData['traffic_id'] = 109
    userData['traffic_x'] = 0.0
    userData['traffic_y'] = 0.0
    userData['traffic_yaw'] = 0.0
    userData['traffic_speed'] = 0.0
    userData['rebuild'] = 0
    
    
    
# 每个仿真周期(10ms)回调
def ModelOutput(userData):
    route = [route_type.straight, route_type.left, route_type.right, route_type.turn_round, route_type.unknown]
    lane_direction = [change_lane_direction.straight, change_lane_direction.left,change_lane_direction.right]
    junction_direction = [next_junction_direction.straight, next_junction_direction.left, next_junction_direction.right,next_junction_direction.u_turn]
    # 车辆状态更新
    userData['traffic_x'] = getVehicleX(userData['traffic_id'])
    userData['traffic_y'] = getVehicleY(userData['traffic_id'])
    userData['traffic_yaw'] = getVehicleYaw(userData['traffic_id'])
    userData['traffic_speed'] = getVehicleSpeed(userData['traffic_id'])
    # 重新生成待控制车辆
    if userData['rebuild'] == 0:
        deleteVehicle(userData['traffic_id'])
        userData['traffic_id'] = addVehicle(userData['traffic_x'], userData['traffic_y'], userData['traffic_speed'])
        userData['rebuild'] =1
    # 1. 主车控制信号发送
    # 从队列中取出元组
    data = get_latest_command(r'C:\PanoSimDatabase\Plugin\Agent\commands.db')  # 设置timeout避免无限阻塞
    if data != None:
        command = data['command']
        throttle = data['throttle']
        brake = data['brake']
        steer = data['steer']
    else:
         return
    if command == 'traffic_control':
        # 生成动作指令
        target_speed, duration, direction = control.control_to_action(userData['traffic_speed'], throttle , brake, steer)
        # 1.主车控制信号发送
        changeSpeed(userData['traffic_id'], target_speed, duration)
        # 2.主车车道变化判断
        valid_lane = get_target_lane(getVehicleLane(userData['traffic_id']), direction)
        if valid_lane:
            changeLane(userData['traffic_id'], lane_direction[direction], 3)
        # 3.车辆路口场景判断
        if getRoute(userData['traffic_id']) == next_junction_direction.unknown:
            valid_routes = getValidDirections(getVehicleLane(userData['traffic_id']))
            # 路口可通行
            if valid_routes:
                # 直行优先
                if junction_direction[0] in valid_routes:
                    changeRoute(userData['traffic_id'], route[0])
                # 右转次优
                elif junction_direction[2] in valid_routes:
                    changeRoute(userData['traffic_id'], route[2])
                # 左转
                elif junction_direction[1] in valid_routes:
                    changeRoute(userData['traffic_id'], route[1])
                # 掉头
                elif junction_direction[3] in valid_routes:
                    changeRoute(userData['traffic_id'], route[3])
            # 死路
            else:
                stopVehicleInJunction(userData['traffic_id'], 0.5)

# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
