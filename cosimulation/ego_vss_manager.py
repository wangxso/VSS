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
import queue
from loguru import logger
class PID:
    def __init__(self, kp, ki, kd):
        self.kp = kp
        self.ki = ki
        self.kd = kd

        self.last_error = 0
        self.integral = 0

    def update(self, set_point, process_variable, dt):
        error = set_point - process_variable
        self.integral += error * dt
        derivative = (error - self.last_error) / dt
        output = self.kp * error + self.ki * self.integral + self.kd * derivative
        self.last_error = error
        return output

q = queue.Queue()
    

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
    
    # 短接部分控制信号 油门
    userData['ego_throttle'] = BusAccessor(userData['busId'],'ego_control.throttle','time@i,valid@b,throttle@d') 
    # 短接部分控制信号 刹车
    userData['ego_brake'] = BusAccessor(userData['busId'],'ego_control.brake','time@i,valid@b,brake@d') 
    # 短接部分控制信号 方向盘
    userData['ego_steer'] = BusAccessor(userData['busId'],'ego_control.steer','time@i,valid@b,steer@d') 

    # 初始化PID控制器
    # userData["pid"] = PID(kp=1, ki=0.0, kd=0.0) #PID(kp=1, ki=0.1, kd=0.5)
    userData["pid"] = PID(kp=1, ki=0.1, kd=0.5)
    userData["pid1"] = PID(kp=1, ki=0.1, kd=0.5)

    # 主车的速度
    userData["HV_Speed"] = 0.0
    userData["last_time"] = 0
    userData["control"] = []
    userData["queue"] = q

def ego_control(throttle, brake, steer):
    q.put(('ego_control', throttle, brake, steer))

# 每个仿真周期(10ms)回调
def ModelOutput(userData):
    # 1. 主车控制信号发送
    try:
        # 从队列中取出元组
        command, throttle, brake, steer = q.get(timeout=1)  # 设置timeout避免无限阻塞
        logger.info(f"Command: {command}, Throttle: {throttle}, Brake: {brake}, Steer: {steer}")
        
        # 标记任务完成
        q.task_done()
    except queue.Empty:
        logger.info("Queue is empty, no items to get.")

    if command == 'ego_control':
        userData['ego_throttle'].writeHeader(*(userData['time'], 1, throttle))
        userData['ego_brake'].writeHeader(*(userData['time'], 1, brake))
        userData['ego_steer'].writeHeader(*(userData['time'], 1, steer))


# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
