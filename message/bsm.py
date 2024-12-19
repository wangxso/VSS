# Author: 1181110317 <1181110317@qq.com>

import struct
import time
import uuid

# 全局变量，用于追踪msg_id
msg_id_counter = 0

class BasicSafetyMessage:
    def __init__(self, vehicle_id=None, timestamp=None, sim_time=None, latitude=377700000, longitude=-1224194000,
                 elevation=150, speed=300, heading=9000, length=500, width=200, acceleration=0, lights_status=0, perception=None):
        global msg_id_counter  # 使用全局变量
        
        self.msg_id = msg_id_counter  # 使用全局变量的当前值
        msg_id_counter += 1  # 自增msg_id
        
        # 确保 vehicle_id 是一个字符串
        if vehicle_id is None:
            self.vehicle_id = str(uuid.uuid4())
        else:
            self.vehicle_id = str(vehicle_id)

        
        self.timestamp = timestamp if timestamp is not None else int(time.time())  # 使用当前时间戳，如果没有提供的话
        self.sim_time = sim_time  # 仿真时间
        self.latitude = latitude  # 纬度（单位：1e-7度）
        self.longitude = longitude  # 经度（单位：1e-7度）
        self.elevation = elevation  # 海拔（单位：0.1米）
        self.speed = speed  # 速度（单位：0.02米/秒）
        self.heading = heading  # 航向（单位：0.0125度）
        self.length = length  # 车辆长度（单位：0.1米）
        self.width = width  # 车辆宽度（单位：0.1米）
        self.acceleration = acceleration  # 加速度（单位：0.1米/秒^2）
        self.lights_status = lights_status  # 灯光状态（布尔值）
        self.perception = perception or ""  # 默认值为空字符串

    def encode(self):
        """
        将BSM消息编码为二进制格式
        """
        perception_data = self.perception.encode("utf-8")  # 将感知数据转为字节流
        perception_length = len(perception_data)  # 计算感知数据的长度

        
        
        try:
            # 编码基础数据，不包括感知数据部分
            packed_data = struct.pack(
                "!B36sffffffffffII", 
                self.msg_id,
                self.vehicle_id.encode("utf-8").ljust(36, b'\0'),  # 将 vehicle_id 编码为字节流
                self.timestamp,
                self.sim_time,
                self.latitude,
                self.longitude,
                self.elevation,
                self.speed,
                self.heading,
                self.length,
                self.width,
                self.acceleration,
                self.lights_status,
                perception_length  # 先编码感知数据长度
            )
            
            # 接着编码实际的感知数据
            packed_data += perception_data  # 添加感知数据字节流
            
            
        except Exception as e:
            print(f"Error during decoding: {e}")
            raise
        
        return packed_data

    @staticmethod
    def decode(data):
        """
        从二进制格式解码为BSM消息对象
        """
        # 首先解码前49字节的基本数据
        unpacked_data = struct.unpack("!B36sffffffffffII", data[:85])
        
        # 获取感知数据的长度
        perception_length = unpacked_data[-1]
        
        # 确保后续的数据足够长来包含感知数据
        perception_data = data[85:85+perception_length]  # 获取感知数据
        
        # 返回包含解码后的数据
        return {
            "msg_id": unpacked_data[0],
            "vehicle_id": unpacked_data[1].decode("utf-8").strip().rstrip('\0'),
            "timestamp": unpacked_data[2],
            "sim_time": unpacked_data[3],
            "latitude": unpacked_data[4],
            "longitude": unpacked_data[5],
            "elevation": unpacked_data[6],
            "speed": unpacked_data[7],
            "heading": unpacked_data[8],
            "length": unpacked_data[9],
            "width": unpacked_data[10],
            "acceleration": unpacked_data[11],
            "lights_status": unpacked_data[12],
            "perception": perception_data.decode("utf-8")
        }



# 示例用法
if __name__ == "__main__":
    # 创建多个BSM消息，msg_id 会递增
    perception_data = "Example perception data that could be of variable length"
    
    bsm1 = BasicSafetyMessage(
        latitude=377700000,   # 37.77度
        longitude=-1224194000,  # -122.4194度
        speed=300,            # 6.0米/秒
        heading=9000,         # 112.5度
        length=500,           # 5米
        width=200,            # 2米
        acceleration=5,       # 加速度
        lights_status=1,      # 灯光状态
        perception=perception_data  # 变长的感知数据
    )
    
    bsm2 = BasicSafetyMessage(
        latitude=377700100,   # 37.77度
        longitude=-1224194000,  # -122.4194度
        speed=250,            # 5.0米/秒
        heading=10000,        # 125度
        length=600,           # 6米
        width=250,            # 2.5米
        acceleration=2,       # 加速度
        lights_status=0,      # 灯光状态
        perception="Another example of perception data"  # 变长的感知数据
    )
    
    # 编码消息
    encoded_data1 = bsm1.encode()
    encoded_data2 = bsm2.encode()
    print("Encoded BSM 1:", encoded_data1)
    print("Encoded BSM 2:", encoded_data2)
    
    # 解码消息
    decoded_bsm1 = BasicSafetyMessage.decode(encoded_data1)
    decoded_bsm2 = BasicSafetyMessage.decode(encoded_data2)
    
    print("Decoded BSM 1:")
    print(f"Vehicle ID: {decoded_bsm1.vehicle_id}")
    print(f"Perception Data: {decoded_bsm1.perception}")
    
    print("Decoded BSM 2:")
    print(f"Vehicle ID: {decoded_bsm2.vehicle_id}")
    print(f"Perception Data: {decoded_bsm2.perception}")
