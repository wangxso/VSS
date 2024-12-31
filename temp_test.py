import mmap
import json
def sender():
    # 文件名和信号量
    filename = r"C:\PanoSimDatabase\Plugin\channel"
    message = {
        "type": "status_update",
        "speed": 20
    }
    
    message = json.dumps(message)
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
        if msg:
            print(f"Received message: {msg}")
        else:
            print("No message received.")

        # 关闭内存映射
        mm.close()



if __name__ == "__main__":
    sender()
    receiver()
