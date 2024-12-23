#!/usr/bin/env python   V2X消息数据包安全层的添加
# -*- encoding: utf-8 -*-
'''
@File    :    .py
@Time    :   2024/03/13
@Author  :   ldy
@Version :   1.0
'''

import mmap
from pickle import FALSE
import re
import threading
import numpy as np
# from paramiko import Agent
from DataInterfacePython import *
import math
from xml.dom.minidom import parseString
from V2X.Message import *
from V2X import Build_BSM
from V2X import Build_RSI
from V2X import Build_RSM
from V2X import Build_SPAT
from V2X import Build_SSM
from V2X import Build_PMM
from V2X import Build_VIR
from V2X import Build_RSC
import base64
import sys
import datetime
import json
import asn1tools
import os
from socket import *
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)
 
ltevCoder = None
ltevCoder_2 = None

def Warning(userData,level,warn):
    bus = userData["warning"].getBus()
    size = userData["warning"].getHeaderSize()
    bus[size:size + len(warn)] = '{}'.format(warn).encode()
    userData["warning"].writeHeader(*(userData["time"], level, len(warn)))

def VehicleControl(userData, valid, throttle, brake, steer, mode, gear):
    userData['ego_control'].writeHeader(*(userData['time'], valid, throttle, brake, steer, mode, gear))
            