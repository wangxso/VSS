import sqlite3
from datetime import datetime

from loguru import logger
import utils
import os
import redis

# 数据库初始化函数（已在上面定义）
# dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
# db_path = os.path.join(dir, 'commands.db')

def init_redis():
    # 初始化redis
    global r
    r = redis.Redis(host='localhost', port=6379, db=0)
    # 清空数据库
    r.flushdb()
    logger.info("Redis 数据库已初始化并清空。")

def send_command(vehicle_id, command, throttle, brake, steer, speed):
    """
    发送控制命令到Redis，并设置1秒过期时间。
    返回: command_id (int)
    """
    if None in (vehicle_id, command, throttle, brake, steer):
        raise ValueError("必需参数不能为None")

    # 生成命令ID（原子操作）
    command_id = r.incr('global:command_id')

    # 命令 key
    command_key = f"command:{command_id}"

    # 存储命令详情（哈希结构）
    r.hset(command_key, mapping={
        'id': command_id,
        'vehicle_id': vehicle_id,
        'command': command,
        'throttle': str(throttle),
        'brake': str(brake),
        'steer': str(steer),
        'speed': str(speed),
        'timestamp': datetime.now().isoformat()
    })

    # 设置10秒过期时间
    r.expire(command_key, 1)

    # 加入全局队列（列表结构）
    r.lpush('command_queue', command_id)

    # 记录车辆关联命令（集合结构）
    r.sadd(f'vehicle:{vehicle_id}:commands', command_id)

    return command_id

def receive_command(command_id=None, vehicle_id=None, block=False, timeout=10):
    """
    获取命令
    参数:
        block - 是否阻塞等待
        timeout - 阻塞超时(秒)
    返回: 命令字典 或 None
    """
    if command_id:
        return r.hgetall(f"command:{command_id}")
    
    if vehicle_id:
        latest_id = r.lindex(f'vehicle:{vehicle_id}:commands', -1)
        return r.hgetall(f"command:{latest_id}") if latest_id else None
    
    if block:
        # 阻塞式获取（BRPOP）
        result = r.brpop('command_queue', timeout=timeout)
        if result:
            return r.hgetall(f"command:{result[1]}")
        return None
    else:
        # 非阻塞获取（RPOP）
        command_id = r.rpop('command_queue')
        return r.hgetall(f"command:{command_id}") if command_id else None
