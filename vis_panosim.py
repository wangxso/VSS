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
import time
import time
import csv
import cv2
import matplotlib.pyplot as plt


height = 320
width = 180
def Warning(userData,level,warn):
    bus = userData["warning"].getBus()
    size = userData["warning"].getHeaderSize()
    bus[size:size + len(warn)] = '{}'.format(warn).encode()
    userData["warning"].writeHeader(*(userData["time"], level, len(warn)))

# 仿真实验启动时回调
def ModelStart(userData):
    # 构造雷达总线读取器
    userData['Cam0'] = BusAccessor(userData['busId'], 'MonoCameraSensor.0', f'time@i,{height*width}@[,r@b,g@b,b@b')
    # BSM总线读取器
    # userData['V2X_BSM'] = BusAccessor(userData['busId'], 'V2X_BSM.0', 'time@i,100@[,id@i,delaytime@i,x@d,y@d,z@d,yaw@d,pitch@d,roll@d,speed@d')
    
    

brake = 0
speed_max =0
# 每个仿真周期(10ms)回调
def ModelOutput(userData):
    timestamp = int(time.time())

    
    plt.clf()
    plt.title('Sensor: Mono Camera')
    plt.imshow(np.frombuffer(userData['Cam0'].getBus()[8:], dtype=np.uint8).reshape((width, height, 3)))
    plt.pause(interval=0.0001)





        
    
    

    


    # print("Saved point cloud to pointcloud{}.pcd".format(timestamp))


    time.sleep(1)
# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
