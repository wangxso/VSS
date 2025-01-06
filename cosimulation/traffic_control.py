import numpy as np
import re
from scipy.interpolate import LinearNDInterpolator



def parse_calibration_data(file_content):
    """# 解析calibration data

    Args:
        file_content (str): calibration data文件

    Returns:
        numpy.array: 速度表
        numpy.array: 加速度表
        numpy.array: 控制命令表
    """
    # 正则表达式匹配模式
    pattern = r"calibration\s*{\s*speed:\s*([\d\.]+)\s*acceleration:\s*([-\d\.]+)\s*command:\s*([-\d\.]+)\s*}"

    # 使用正则表达式找到所有匹配项
    matches = re.findall(pattern, file_content, re.MULTILINE)

    # 提取数据并转换为NumPy数组
    speeds = np.array([float(speed) for speed, _, _ in matches])
    accelerations = np.array([float(acceleration) for _, acceleration, _ in matches])
    commands = np.array([float(command) for _, _, command in matches])

    return speeds, accelerations, commands

# 读取文件内容
def read_calibration_data_from_file(file_path):
    
    with open(file_path, 'r') as file:
        file_content = file.read()

    # 解析数据
    return parse_calibration_data(file_content)


class Calibration:
    def __init__(self,calibration_file):
        speeds,accelerations,commands = read_calibration_data_from_file(calibration_file)
        points = np.column_stack((speeds, commands))
        # 生成插值算法
        self.interp_func = LinearNDInterpolator(points, accelerations)

    def calculate_accel(self,speed,command):
        """计算加速度

        Args:
            speed (float): 车辆当前速度
            command (float): 控制命令

        Returns:
            float: 加速度
        """
        accel = self.interp_func(speed,command)
        return accel
    

class trafficControl:
    def __init__(self,calibration_file):
        self.calibration = Calibration(calibration_file)
    

    def compute_accel(self,speed,throttle,brake):
        """计算车辆加速度

        Args:
            speed (float): 车辆当前速度
            throttle (float): 车辆油门命令
            brake (float): 车辆刹车命令

        Returns:
            float: 车辆加速度
        """
        command = 0.0
        if throttle == 0.0:
            command = brake*100
        elif throttle != 0.0:
            command = throttle*100
        accel = self.calibration.calculate_accel(speed,command)
        if speed > 9.5:
            accel = -0.1
        return accel
    

    def control_to_action(self,speed,throttle,brake,steer):
        """生成车辆动作命令

        Args:
            speed (float): 车辆当前速度
            throttle (float): 车辆油门命令
            brake (float): 车辆刹车命令
            steer (float): 车辆转向命令

        Returns:
            float: 车辆目标速度
            float: 持续时间
            float: 方向 —— 0, 直行; 1, 左转; 2, 右转
        """
    # 直行判断
        if steer == 0.0:
            accel = self.compute_accel(speed,throttle,brake)
            duration = 0.1
            target_speed = speed + accel*duration
            direction = 0
            return target_speed,duration,direction
        # 右转
        elif steer > 0.0:
            accel = self.compute_accel(speed,throttle,brake)
            duration = 0.1
            target_speed = speed + accel*duration
            direction = 2
            return target_speed,duration,direction
        # 左转
        else:
            accel = self.compute_accel(speed,throttle,brake)
            duration = 0.1
            target_speed = speed + accel*duration
            direction = 1
            return target_speed,duration,direction
