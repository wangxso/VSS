import uuid
from opencda.core.actuation.control_manager import ControlManager
from opencda.core.application.platooning.platoon_behavior_agent import PlatooningBehaviorAgent
from opencda.core.common.v2x_manager import V2XManager
from opencda.core.sensing.localization.localization_manager import LocalizationManager
from opencda.core.sensing.perception.perception_manager import PerceptionManager
from opencda.core.safety.safety_manager import SafetyManager
from opencda.core.plan.behavior_agent import BehaviorAgent
from opencda.core.map.map_manager import MapManager
from opencda.core.common.data_dumper import DataDumper


class VehicleManager(object):
    """
    车辆管理类，用于整合车辆的各个模块（感知、控制、行为规划等）在一起。

    参数
    ----------
    vehicle : carla.Vehicle
        Carla仿真中的车辆对象。我们需要通过这个类来生成GNSS和IMU传感器。

    config_yaml : dict
        该CAV的配置字典。

    application : list
        应用类别，目前支持['single', 'platoon']。

    carla_map : carla.Map
        CARLA仿真地图。

    cav_world : opencda对象
        CAV世界，用于V2X通信仿真。

    current_time : str
        仿真开始的时间戳，用于数据导出。

    data_dumping : bool
        指示是否在仿真过程中导出传感器数据。

    属性
    ----------
    v2x_manager : opencda对象
        当前的V2X管理器。

    localizer : opencda对象
        当前的定位管理器。

    perception_manager : opencda对象
        当前的V2X感知管理器。

    agent : opencda对象
        当前的车辆行为规划代理。

    controller : opencda对象
        当前的控制管理器。

    data_dumper : opencda对象
        用于导出传感器数据。
    """

    def __init__(self,
                 vehicle,
                 config_yaml,
                 application,
                 carla_map,
                 cav_world,
                 current_time='',
                 data_dumping=False):
        """
        初始化方法，整合车辆管理各模块。

        参数
        ----------
        vehicle : carla.Vehicle
            车辆对象。

        config_yaml : dict
            配置字典。

        application : list
            应用类别。

        carla_map : carla.Map
            仿真地图。

        cav_world : opencda对象
            CAV世界。

        current_time : str
            仿真开始时间。

        data_dumping : bool
            是否导出数据。
        """
        # 为车辆生成唯一的UUID
        self.vid = str(uuid.uuid1())
        self.vehicle = vehicle
        self.carla_map = carla_map

        # 获取不同模块的配置
        sensing_config = config_yaml['sensing']
        map_config = config_yaml['map_manager']
        behavior_config = config_yaml['behavior']
        control_config = config_yaml['controller']
        v2x_config = config_yaml['v2x']

        # 初始化V2X模块
        self.v2x_manager = V2XManager(cav_world, v2x_config, self.vid)
        # 初始化定位模块
        self.localizer = LocalizationManager(vehicle, sensing_config['localization'], carla_map)
        # 初始化感知模块
        self.perception_manager = PerceptionManager(vehicle, sensing_config['perception'], cav_world, data_dumping)
        # 初始化地图管理模块
        self.map_manager = MapManager(vehicle, carla_map, map_config)
        # 初始化安全管理模块
        self.safety_manager = SafetyManager(cav_world=cav_world, vehicle=vehicle, params=config_yaml['safety_manager'])
        # 初始化行为规划代理
        self.agent = None
        if 'platooning' in application:
            platoon_config = config_yaml['platoon']
            self.agent = PlatooningBehaviorAgent(vehicle, self, self.v2x_manager, behavior_config, platoon_config, carla_map)
        else:
            self.agent = BehaviorAgent(vehicle, carla_map, behavior_config)

        # 初始化控制模块
        self.controller = ControlManager(control_config)

        # 如果需要数据导出，初始化数据导出器
        if data_dumping:
            self.data_dumper = DataDumper(self.perception_manager, vehicle.id, save_time=current_time)
        else:
            self.data_dumper = None

        # 更新CAV世界中的车辆管理器
        cav_world.update_vehicle_manager(self)

    def set_destination(self, start_location, end_location, clean=False, end_reset=True):
        """
        设置全局路线。

        参数
        ----------
        start_location : carla.location
            车辆的起始位置。

        end_location : carla.location
            车辆的目标位置。

        clean : bool
            是否清空路径队列。

        end_reset : bool
            是否重置终点位置。

        """
        self.agent.set_destination(start_location, end_location, clean, end_reset)

    def update_info(self):
        """
        调用感知和定位模块，获取周围信息和自车位置。
        """
        # 定位
        self.localizer.localize()

        ego_pos = self.localizer.get_ego_pos()
        ego_spd = self.localizer.get_ego_spd()

        # 物体检测
        objects = self.perception_manager.detect(ego_pos)

        # 更新地图管理器中的自车位置信息
        self.map_manager.update_information(ego_pos)

        # 安全管理需要的输入信息
        safety_input = {
            'ego_pos': ego_pos,
            'ego_speed': ego_spd,
            'objects': objects,
            'carla_map': self.carla_map,
            'world': self.vehicle.get_world(),
            'static_bev': self.map_manager.static_bev,
            'vis_bev': self.map_manager.vis_bev
        }
        self.safety_manager.update_info(safety_input)

        # 更新V2X管理器中的自车信息，并搜索附近的CAV
        self.v2x_manager.update_info(ego_pos, ego_spd)

        # 更新行为规划代理的信息
        self.agent.update_information(ego_pos, ego_spd, objects)
        # 将位置和速度信息传递给控制器
        self.controller.update_info(ego_pos, ego_spd)

    def run_step(self, target_speed=None):
        """
        执行一步导航。
        """
        # 可视化BEV地图（如果需要）
        self.map_manager.run_step()
        target_speed, target_pos = self.agent.run_step(target_speed)
        control = self.controller.run_step(target_speed, target_pos)

        # 导出数据
        if self.data_dumper:
            self.data_dumper.run_step(self.perception_manager, self.localizer, self.agent)

        return control

    def destroy(self):
        """
        销毁车辆对象。
        """
        self.perception_manager.destroy()
        self.localizer.destroy()
        self.vehicle.destroy()
        self.map_manager.destroy()
