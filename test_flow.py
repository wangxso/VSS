# Author: 1181110317 <1181110317@qq.com>

import matplotlib.pyplot as plt
import numpy as np
import yaml
from manager.ego_vehicle_manager import EgoVehicleManager
from manager.traffic_vehicle_manager import TrafficVehicleManager
from manager.world_manager import CavWorld
from entities.vehicle import Vehicle
import time
import random
from matplotlib.patches import Circle


traffic_number = 20

# 加载配置文件
config = next(yaml.safe_load_all(open('config.yaml')))

# 世界管理器
cav_world = CavWorld(comm_model='udp')

# 主车管理器
v1_m = EgoVehicleManager(Vehicle(), cav_world, config_yaml=config)

# 交通车管理器（多辆交通车）
traffic_managers = [
    TrafficVehicleManager(Vehicle(), cav_world, config_yaml=config) for _ in range(traffic_number)  # 增加5辆交通车
]

# 初始化画图
def get_img(a=-200,b=200):
    # 初始化绘图
    fig, ax = plt.subplots()
    ax.set_xlim(a, b)  # 坐标范围（根据车辆运行范围调整）
    ax.set_ylim(a, b)

    # 不同车辆用不同颜色显示
    colors = ['g', 'b', 'c', 'm', 'y', 'k'] 
    labels = ['Ego Vehicle'] + [f'Traffic {i+1}' for i in range(len(traffic_managers))]

    # 为每辆车准备一条轨迹线
    lines = []
    for i in range(len(labels)):
        color = np.random.rand(3,)
        if i == 0:
            marker = '*'
        else:
            marker = 'o'
        lines.append(ax.plot([], [], color=(color[0], color[1], color[2]), marker=marker, label=labels[i], linewidth=1, markersize=0.5)[0])
    # 添加图例
    ax.legend()
    return ax, lines

# 根据坐标点范围初始化画图
ax,lines = get_img(-200,200)

# 初始化轨迹数据
trajectory_x = [[] for _ in range(len(lines))]
trajectory_y = [[] for _ in range(len(lines))]

# 初始化交通车位置
for t_m in traffic_managers:
    t_m.update_vehicle_state(position=(random.uniform(0, 100),random.uniform(0, 100),0))


# 初始化圆对象，使用柔和的半透明淡紫色
circle = Circle((v1_m.vehicle.x, v1_m.vehicle.y), config['v2x']['communication_range'], color='#9370DB', alpha=0.3, label='Ego Range')  # #9370DB为淡紫色
ax.add_patch(circle)

# 添加车辆数目标注
vehicle_count_text = ax.text(0, 0, "", fontsize=10, color='#4B0082', ha='center')  # 使用较深的紫色显示车辆数

# 模拟控制与动态绘图
text_objects = []  # 存储所有距离标注的文本对象

# 初始化轨迹数据
trajectory_x[0].append(v1_m.vehicle.x)  # 主车
trajectory_y[0].append(v1_m.vehicle.y)


for i, tm in enumerate(traffic_managers):
    trajectory_x[i + 1].append(tm.vehicle.x)  # 交通车
    trajectory_y[i + 1].append(tm.vehicle.y)

for step in range(100):  # 运行100步
    # 主车控制
    v1_m.apply_control(throttle=0.5, brake=0.0, steer=0)



    # 交通车控制
    for i, tm in enumerate(traffic_managers):
        tm.apply_control(throttle=0.5 + np.random.uniform(-0.5, 0.5), brake=0.0, steer=random.uniform(-0.2, 0.2))
        

    if not cav_world.update():
        print('error')
        break

    # 打印通信范围内的车辆
    # print(f'ego_car的通信范围内有：{len(v1_m.v2x_manager.cav_nearby)}辆车，分别是：{v1_m.v2x_manager.cav_nearby}')

    # 更新轨迹数据
    trajectory_x[0].append(v1_m.vehicle.x)  # 主车
    trajectory_y[0].append(v1_m.vehicle.y)


    for i, tm in enumerate(traffic_managers):
        trajectory_x[i + 1].append(tm.vehicle.x)  # 交通车
        trajectory_y[i + 1].append(tm.vehicle.y)

    # 更新绘图数据
    for i, line in enumerate(lines):
        line.set_data(trajectory_x[i], trajectory_y[i])

    # 清除之前的距离标注
    for text in text_objects:
        text.remove()  # 移除上一步的文本对象
    text_objects = []  # 清空存储列表

    # 在图上标出车辆的距离
    ego_x, ego_y = v1_m.vehicle.x, v1_m.vehicle.y
    vehicles_in_range = 0  # 计数在圆内的车辆数
    for i, tm in enumerate(traffic_managers):
        traffic_x, traffic_y = tm.vehicle.x, tm.vehicle.y
        distance = np.sqrt((ego_x - traffic_x) ** 2 + (ego_y - traffic_y) ** 2)  # 计算距离

        # 判断是否在通信范围内
        if distance <= config['v2x']['communication_range']:
            vehicles_in_range += 1

        # 设置颜色：小于50标红，大于等于50标绿
        text_color = 'red' if distance < config['v2x']['communication_range'] else 'green'

        # 在交通车点的上方（或下方）显示距离值
        text_offset_x = 2  # 横向偏移量
        text_offset_y = 5 if ego_y < traffic_y else -5  # 根据位置动态调整纵向偏移
        text = ax.text(
            traffic_x + text_offset_x, traffic_y + text_offset_y,  # 将文本放置在交通车点附近
            f"{distance:.1f}",  # 显示保留1位小数的距离
            fontsize=8, color=text_color, ha='center'
        )
        text_objects.append(text)  # 保存文本对象

    # 更新圆的位置和大小
    circle.set_center((ego_x, ego_y))  # 更新圆心位置
    circle.set_radius(config['v2x']['communication_range'])  # 设置半径

    # 更新圆内车辆数的标注
    vehicle_count_text.set_text(f"range: {vehicles_in_range}")
    vehicle_count_text.set_position((ego_x, ego_y))

    # 更新绘图
    plt.pause(0.1)  # 设置更新间隔为0.1秒

cav_world.stop()
print('停止')

plt.show()




    





