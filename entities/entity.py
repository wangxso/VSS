# Author: 1181110317 <1181110317@qq.com>

import uuid
import time
import json
from typing import List, Tuple, Dict, Union
import matplotlib.pyplot as plt
import math



class Entity:
    """
    通用父类，用于表示交通系统中的各种实体（如OBU、RSU、车辆、行人等）。
    """
    def __init__(self, entity_id: str = None, entity_type: str = "generic"):
        """
        初始化实体对象。

        参数:
            entity_id (str, optional): 实体ID，默认为None，如果未提供，自动生成一个唯一的UUID作为ID。
            entity_type (str): 实体类型，例如"vehicle", "pedestrian", "obu", "rsu"。
        """
        self.id = entity_id if entity_id else str(uuid.uuid4())
        self.creation_time = time.time()
        self.sim_time = 0.0  # 仿真时间
        self.entity_type = entity_type

        # 实体位置与方向
        self.x, self.y, self.z = 0.0, 0.0, 0.0
        self.yaw, self.pitch, self.roll = 0.0, 0.0, 0.0

        # 运动信息
        self.speed = 0.0
        self.acceleration = 0.0

        # 状态信息
        self.status = 'active'

        self.height = 0
        self.width = 0
        self.length = 0
