import numpy as np
import re
import traffic_control as control

file_path = r'co-simulation\calibration_table.txt'

# 调用函数并打印结果
traffic_control = control.trafficControl(file_path)

speed = 0
throttle,brake,steer = 0.5,0,0

target_speed,duration,diretion = traffic_control.control_to_action(speed,throttle,brake,steer)


print("target_speed:", target_speed)
print("duration:", duration)
print("diretion:", diretion)
