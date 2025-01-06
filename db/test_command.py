import logging
import pytest
import sqlite3
from db.command import receive_command
import pytest
import sqlite3
from db.command import send_command
import utils
# 定义一个fixture来加载配置文件
@pytest.fixture(scope="session")
def config():
    return utils.read_config()

# 定义一个fixture来获取数据库路径
@pytest.fixture(scope="session")
def db_path(config):
    return config["db"]["path"]

# 定义一个fixture来创建数据库连接
@pytest.fixture(scope="session")
def db_connection(db_path):
    conn = sqlite3.connect(db_path)
    yield conn
    conn.close()
logging.basicConfig(level=logging.INFO)

# Test sending a valid command
def test_send_command_valid(db_path, db_connection):
    command = "Test Command"
    throttle = 0.5
    brake = 0.2
    steer = 0.3

    send_command(command, throttle, brake, steer)

    # Check if the command was inserted into the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM commands WHERE command=?", (command,))
    result = cursor.fetchone()
    conn.close()

    assert result is not None
    assert result[1] == command
    assert result[2] == throttle
    assert result[3] == brake
    assert result[4] == steer

# Test sending a command with missing parameters
def test_send_command_missing_parameters(db_path, db_connection):
    command = "Test Command"
    throttle = None
    brake = 0.2
    steer = 0.3

    with pytest.raises(TypeError):
        send_command(command, throttle, brake, steer)



def test_receive_command_valid(db_path, db_connection):
    command = "Test Command"
    throttle = 0.5
    brake = 0.2
    steer = 0.3

    commands = receive_command()

    assert len(commands) > 0

def test_send_and_receive_command(db_path, db_connection):
    command = "Test Command"
    throttle = 0.5
    brake = 0.2
    steer = 0.3
    command_id = send_command( command, throttle, brake, steer)
    commands = receive_command(command_id=command_id)
    logging.info(f'{commands}')
    assert commands is not None
    assert commands[1] == command
    assert commands[2] == throttle
    assert commands[3] == brake
    assert commands[4] == steer

