#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   aeb.py
@Time    :   2021/08/13
@Author  :   hf
@Version :   1.0
'''

import numpy as np
from DataInterfacePython import *
import math
# from V2X_sensor import V2X_sensor
from manager.ego_vehicle_manager import EgoVehicleManager
from manager.traffic_vehicle_manager import TrafficVehicleManager
from manager.world_manager import CavWorld
from entities.vehicle import Vehicle
def threshold(ego_v):
    time = 2.5
    if (40 < ego_v <= 60):
        time = 4
    if (60<ego_v <= 80):
        time = 5
    if (80<ego_v <= 100):
        time = 6
    if (100<ego_v):
        time = 7
    return time
# 计算TTC
def cal_ttc(s, v):
    v = v / 3.6
    ttc = 15
    if v < 0.1:
        ttc = - (s-4) / v
    if ttc > 15:
        ttc = 15
    # if s < 9:
    #     ttc = 0
    return ttc

# 计算横向偏差
def aim_distance(lane_all, Vx_Host):
    a = (lane_all[0][1] + lane_all[0][2]) / 2
    b = (lane_all[1][1] + lane_all[1][2]) / 2
    c = (lane_all[2][1] + lane_all[2][2]) / 2
    d = (lane_all[3][1] + lane_all[3][2]) / 2
    aim_x = Vx_Host * 0.7
    aim_y = b * (aim_x ** 2) + c * aim_x + d
    return aim_y

def Warning(userData,level,warn):
    bus = userData["warning"].getBus()
    size = userData["warning"].getHeaderSize()
    bus[size:size + len(warn)] = '{}'.format(warn).encode()
    userData["warning"].writeHeader(*(userData["time"], level, len(warn)))

# PID控制
class PID():
    def __init__(self, P = 0.45, I = 0.0, D=0.0):
        self.kp = P
        self.ki = I
        self.kd = D
        self.uPrevious = 0
        self.uCurent = 0
        self.setValue = 0
        self.lastErr = 0
        self.preLastErr = 0
        self.errSum = 0
        self.errSumLimit = 100
# 位置式PID
    def pidPosition(self, curValue):
        err = self.setValue - curValue
        dErr = err - self.lastErr
        self.preLastErr = self.lastErr
        self.lastErr = err
        self.errSum += err
        outPID = self.kp * err + (self.ki * self.errSum) + (self.kd * dErr)
        return outPID




# 仿真实验启动时回调
def ModelStart(userData):
    # 构造雷达总线读取器
    userData['Radar'] = BusAccessor(userData['busId'], 'Radar_ObjList_G.0','time@i,64@[,OBJ_ID@i,OBJ_Class@d,OBJ_Azimuth@d,OBJ_Elevation@d,OBJ_Velocity@d,OBJ_Range@d,OBJ_RCS@d')
    # 构造车道线传感器总线读取器
    userData['Laneline'] = BusAccessor(userData['busId'], 'MonoDetector_Lane.0',
                                       "Timestamp@i,4@[,Lane_ID@i,Lane_Distance@d,Lane_Car_Distance_Left@d,Lane_Car_Distance_Right@d,Lane_Curvature@d,Lane_Coefficient_C0@d,Lane_Coefficient_C1@d,Lane_Coefficient_C2@d,Lane_Coefficient_C3@d,Lane_Class@b")
    # 构造主车控制总线读取器
    userData['ego_control'] = BusAccessor(userData['busId'], 'ego_control',
                                          'time@i,valid@b,throttle@d,brake@d,steer@d,mode@i,gear@i')
    # 构造主车状态总线读取器1
    userData['ego_state'] = BusAccessor(userData['busId'], 'ego', 'time@i,x@d,y@d,z@d,yaw@d,pitch@d,roll@d,speed@d')
    # 构造主车状态总线读取器2
    userData['ego_extra'] = BusAccessor(userData['busId'], 'ego_extra',
                                        'time@i,VX@d,VY@d,VZ@d,AVx@d,AVy@d,AVz@d,Ax@d,Ay@d,Az@d,AAx@d,AAy@d,AAz@d')
    userData["warning"] = BusAccessor(userData['busId'], "warning", 'time@i,type@b,64@[,text@b')
    
    # BSM总线读取器
    userData['V2X_BSM'] = BusAccessor(userData['busId'], 'V2X_BSM.0', 'time@i,100@[,id@i,delaytime@i,x@d,y@d,z@d,yaw@d,pitch@d,roll@d,speed@d')
    
    # 初始化变量
    userData['last'] = 0
    userData['Vx'] = []
    userData['Time'] = []
    userData['i_term_last'] = 0
    userData['v_error_last'] = 0
    userData['steer'] = []
    userData['world_manager'] = CavWorld()
    userData['vehicle_instances'] = {}
    userData['traffic_manager_instances'] = {}
    userData['obstacles_instances'] = {}


# 每个仿真周期(10ms)回调
def ModelOutput(userData):
    Ts = 0.01
    # 读车辆状态（主车信息)
    ego_time, ego_x, ego_y, ego_z, ego_yaw, ego_pitch, ego_roll, ego_speed = userData['ego_state'].readHeader()
    _, valid_last, throttle_last, brake_last, steer_last, mode_last, gear_last = userData['ego_control'].readHeader()
    _, VX, VY, VZ, AVx, AVy, AVz, Ax, Ay, Az, AAx, AAy, AAz = userData['ego_extra'].readHeader()
    
    # 更新manager的内容
    userData['ego_manager'].update_vehicle_state((ego_x, ego_y, ego_z), (ego_yaw, ego_pitch, ego_roll), speed)
    
    if ego_time > userData['last']:
        userData['last'] = ego_time


    # 读取交通车信息(交通车信息)
    obj_attibutes = []
    obj_time, obj_width = userData['V2X_BSM'].readHeader()

    # (id,delay_time,x,y,z,yaw,pitch,roll,speed)
    for i in range(obj_width):
        id,delay_time,x,y,z,yaw,pitch,roll,speed = userData['V2X_BSM'].readBody(i)
        accel = getVehicleAccel(id) # 返回车辆当前加速度
        vehicle = get_or_create_vehicle(userData, id)
        tvm = get_or_create_tvm(userData, vehicle, userData['world_manager'])
        tvm.update_vehicle_state((x, y, z), (yaw, pitch, roll), speed, acceleration=accel, sim_time=userData['Time'])
        obj_attibutes.append((id, x, y, z, yaw, pitch, roll, speed))

    # 返回范围内障碍物信息
    # (2, -1.269, 1.733, 0.0, 0.0, 0.0, 0.0) 
    # shape, x, y, z, yaw, pitch, roll
    distance = 200
    obstacles = getObstacle(distance)
    for obstacle in obstacles:
        print(obstacle)


    # 获取所有交通车相关信息
    id_list = getVehicleList() # 返回所有车辆id列表
    for id in id_list:
        yaw = getVehicleYaw(id) # 返回车辆方向角
        x = getVehicleX(id) # 返回车辆x坐标
        y = getVehicleY(id) # 返回车辆y坐标
        speed = getVehicleSpeed(id) # 返回车辆速度
        offset = getVehicleLateralOffset(id) # 返回车辆横向偏移
        distance = getTotalDistance(id) # 返回车辆总行驶距离（暂不支持被接管车辆）
        type = getVehicleType(id) # 返回车辆类型
        
# 仿真实验结束时回调
def ModelTerminate(userData):
    pass


def get_or_create_vehicle(userData, id):
    if id not in userData['vehicle_instances']:
        userData['vehicle_instances'][id] = Vehicle(id)
    return userData['vehicle_instances'][id]

def get_or_create_tvm(userData, vehicle, cav_world):
    traffic_manager_instances = userData['traffic_manager_instances']
    vehicle_id = vehicle.id  # 使用 Vehicle 的 id 作为唯一标识

    # 如果实例已存在，直接返回
    if vehicle_id in traffic_manager_instances:
        return traffic_manager_instances[vehicle_id]

    # 如果实例不存在，创建并存储
    tvm = TrafficVehicleManager(vehicle=vehicle, cav_world=cav_world)
    traffic_manager_instances[vehicle_id] = tvm
    return tvm

def get_or_create_obstacle(userData):
    pass