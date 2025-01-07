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
import mmap
import msvcrt

import sys
import time

# 添加包所在的绝对路径
sys.path.append(r'C:\PanoSimDatabase\Plugin\Agent')

# 导入包
# from vss_panosim import world_manager

dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


calibration_file = r'C:\PanoSimDatabase\Plugin\Agent\cosimulation\calibration_table'

def receive_command(db_path, command_id=None):
    """
    从数据库接收命令。
    
    :param db_path: 数据库文件路径
    :param command_id: 要接收的命令ID，如果为None则返回所有命令
    :return: 命令列表或单个命令
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if command_id is not None:
        # 根据ID接收命令
        cursor.execute('''
            SELECT * FROM commands WHERE id = ?
        ''', (command_id,))
        command = cursor.fetchone()
        conn.close()
        return command
    else:
        # 获取最新的一条
        cursor.execute('''
            SELECT * FROM commands ORDER BY id DESC LIMIT 1
        ''')
        command = cursor.fetchone()
        conn.close()
        return command

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
    
new_car_map = {}    
    
# 每个仿真周期(10ms)回调
def ModelOutput(userData):
    route = [route_type.straight, route_type.left, route_type.right, route_type.turn_round, route_type.unknown]
    lane_direction = [change_lane_direction.straight, change_lane_direction.left,change_lane_direction.right]
    junction_direction = [next_junction_direction.straight, next_junction_direction.left, next_junction_direction.right,next_junction_direction.u_turn]

    
    # 重新生成待控制车辆
    if userData['rebuild'] == 0:
        vehicle_list = getVehicleList()
        print(f"车辆列表：{vehicle_list}")
        x,y,speed = 0.0,0.0,0.0
        for vehicle_id in vehicle_list:
            # 跳过RSU
            if vehicle_id == 0:
                continue
            x = getVehicleX(vehicle_id)
            y = getVehicleY(vehicle_id)
            speed = getVehicleSpeed(vehicle_id)
            deleteVehicle(vehicle_id)
            new_id = addVehicle(x, y, speed)
            # new_car_map[vehicle_id] = new_id
            print(f"生成车辆：{new_id,x, y, speed}")
        userData['rebuild'] =1

    
    with open(os.path.join(dir,'Agent','command'),'r') as f:
        for command in f.readlines():
            id,speed,duration = command.strip().split(',')
            if int(id) == 0:
                continue
            changeSpeed(int(id), float(speed), float(duration))
            logger.warning(f'{id} 速度改变为：{speed}')
        f.close()

    # # 1. 主车控制信号发送
    # # 从队列中取出元组
    # data = receive_command(r'C:\PanoSimDatabase\Plugin\Agent\commands.db')  # 设置timeout避免无限阻塞
    # # logger.error(f'Receive command >>>>>>>>>>> {data}')
    # # 从元组中取出元素
    # if data is not None:
    #     id = data[1]
    #     command = data[2]
    #     throttle = data[3]
    #     brake = data[4]
    #     steer = data[5]
    # else:
    #      return
    # if command == 'traffic_control':
    #     # 车辆状态更新
    #     vehicle_speed = getVehicleSpeed(id)
    #     # 生成动作指令
    #     target_speed, duration, direction = control.control_to_action(vehicle_speed, throttle , brake, steer)
    #     # logger.error(f'Control action >>>>>>>>>>> {vehicle_speed, target_speed, duration, direction}')
    #     # 1.主车控制信号发送
    #     changeSpeed(id, target_speed, duration)
    #     # 2.主车车道变化判断
    #     # valid_lane = get_target_lane(getVehicleLane(id), direction)
    #     # if valid_lane:
    #     #     changeLane(id, lane_direction[direction], 3)
    #     # 3.车辆路口场景判断
    #     # if getRoute(id) == next_junction_direction.unknown:
    #     #     valid_routes = getValidDirections(getVehicleLane(id))
    #     #     # 路口可通行
    #     #     if valid_routes:
    #     #         # 直行优先
    #     #         if junction_direction[0] in valid_routes:
    #     #             changeRoute(id, route[0])
    #     #         # 右转次优
    #     #         elif junction_direction[2] in valid_routes:
    #     #             changeRoute(id, route[2])
    #     #         # 左转
    #     #         elif junction_direction[1] in valid_routes:
    #     #             changeRoute(id, route[1])
    #     #         # 掉头
    #     #         elif junction_direction[3] in valid_routes:
    #     #             changeRoute(id, route[3])
    #     #     # 死路
    #     #     else:
    #     #         stopVehicleInJunction(id, 0.5)

# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
