from entities.entity import Entity

class Obstacle(Entity):
    # (2, -1.269, 1.733, 0.0, 0.0, 0.0, 0.0) 
    # shape, x, y, z, yaw, pitch, roll
    # shape  0-车辆 1-行人 2-其他（自行车、三轮车、动物）3-交通标志 4-障碍物 
    def __init__(self, shape, x, y, z, yaw, pitch, roll):
        super().__init__(entity_type="obstacle")
        self.shape = shape
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
    
    def __dict__(self):
        return {
            'shape': self.shape,
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'yaw': self.yaw,
            'pitch': self.pitch,
            'roll': self.roll
        }

    def update(self, x, y, z, yaw, pitch, roll):
        self.x = x
        self.y = y
        self.z = z
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll
