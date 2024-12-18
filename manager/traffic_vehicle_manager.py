from typing import List, Dict
from entities.vehicle import Vehicle
import logging

class TrafficVehicleManager:
    def __init__(self):
        self.vehicles: Dict[str, Vehicle] = {}  # 使用字典存储车辆，键为车辆ID，值为车辆对象
        self.event_log = []  # 事件日志记录

    def add_vehicle(self, vehicle: Vehicle):
        """添加单个车辆"""
        self.vehicles[vehicle.id] = vehicle
        logging.info(f"Vehicle {vehicle.id} added.")

    def add_vehicles(self, vehicles: List[Vehicle]):
        """批量添加车辆"""
        for vehicle in vehicles:
            self.vehicles[vehicle.id] = vehicle
        logging.info(f"{len(vehicles)} vehicles added.")

    def remove_vehicle(self, vehicle_id: str):
        """根据车辆ID移除车辆"""
        if vehicle_id in self.vehicles:
            del self.vehicles[vehicle_id]
            logging.info(f"Vehicle {vehicle_id} removed.")
        else:
            logging.warning(f"Vehicle {vehicle_id} not found.")

    def get_vehicle_info(self, vehicle_id: str) -> Dict:
        """根据车辆ID获取车辆信息"""
        if vehicle_id in self.vehicles:
            return self.vehicles[vehicle_id].__dict__
        logging.warning(f"Vehicle {vehicle_id} not found.")
        return {}

    def get_all_vehicles_info(self) -> List[Dict]:
        """获取所有车辆信息"""
        return [vehicle.__dict__ for vehicle in self.vehicles.values()]

    def find_vehicles_by_status(self, status: str) -> List[Dict]:
        """根据状态查找车辆"""
        return [vehicle.__dict__ for vehicle in self.vehicles.values() if vehicle.status == status]

    def sort_vehicles_by_time(self):
        """按时间戳排序车辆"""
        self.vehicles = dict(sorted(self.vehicles.items(), key=lambda item: item[1].time, reverse=True))

    def find_vehicles_by_position_range(self, x_min: float, x_max: float, y_min: float, y_max: float) -> List[Dict]:
        """根据位置范围查找车辆"""
        return [vehicle.__dict__ for vehicle in self.vehicles.values() if x_min <= vehicle.x <= x_max and y_min <= vehicle.y <= y_max]
