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
import traffic_control

    


# 仿真实验启动时回调
def ModelStart(userData):

    # 交通参与物信息读取，type==1为行人,type==0为车辆
    userData['traffic'] = DoubleBusReader(userData['busId'],'traffic','time@i,100@[,id@i,type@b,shape@i,x@f,y@f,z@f,yaw@f,pitch@f,roll@f,speed@f') 
    # BSM总线读取器
    userData['V2X_BSM'] = BusAccessor(userData['busId'], 'V2X_BSM.0', 'time@i,100@[,id@i,delaytime@i,x@d,y@d,z@d,yaw@d,pitch@d,roll@d,speed@d')
    # 初始化交通车信息
    userData['traffic_id'] = 101
    userData['traffic_x'] = 0
    userData['traffic_y'] = 0
    userData['traffic_yaw'] = 0
    userData['traffic_speed'] = 0
    calibration_file = r'co-simulation\calibration_table.txt'
    userData['traffic_control'] = traffic_control.trafficControl(calibration_file)


# 每个仿真周期(10ms)回调
def ModelOutput(userData):

    # 更新交通车信息
    bus_reader = userData['bus_traffic'].getReader(userData['time'])
    _, width = bus_reader.readHeader()
    for i in range(width):
        if i == userData['traffic_id']:
            id,ty,shape,x,y,z,yaw,pitch,roll,speed = bus_reader.readBody(i)
            userData['traffic_x'] = x
            userData['traffic_y'] = y
            userData['traffic_yaw'] = yaw
            userData['traffic_speed'] = speed

    triggle = 0
    
    # 控制交通车
    throttle = 0
    brake= 0
    steer = 0
    target_speed, duration, direction = userData['traffic_control'].control_to_action(userData['traffic_speed'],throttle,brake,steer)
    # 变速
    changeSpeed(userData['traffic_id'], target_speed, duration)
    # 变道
    changeLane(id, direction, duration)
    pass


# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
