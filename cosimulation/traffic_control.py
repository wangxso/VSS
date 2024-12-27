import numpy as np
import re
from scipy.interpolate import LinearNDInterpolator


# 解析calibration data
def parse_calibration_data(file_content):
    # 正则表达式匹配模式
    pattern = r"calibration\s*{\s*speed:\s*([\d\.]+)\s*acceleration:\s*([-\d\.]+)\s*command:\s*([-\d\.]+)\s*}"

    # 使用正则表达式找到所有匹配项
    matches = re.findall(pattern, file_content, re.MULTILINE)

    # 提取数据并转换为NumPy数组
    speeds = np.array([float(speed) for speed, _, _ in matches])
    accelerations = np.array([float(acceleration) for _, acceleration, _ in matches])
    commands = np.array([float(command) for _, _, command in matches])

    return speeds, accelerations, commands

def read_calibration_data_from_file(file_path):
    # 读取文件内容
    with open(file_path, 'r') as file:
        file_content = file.read()

    # 解析数据
    return parse_calibration_data(file_content)


class Calibration:
    
    def __init__(self,calibration_file):
        # self.speeds,self.accelerations,self.commands = read_calibration_data_from_file(calibration_file)
        # points = np.column_stack((self.speeds, self.commands))
        # self.interp_func = LinearNDInterpolator(points, self.accelerations)
        speeds,accelerations,commands = read_calibration_data_from_file(calibration_file)
        points = np.column_stack((speeds, commands))
        self.interp_func = LinearNDInterpolator(points, accelerations)

    def calculate_accel(self,speed,command):
        accel = self.interp_func(speed,command)
        return accel
    

class trafficControl:
    def __init__(self,calibration_file):
        self.calibration = Calibration(calibration_file)
    

    def compute_accel(self,speed,throttle,brake):
        command = 0.0
        if throttle == 0.0:
            command = brake*100
        elif throttle != 0.0:
            command = throttle*100

        accel = self.calibration.calculate_accel(speed,command)
        return accel
    

    def control_to_action(self,speed,throttle,brake,steer):
        # 
    # 直行判断
        if steer == 0.0:
            accel = self.compute_accel(speed,throttle,brake)
            duration = 3
            target_speed = speed + accel*duration
            direction = 0
            return target_speed,duration,direction
        # 右转
        elif steer > 0.0:
            accel = self.compute_accel(speed,throttle,brake)
            duration = 3
            target_speed = speed + accel*duration
            direction = 2
            return target_speed,duration,direction
        # 左转
        else:
            accel = self.compute_accel(speed,throttle,brake)
            duration = 3
            target_speed = speed + accel*duration
            direction = 1
            return target_speed,duration,direction
        