import os
import pytest
from utils import read_config

# Test that the config file is successfully read
def test_read_config_success():
    config = read_config()
    assert config is not None

# Test that the config file contains the expected keys
def test_read_config_keys():
    config = read_config()
    assert 'db' in config
    assert 'v2x' in config

# Test that the config file values are correct
def test_read_config_values():
    config = read_config()
    assert config['db']['path'] == 'C:\\PanoSimDatabase\\Plugin\\Agent\\commands.db'
    assert config['v2x']['communication_range'] == 1000
