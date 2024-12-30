# Author: 1181110317 <1181110317@qq.com>

import math
import socket
import time
from typing import List, Dict, Tuple, Union
from entities.vehicle import Vehicle
from manager.v2x_manager import V2XManager
from manager.world_manager import CavWorld
from message.tools import Build_RSM
import random
import struct
import threading
from queue import Queue
from message.MsgFrame import *
import os
import asn1tools
from loguru import logger
from pki.xdjapki import XdjaPKI
# 默认通信范围
communication_range = 500
PORT = 10086  # 通信端口

# 模拟使用udp通信
# 效率 每辆车一个端口

class CommunicationManagerSocketUdp:
    def __init__(self, cav_world, entity, config_yaml=None):
        """
        初始化通信管理器。

        参数:
            cav_world (CavWorld): 用于管理区域消息池的世界对象。
            config (Dict): 配置字典，用于设置通信参数。
        """
        self.cav_world = cav_world
        self.entity = entity
        self.connections = {}  # 存储当前连 .接的设备或基础设施信息
        vassRootPath = r"C:/PanoSimDatabase/Plugin/Agent/pki/sdk/data"
        self.pki_sys = XdjaPKI(vassRootPath, 111)
        if config_yaml:
            self.communication_range = config_yaml.get('communication_range', communication_range)
            self.loc_noise = config_yaml.get('loc_noise', 0.0)
            self.yaw_noise = config_yaml.get('yaw_noise', 0.0)
            self.speed_noise = config_yaml.get('speed_noise', 0.0)
            self.lag = config_yaml.get('lag', 0)
            self.message_tolerate = config_yaml.get('message_tolerate', 0)
            self.save_latest = config_yaml.get('save_latest', True)
            self.use_sim = config_yaml.get('use_sim', True)
        else:
            self.communication_range = communication_range
            self.loc_noise = 0
            self.yaw_noise = 0
            self.speed_noise = 0
            self.lag = 0
            self.message_tolerate = 0
            self.save_latest = True
            self.use_sim = True


        # 随机ip和端口
        self.received_messages = Queue()
        
        self.threads = {}

        self.ip = 'localhost'
        self.lock = threading.Lock()
        self.port = self.find_free_port()
        
        
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.ip, self.port))
        self.sock.settimeout(1)

        
        self.stop_event = threading.Event()
        self.receive_thread = threading.Thread(target=self._receive_messages)
        self.receive_thread.start()




    def vehicle_send_bsm_message(self, vehicle: Vehicle, v2x_manager: V2XManager, objets = None, config_yaml: Dict = None):
        """
        发送V2X消息。
        """
        add_noise_x, add_noise_y, add_noise_yaw = v2x_manager.get_ego_pos()
        add_noise_speed = v2x_manager.get_ego_speed()
        bsm_message = BSM_MsgFrame()
        id = str(vehicle.id)  # 截取 UUID 的前 8 个字符，符合标准
        bsm_message['id'] = '{:0>8}'.format(id)
        bsm_message['secMark'] = int((time.time() * 1000) % 60000)  # 当前毫秒值，取模 60000 符合范围 [0, 59999]

        # 经纬度：单位为 1/10 微度 (10^-7 度)
        bsm_message['pos']['lat'] = int(add_noise_y * 1e7)
        bsm_message['pos']['long'] = int(add_noise_x * 1e7)

        # 高度：单位为 1 厘米，假设 z 为米
        bsm_message['pos']['elevation'] = int(vehicle.z * 100)

        # 速度：单位为 0.02 米每秒，转化为厘米每秒后除以 2
        bsm_message['speed'] = int(add_noise_speed * 50)  # 转化为符合 BSM 的单位


        if add_noise_yaw < 0:
            add_noise_yaw += 360
        if add_noise_yaw> 359.9875:
            add_noise_yaw =359.9875 

        # 方位角：单位为 0.0125 度，先转为度再乘以 80
        bsm_message['heading'] = int(math.degrees(add_noise_yaw) * 80)

        # 加速度：单位为 0.01 m/s^2
        bsm_message['accelSet']['long'] = int(vehicle.acceleration * 100)

        # 速度置信度：假设为 1 表示置信度可用
        bsm_message['motionCfd']['speedCfd'] = 1

        # 车辆尺寸：单位为厘米
        bsm_message['size']['width'] = vehicle.width * 100
        bsm_message['size']['length'] = vehicle.length * 100

        objets = None

        if objets != None:
            for i in range(len(objets)):
                bsm_message['obstacles'].append(objets[i])

        # bsm_message = BSM_MsgFrame()
        # print(bsm_message)

        AID = int(1).to_bytes(length=4, byteorder='big')
        bsm_encoded = self.cav_world.ltevCoder.encode('BasicSafetyMessage', BSM.PrepareForCode(bsm_message))
        bsm_encoded = AID + bsm_encoded
        bsm_encoded_str = bsm_encoded.hex()
        safe_message, length = self.pki_sys.sign(bsm_encoded_str, 0)
        # demo bsm message
        # bsm_message = f'{self.vehicle.id},{add_noise_x},{add_noise_y},{add_noise_speed},{self.vehicle.sim_time}'.encode('utf-8')


        for id in self.connections.keys():
            logger.info(f"BSM Message>>>>> 车辆 {vehicle.id} 发送消息: {bsm_encoded_str} to {id} ")
            self.sock.sendto(safe_message, (self.connections[id]['vm'].obu.communication_manager.ip,self.connections[id]['vm'].obu.communication_manager.port))

        # print(f"车辆 {vehicle.id} 发送消息: {bsm_message}")



    def rsu_send_rsm_message(self, v2x_manager: V2XManager, objets, config_yaml: Dict = None):
        add_noise_x, add_noise_y, add_noise_yaw = v2x_manager.get_ego_pos()
        rsm_message = [0 for _ in range(5)]
        rsm_message[2] = int(add_noise_y)
        rsm_message[3] = int(add_noise_x)
        rsm_message[4] = 0
        participant_list = []
        for i in range(len(objets)):
            # Add participant with obstacle-like information
            # participant = RSMParticipantData_DF()
            # participant['id'] = str(objets[i]['id'])
            x, y ,z = objets[i]["position"]

            yaw, pitch, roll = objets[i]["orientation"]
            participant = [0 for _ in range(11)]
            participant[0] = str(objets[i]['id'])
            participant[2] = objets[i]['type']
            participant[3] = objets[i]['type']
            participant[4] = int(x)
            participant[5]= int(y)
            participant[6] = int(z)
            participant[7] = int(yaw)
            participant[8] = int(pitch)
            participant[9] = int(roll)
            participant[10] = int(objets[i]['speed'])
            participant_list.append(participant)
            # participant['pos']['offsetLL'] = ('position-LatLon', {'lon': int(x), 'lat': int(y)})
            # participant['pos']['offsetV'] = ('elevation', int(z))
            # participant['heading'] = int(yaw)
            # participant['speed'] = int(objets[i]['speed'])
            # participant['ptcType'] = objets[i]['type']  # Example obstacle type
            # rsm_message['participants'].append(participant)
        rsm_message_data = Build_RSM.getRSMData(rsm_message, participant_list)
        rsm_encoded = self.cav_world.ltevCoder.encode('RoadsideSafetyMessage', RSM.PrepareForCode(rsm_message_data))
        AID = int(2).to_bytes(length=4, byteorder='big')
        rsm_encoded = AID + rsm_encoded
        rsm_encoded_str = rsm_encoded.hex()
        safe_message, length = self.pki_sys.sign(rsm_encoded_str, 0)
        for id in self.connections.keys():
            logger.info(f"RSM Message>>>>> 车辆 {self.entity.id} 发送消息: {rsm_encoded_str} to {id} ")
            self.sock.sendto(safe_message, (self.connections[id]['vm'].obu.communication_manager.ip,self.connections[id]['vm'].obu.communication_manager.port))



    def _receive_messages(self):
        while not self.stop_event.is_set():
            try:
                message, addr = self.sock.recvfrom(4096)
        
                # bsm_decoded = self.cav_world.ltevCoder.decode('BasicSafetyMessage', message)
                # decoded_message = message.decode('utf-8')  # Assuming message is a string

                # 检查时间有效性
                # if self.use_sim:
                #     current_time = self.vehicle.sim_time
                #     if current_time - message['sim_time'] > self.message_tolerate:
                #         return
                # else:
                #     current_time = self.vehicle.current_time
                #     if current_time - message['timestamp'] > self.message_tolerate:
                #         return
                # if decoded_message['vehicle_id'] in self.connections:
                #     self.receive_v2x_message(decoded_message)
                self.received_messages.put(message)


            except socket.timeout:
                continue
            except Exception as e:
                print(f"Error while receiving: {e}")



    def connect(self, target_id, vm_info, connection_type):
        """
        建立与目标设备或基础设施的连接。
        """
        if target_id in self.connections:
            # print(f"已经与目标 {target_id} 建立了连接。")
            return False

        # 模拟建立连接的逻辑c
        info = {}
        info['vm'] = vm_info
        info['connection_type'] = connection_type
        self.connections[target_id] = info
        # self.connections[target_id]['connection_type'] = {}
        # self.connections[target_id]['connection_type'] = connection_type
        # print(f"成功建立与目标 {target_id} 的 {connection_type} 连接。")
        return True

    def disconnect(self, target_id):
        """
        断开与目标设备或基础设施的连接。

        """
        if target_id not in self.connections:
            # print(f"未找到与目标 {target_id} 的连接。")
            return False

        # 模拟断开连接的逻辑
        del self.connections[target_id]
        # print(f"已断开与目标 {target_id} 的连接。")
        return True

    def list_connections(self):
        """
        列出当前所有的连接。
        """
        # print("当前连接：")
        # for target_id, connection_type in self.connections.items():
        #     print(f"目标 ID: {target_id}, 连接类型: {connection_type}")
        return self.connections

    def broadcast_message(self, v2x_manager: V2XManager, objects, config_yaml: Dict = None, message_type: str = 'bsm', entity: Vehicle = None):
        """
        向当前通信范围内的所有设备广播消息。
        """
        if message_type == 'bsm':
            self.vehicle_send_bsm_message(entity, v2x_manager, objects)

        if message_type == 'rsu':
            self.rsu_send_rsm_message(v2x_manager, objects)

    def update_connections(self, nearby_vehicles: Dict, connection_type: str):
        """
        更新当前的连接，根据通信范围内的附近车辆动态调整连接。
        """
        # 获取当前的连接类型信息
        current_connections = set(
            target_id for target_id, conn_type in self.connections.items() if conn_type == connection_type
        )
        updated_connections = set()

        for vehicle, info in nearby_vehicles.items():
            # 如果车辆在通信范围内，更新连接
            updated_connections.add(vehicle)
            if vehicle not in current_connections:
                self.connect(vehicle, info, "V2V")

        # 清理不在范围内的连接
        for target_id in current_connections - updated_connections:
            self.disconnect(target_id)

    '''
    ===================================工具===================================
    '''

    def find_free_port(self):
        """随机选择一个端口并确保它没有被占用"""
        while True:
            port = random.randint(1024, 65535)
            with self.lock:  # 确保在访问 shared 资源时没有竞争条件
                if port not in self.cav_world.used_ports:
                    try:
                        # 尝试绑定端口
                        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        server_socket.bind(('localhost', port))
                        server_socket.close()
                        self.cav_world.used_ports.add(port)
                        return port
                    except OSError:
                        # 如果端口已被占用，则跳过并继续
                        continue
    

    def stop_port(self):
        self.stop_event.set()
        self.receive_thread.join()