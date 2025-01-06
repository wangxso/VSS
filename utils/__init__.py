import os
from entities.vehicle import Vehicle
import mmap
import json
import msvcrt
import yaml
def mmap_sender(objs):
    # 文件名和信号量
    filename = r"C:\PanoSimDatabase\Plugin\channel"
    
    message = json.dumps(objs)
    # 创建一个内存映射文件
    with open(filename, 'w+b') as f:
        msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, os.path.getsize(filename))
        # 为文件分配空间
        f.write(b'\x00' * 1024)  # 1024字节的空间
        mm = mmap.mmap(f.fileno(), 2048)
        # 写入消息
        mm.write(message.encode())
        mm.close()     
        msvcrt.locking(f.fileno(), msvcrt.LK_UNLCK, os.path.getsize(filename))
def receiver():
    # 文件名和信号量
    filename = r"C:\PanoSimDatabase\Plugin\channel"
    
    # 打开并映射文件
    with open(filename, 'r+b') as f:
        # 映射整个文件到内存
        fd = f.fileno()

        # 获取共享锁，其他进程也可以读取
        msvcrt.locking(fd, msvcrt.LK_LOCK, os.path.getsize(filename))
        mm = mmap.mmap(f.fileno(), 2048)
        
        # 读取消息
        msg = mm[:].decode('utf-8').strip()
        objs = json.loads(msg)

        # 关闭内存映射
        mm.close()
         # 释放锁
        msvcrt.locking(fd, msvcrt.LK_UNLCK, os.path.getsize(filename))
    return objs
def cal_ttc(s, v):
    v = v / 3.6
    ttc = 15
    if v < 0.1:
        ttc = - (s-4) / v
    if ttc > 15:
        ttc = 15
    # if s < 9:
    #     ttc = 0
    return ttc 
  
def read_config():
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在目录的上一级目录，即项目根目录
    project_root = os.path.dirname(os.path.dirname(current_file_path))
    # 构建config.yaml文件的完整路径
    config_path = os.path.join(project_root, 'config.yaml')
    
    # 打开并读取YAML文件
    with open(config_path, 'r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    
    return config
