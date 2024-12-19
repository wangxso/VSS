import struct
import time

class BasicSafetyMessage:
    def __init__(self, msg_id=0x20, vehicle_id="VH123456", timestamp=None, sim_time = None, latitude=377700000, longitude=-1224194000,
                 elevation=150, speed=300, heading=9000, length=500, width=200, acceleration=0, lights_status=0, perception=None):
        self.msg_id = msg_id  # 消息ID
        self.vehicle_id = vehicle_id  # 车辆ID
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
        
        # 编码基础数据，不包括感知数据部分
        packed_data = struct.pack(
            "!B8sQiiffffHBBI", 
            self.msg_id,
            self.vehicle_id.encode("utf-8"),  # 将 vehicle_id 编码为字节流
            self.timestamp,
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
        
        return packed_data

    @staticmethod
    def decode(data):
        """
        从二进制格式解码为BSM消息对象
        """
        # 首先解码前49字节的基本数据
        unpacked_data = struct.unpack("!B8sQiiffffHBBI", data[:49])
        
        # 获取感知数据的长度
        perception_length = unpacked_data[-1]
        
        # 确保后续的数据足够长来包含感知数据
        perception_data = data[49:49+perception_length]  # 获取感知数据
        
        # 返回包含解码后的数据
        return BasicSafetyMessage(
            msg_id=unpacked_data[0],
            vehicle_id=unpacked_data[1].decode("utf-8").strip(),  # 解码并去除空格
            timestamp=unpacked_data[2],
            latitude=unpacked_data[3],
            longitude=unpacked_data[4],
            elevation=unpacked_data[5],
            speed=unpacked_data[6],
            heading=unpacked_data[7],
            length=unpacked_data[8],
            width=unpacked_data[9],
            acceleration=unpacked_data[10],
            lights_status=unpacked_data[11],
            perception=perception_data.decode("utf-8")  # 将感知数据转为字符串
        )

# 示例用法
if __name__ == "__main__":
    # 构造BSM消息
    perception_data = "Example perception data that could be of variable length"
    bsm = BasicSafetyMessage(
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
    
    # 编码消息
    encoded_data = bsm.encode()
    print("Encoded BSM:", encoded_data)
    
    # 解码消息
    decoded_bsm = BasicSafetyMessage.decode(encoded_data)
    print("Decoded BSM:")
    print(f"Vehicle ID: {decoded_bsm.vehicle_id}")
    print(f"Perception Data: {decoded_bsm.perception}")
