# Author: 1181110317 <1181110317@qq.com>

import uuid
import time
from typing import List, Dict, Union, Tuple
from entities.vehicle import Vehicle
from entities.entity import Entity

# RSU可以看作带有OBU的静止不动的车辆

class RSU(Entity):
    def __init__(self, rsu_id: str = None, location: Tuple[float, float] = (0.0, 0.0, 0.0), communication_range: float = 100.0):
        """
        初始化RSU（道路侧设备）的属性，设定默认值。
        
        参数:
            rsu_id (str, optional): RSU的ID，默认为None。如果未提供，将自动生成一个唯一的UUID。
            location (Tuple[float, float], optional): RSU的位置，默认为(0.0, 0.0)。
            communication_range (float, optional): RSU的通信范围，默认为100.0米。
        """
        super().__init__(rsu_id, entity_type="rsu")
        # RSU基本信息
        self.id = rsu_id if rsu_id else str(uuid.uuid4())
        # RSU位置 (x, y)
        self.x = location[0]
        self.y = location[1]
        self.z = location[2]
        self.communication_range = communication_range  # RSU的通信范围（单位：米）
        self.nearby_vehicles: List[Vehicle] = []  # 与该RSU周围的车辆列表
        self.status = 'active'  # RSU状态（'active', 'inactive'）

    def update_status(self, status: str):
        """更新RSU的状态"""
        valid_statuses = ['active', 'inactive']
        if status not in valid_statuses:
            raise ValueError(f"无效的状态: {status}. 必须为 {valid_statuses} 中的一个.")
        self.status = status


    def get_rsu_info(self) -> Dict:
        """获取RSU的基本信息"""
        return {
            'id': self.id,
            'location': (self.x, self.y, self.z),
            'status': self.status,
            'communication_range': self.communication_range,
        }
    
    def update_rsu_state(self, position):
        """更新RSU的基本信息"""
        if position is not None:
            self.x, self.y, self.z = position


