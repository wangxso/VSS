import sqlite3
from datetime import datetime
import utils
# 数据库初始化函数（已在上面定义）
db_path = utils.read_config()['db']['path']
def send_command(vehicle_id, command, throttle, brake, steer):
    """
    向数据库发送命令。
    
    :param db_path: 数据库文件路径
    :param command: 命令文本
    :param throttle: 油门值
    :param brake: 制动值
    :param steer: 转向值
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    if command is None or throttle is None or brake is None or steer is None or vehicle_id is  None:
        raise TypeError("Command, throttle, brake, and steer cannot be None.")
    # 插入命令到数据库
    cursor.execute('''
        INSERT INTO commands (vehicle_id, command, throttle, brake, steer, timestamp)
        VALUES (?,?,?,?,?,?)
    ''', (vehicle_id, command, throttle, brake, steer, datetime.now()))

    # 返回命令ID
    command_id = cursor.lastrowid
    # 提交更改并关闭连接
    conn.commit()
    conn.close()
    return command_id

def receive_command(command_id=None):
    """
    从数据库接收命令。
    
    :param db_path: 数据库文件路径
    :param command_id: 要接收的命令ID，如果为None则返回所有命令
    :return: 命令列表或单个命令
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    if command_id is not None:
        # 根据ID接收命令
        cursor.execute('''
            SELECT * FROM commands WHERE id = ?
        ''', (command_id,))
        command = cursor.fetchone()
        conn.close()
        return command
    else:
        # 获取最新的一条
        cursor.execute('''
            SELECT * FROM commands ORDER BY id DESC LIMIT 1
        ''')
        command = cursor.fetchone()
        conn.close()
        return command
        
