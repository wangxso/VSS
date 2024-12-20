# Author: 1181110317 <1181110317@qq.com>

import importlib
import socket
import random
import threading

class CavWorld(object):
    """
    一个定制的世界对象，用于保存所有协同驾驶车辆信息和共享的机器学习模型。

    参数
    ----------
    apply_ml : bool
        在此仿真中是否应用机器学习/深度学习模型，请确保在将此设置为True之前已安装torch/sklearn。

    属性
    ----------
    vehicle_id_set : set
        存储车辆ID的集合。

    ego_vehicle_manager : vehicle_manager对象
        存储主车管理器。

    _traffic_vehicle_managers : dict
        存储交通车管理器的字典。

    _rsu_manager_dict : dict
        存储RSU管理器的字典。

    ml_manager : 机器学习对象
        机器学习管理器类。
    """

    def __init__(self, comm_model='sim', apply_ml=False):
        self.vehicle_id_set = set()  # 存储车辆ID
        self.ego_vehicle_manager = None  # 主车管理器
        self.ego_vehicle_id = None
        self._traffic_vehicle_managers = {}  # 交通车管理器字典
        self._rsu_manager_dict = {}  # RSU管理器字典
        self.ml_manager = None  # ML管理器
        self.global_clock = 0  # 全局时钟
        self.MESSAGE_REGIONS = {}
        self.comm_model = comm_model # 通信模拟模型



        self.threads = {}
        self.used_port = set()
        self.lock = threading.Lock()
        self.MESSAGE_REGIONS_UDP = {}

        # if apply_plat:
        #     self._platooning_dict = {}

        # if apply_ml:
        #     # 初始化机器学习管理器，将深度学习/机器学习模型加载到内存中
        #     self.ml_manager = ml_manager()

    def set_ego_vehicle_manager(self, vehicle_manager):
        """
        设置主车管理器。
        """
        if self.ego_vehicle_manager is not None:
            raise ValueError("主车管理器已经存在，无法重复设置！")
        self.ego_vehicle_manager = vehicle_manager
        self.ego_vehicle_id = vehicle_manager.vehicle.id  # 添加到车辆ID集合
        print(f"主车 {vehicle_manager.vehicle.id} 已成功设置。")

    def add_traffic_vehicle_manager(self, vehicle_manager):
        """
        添加交通车管理器。
        """
        if vehicle_manager.vehicle.id in self.vehicle_id_set:
            raise ValueError(f"车辆ID {vehicle_manager.vehicle.id} 已存在！")
        self.vehicle_id_set.add(vehicle_manager.vehicle.id)  # 添加到车辆ID集合
        self._traffic_vehicle_managers[vehicle_manager.vehicle.id] = vehicle_manager
        print(f"交通车 {vehicle_manager.vehicle.id} 已成功添加。")

    def update_rsu_manager(self, rsu_manager):
        """
        添加RSU管理器。
        """
        self._rsu_manager_dict.update({rsu_manager.rid: rsu_manager})
        print(f"RSU {rsu_manager.rid} 已成功添加。")

    def get_all_vehicle_managers(self):
        """
        返回所有车辆管理器的字典，包括主车和交通车。
        """
        vehicle_managers = {}
        if self.ego_vehicle_manager:
            ego_managers = {}
            ego_managers[self.ego_vehicle_id] = self.ego_vehicle_manager
            vehicle_managers["ego"] = ego_managers
        vehicle_managers["traffic"] = self._traffic_vehicle_managers
        return vehicle_managers

    def get_ego_vehicle_manager(self):
        """
        返回主车的车辆管理器。
        """
        return self.ego_vehicle_manager

    def get_traffic_vehicle_managers(self):
        """
        返回所有交通车的管理器字典。
        """
        return self._traffic_vehicle_managers

    def tick(self):
        """
        增加全局时钟。
        """
        self.global_clock += 1
        print(f"全局时钟已更新至：{self.global_clock}")


    '''
    =======================================================================udp=======================================================================
    '''

    def find_free_port(self):
        """随机选择一个端口并确保它没有被占用"""
        while True:
            port = random.randint(1024, 65535)
            with self.lock:  # 确保在访问 shared 资源时没有竞争条件
                if port not in self.used_ports:
                    try:
                        # 尝试绑定端口
                        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        server_socket.bind(('localhost', port))
                        server_socket.close()
                        self.used_ports.add(port)
                        return port
                    except OSError:
                        # 如果端口已被占用，则跳过并继续
                        continue

    def handle_client(self, port):
        """监听指定端口的 UDP 请求"""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server_socket.bind(('localhost', port))

    def add_port(self, port):
        """动态添加一个端口并启动监听"""
        stop_flag = threading.Event()
        threading.Thread(target=self.handle_client, args=(port,)).start()
        self.threads[port] = stop_flag

    def stop_port(self, port):
        """停止指定端口的监听"""
        if port in self.threads:
            stop_flag = self.threads[port]
            stop_flag.set()  # 设置 stop_flag，通知线程退出



    '''
    =======================================================================更新世界=======================================================================
    '''
    def update(self):
        """
        更新整个世界管理器。
        """
        try:
            return True
        except:
            return False


    '''
    =====================================================车队接口，暂时不需要=====================================================

    '''
    # def get_platoon_dict(self):
    #     """
    #     返回现有的车队。
    #     """
    #     return self._platooning_dict
    # def update_platooning(self, platooning_manager):
    #     """
    #     添加创建的车队。

    #     参数
    #     ----------
    #     platooning_manager : opencda对象
    #         车队管理器类。
    #     """
    #     self._platooning_dict.update(
    #         {platooning_manager.pmid: platooning_manager})