import sqlite3
import json
import time

def send_command(db_path, command_data):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 插入指令
    cursor.execute('''
        INSERT INTO commands (command, throttle, brake, steer)
        VALUES (?, ?, ?, ?)
    ''', (command_data['command'], command_data['throttle'], command_data['brake'], command_data['steer']))

    conn.commit()
    conn.close()



def get_latest_command(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取最新的指令
    cursor.execute('''
        SELECT id, command, throttle, brake, steer, timestamp
        FROM commands
        ORDER BY timestamp DESC
        LIMIT 1
    ''')

    row = cursor.fetchone()
    if row:
        command_data = {
            'id': row[0],
            'command': row[1],
            'throttle': row[2],
            'brake': row[3],
            'steer': row[4],
            'timestamp': row[5]
        }
        conn.close()

        return command_data
    else:
        conn.close()
        return None




