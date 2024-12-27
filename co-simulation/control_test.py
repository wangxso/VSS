import numpy as np
from TrafficModelInterface import *
# from TrafficModelInterface import *
import math
import queue
from loguru import logger
import traffic_control

calibration_file = r'co-simulation\calibration_table.txt'
control = traffic_control.trafficControl(calibration_file)

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
    route = [route_type.straight, route_type.left, route_type.right, route_type.turn_round, route_type.unknown]
    change_lane_direction = [change_lane_direction.straight, change_lane_direction.left,change_lane_direction.right]
    # 重新生成待控制车辆
    if userData['rebuild'] == 0:
        deleteVehicle(userData['traffic_id'])
        userData['traffic_id'] = addVehicle(userData['traffic_x'], userData['traffic_y'], userData['traffic_speed'])
        userData['rebuild'] =1
    # 生成动作指令
    target_speed, duration, direction = control.control_to_action(userData['traffic_speed'],userData['traffic_throttle'],userData['traffic_brake'],userData['traffic_steer'])
    # 速度控制
    changeSpeed(userData['traffic_id'], target_speed, duration)
    # 方向控制
    changeLane(userData['traffic_id'], change_lane_direction[direction], duration)
    # 车辆路口场景判断(待测试通过路口情况)
    if getRoute(userData['traffic_id']) == next_junction_direction.unknown:
        valid_route = getValidDirections(getVehicleLane(userData['traffic_id']))
        if valid_route:
                changeRoute(userData['traffic_id'], Direction2Route[direction])

# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
