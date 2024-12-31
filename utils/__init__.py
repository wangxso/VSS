from entities.vehicle import Vehicle
import mmap
import json

def mmap_sender(objs):
    # 文件名和信号量
    filename = r"C:\PanoSimDatabase\Plugin\channel"
    
    message = json.dumps(objs)
    # 创建一个内存映射文件
    with open(filename, 'w+b') as f:
        
        # 为文件分配空间
        f.write(b'\x00' * 1024)  # 1024字节的空间
        f.close()
    
    # 打开内存映射文件
    with open(filename, 'r+b') as f:
        mm = mmap.mmap(f.fileno(), 1024)
        # 写入消息
        mm.write(message.encode())
        mm.close()     
def receiver():
    # 文件名和信号量
    filename = r"C:\PanoSimDatabase\Plugin\channel"
    


    # 打开并映射文件
    with open(filename, 'r+b') as f:
        # 映射整个文件到内存
        mm = mmap.mmap(f.fileno(), 1024)
        
        # 读取消息
        msg = mm[:].decode('utf-8').strip()
        objs = json.loads(msg)

        # 关闭内存映射
        mm.close()
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
