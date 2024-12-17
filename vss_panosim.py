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
    
    print("-----This is the initialization of FCW_Python_V2X-----")
    

brake = 0
speed_max =0
# 每个仿真周期(10ms)回调
def ModelOutput(userData):
    global brake,speed_max
    Ts = 0.01
    # 读车辆状态
    ego_time, ego_x, ego_y, ego_z, ego_yaw, ego_pitch, ego_roll, ego_speed = userData['ego_state'].readHeader()
    _, valid_last, throttle_last, brake_last, steer_last, mode_last, gear_last = userData['ego_control'].readHeader()
    _, VX, VY, VZ, AVx, AVy, AVz, Ax, Ay, Az, AAx, AAy, AAz = userData['ego_extra'].readHeader()
    if ego_time > userData['last']:
        userData['last'] = ego_time
    # 读车道线传感器信息，lane_a, lane_b, lane_c, lane_d三次多项式系数降幂排列, y = a*x^3 + b*x^2 + c*x + d
    lane_time, lane_width = userData['Laneline'].readHeader()
    lane_coefs = []
    lane_types = []

    for i in range(lane_width):
        Lane_ID, Lane_Distance, Lane_Car_Distance_Left, Lane_Car_Distance_Right, Lane_Curvature, Lane_Coefficient_C0, Lane_Coefficient_C1, Lane_Coefficient_C2, Lane_Coefficient_C3, Lane_Class = \
        userData['Laneline'].readBody(i)
        lane_coefs.append([Lane_Coefficient_C3, Lane_Coefficient_C2, Lane_Coefficient_C1, Lane_Coefficient_C0])

    # 读取交通车信息
    obj_attibutes = []
    obj_time, obj_width = userData['V2X_BSM'].readHeader()

    for i in range(obj_width):
        id,delay_time,x,y,z,yaw,pitch,roll,speed = userData['V2X_BSM'].readBody(i)
        OBJ_X = x
        OBJ_Y = y
        OBJ_Re_Vx = speed
        OBJ_Azimuth = yaw
        obj_attibutes.append([OBJ_X, OBJ_Y, OBJ_Re_Vx,OBJ_Azimuth])

    delta = 0

    # 纵向初始值
    if userData['time'] / 1000 < 40:
        throttle = 0.13
    else:
        throttle = 0

    if obj_width > 0:
        for i in range(obj_width):
            Obj_x = obj_attibutes[i][0]
            Obj_y = obj_attibutes[i][1]
            Obj_speed = obj_attibutes[i][2]
            Obj_yaw = obj_attibutes[i][3]
            longitudinal_offset = abs(ego_x-Obj_x)
            lateral_offset = abs(ego_y-Obj_y)
            distance = math.sqrt(math.pow(longitudinal_offset,2)+math.pow(lateral_offset,2))
            
            #把traffic的坐标转成主车ego坐标
            obj_yaw = (360-Obj_yaw+90)
            if obj_yaw>=360:
                obj_yaw -= 360   
                
            y_axle_speed_offset = ego_speed*math.sin(ego_yaw) - Obj_speed*math.sin(obj_yaw/180*3.14159)
            x_axle_speed_offset = ego_speed*math.cos(ego_yaw) - Obj_speed*math.cos(obj_yaw/180*3.14159)
            V_error = math.sqrt(math.pow(y_axle_speed_offset,2)+math.pow(x_axle_speed_offset,2))
            TTC = distance/V_error
            print('ttc',TTC,V_error)

            if  distance < 30 and abs(ego_yaw*180/3.14159-obj_yaw)<15:#判断同向车道的车辆位置、车灯状态
                if (3 < TTC < 5):
                    throttle = 0
                    brake = 2.5
                    Warning(userData, 2, 'FCW')
                elif TTC < 3:
                    throttle = 0
                    brake = 15
                    Warning(userData, 2, 'FCW')
    # 从主车发送控制指令，valid = 1, throttle, brake, steer, mode=5自动挡, gear=0不控制挡位，由自动变速器控制
    valid = 1
    steer = delta
    mode = 5
    gear = 0
    userData['ego_control'].writeHeader(*(userData['time'], valid, throttle, brake, steer, mode, gear))



# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
