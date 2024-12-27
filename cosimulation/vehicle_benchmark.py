import numpy as np
from TrafficModelInterface import *
# from TrafficModelInterface import *
import math
import queue
from loguru import logger


# 仿真实验启动时回调
def ModelStart(userData):
    # 初始化待控制交通车信息
    userData['traffic_id'] = 109
    userData['traffic_x'] = 0
    userData['traffic_y'] = 0
    userData['traffic_yaw'] = 0
    userData['traffic_speed'] = 0.0
    userData['traffic_throttle'] = 0
    userData['traffic_brake'] = 0
    userData['traffic_steer'] = 0
    userData['rebuild'] = 0
    
    
    
# 每个仿真周期(10ms)回调
def ModelOutput(userData):
    # 随机生成x,y,speed
    
    for i in range(1000):
        x = np.random.randint(-100, 100)
        y = np.random.randint(-100, 100)
        speed  = np.random.randint(0, 100)
        userData['traffic_id'] = addVehicle(x, y, speed)
    

# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
