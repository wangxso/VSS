# Author: 1181110317 <1181110317@qq.com>

import uuid
from typing import Dict, List, Union, Tuple
from manager.v2x_manager import V2XManager
from manager.world_manager import  CavWorld

import time
import json
import matplotlib.pyplot as plt

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from entities.vehicle import Vehicle  # Vehicle 类已经定义
from entities.obu import OBU
from perception.perception_manager import PerceptionManager
from entities.rsu import RSU
import numpy as np

# 默认通信距离
communication_range = 500

class RSUManager:
    def __init__(self, rsu: RSU, cav_world: CavWorld, config_yaml: Dict = None):
        """
        初始化车辆管理类，管理单个车辆的状态和操作。

        参数:
            vehicle (Vehicle): 需要管理的车辆对象。
        """
        self.rsu = rsu  # 管理的车辆
        self.rsu_id = rsu.id  # 车辆的ID，直接从车辆对象获取


        self.perception_manager = PerceptionManager(rsu, cav_world)
        self.obu = None
        self.v2x_manager = None
        
        if config_yaml:
            v2x_config = config_yaml.get('v2x', {})
        else:
            v2x_config = None

        self.rsu.communication_range = config_yaml.get('communication_range', communication_range)

        if len(v2x_config) > 0:
            self.v2x_manager = V2XManager(self, rsu.id, cav_world, config_yaml=v2x_config)
            self.v2x_manager.ego_car = 1
            self.obu = OBU(self.v2x_manager, rsu, cav_world=cav_world, config_yaml=v2x_config)

        
        self.cav_world = cav_world
        self.cav_world.add_rsu_manager(self)


    def get_rsu_info(self) -> Dict:
        """获取RSU的基本信息"""
        return self.rsu.get_rsu_info()

    def update_rsu_state(self, position):
        """更新RSU的基本信息"""
        self.rsu.update_rsu_state(position)