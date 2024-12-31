class V2XApplication:
    def __init__(self, vehicle):
        self.vehicle = vehicle
        self.name = 'V2XApplication'
        self.vehicle_id = vehicle.id
        self.vehicle_x = vehicle.x
        self.vehicle_y = vehicle.y
        self.vehicle_z = vehicle.z
        self.vehicle_yaw = vehicle.yaw
    
    def proc():
        pass