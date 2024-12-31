import numpy as np
from TrafficModelInterface import *
# from TrafficModelInterface import *
import math
import queue
from loguru import logger
import json
import traffic_control
import mmap


calibration_file = r'../Agent/cosimulation/calibration_table.txt'
control = traffic_control.trafficControl(calibration_file)
task_queue = queue.Queue()

def receiver():
    # 文件名和信号量
    filename = r"C:\PanoSimDatabase\Plugin\channel"
    
    # 打开并映射文件
    with open(filename, 'r+b') as f:
        # 映射整个文件到内存
        mm = mmap.mmap(f.fileno(), 1024)
        try:
            # 读取消息
            msg = mm[:].decode('utf-8').strip()
            if msg:
                print(f"Received message: {msg}")
                data = json.loads(msg)
                command = data.get('command')
                throttle = data.get('throttle')
                brake = data.get('brake')
                steer = data.get('steer')
                return command,throttle,brake,steer
            else:
                print("No message received.")
                return None
        finally:
                # 关闭内存映射
                mm.close()


# 仿真实验启动时回调
def ModelStart(userData):
    # 初始化待控制交通车信息
    userData['traffic_id'] = 109
    userData['traffic_x'] = 0
    userData['traffic_y'] = 0
    userData['traffic_yaw'] = 0
    userData['traffic_speed'] = 0.0
    userData['traffic_throttle'] = 0.11
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
    # 1. 主车控制信号发送
    try:

        # 从队列中取出元组
        command, throttle, brake, steer = receiver()  # 设置timeout避免无限阻塞
        logger.info(f"Command: {command}, Throttle: {throttle}, Brake: {brake}, Steer: {steer}")
        if command == 'traffic_control':
            # 生成动作指令
            target_speed, duration, direction = control.control_to_action(userData['traffic_speed'], throttle , brake, steer)
            # 速度控制
            changeSpeed(userData['traffic_id'], target_speed, duration)
            # 方向控制
            changeLane(userData['traffic_id'], change_lane_direction[direction], duration)
            # 车辆路口场景判断(待测试通过路口情况)
            if getRoute(userData['traffic_id']) == next_junction_direction.unknown:
                valid_route = getValidDirections(getVehicleLane(userData['traffic_id']))
                if valid_route:
                        changeRoute(userData['traffic_id'], Direction2Route[direction])
            # 标记任务完成
            task_queue.task_done()
    except queue.Empty:
        logger.info("Queue is empty, no items to get.")

    

# 仿真实验结束时回调
def ModelTerminate(userData):
    pass
