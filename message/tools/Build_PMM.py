from ...message import MsgFrame
from loguru import logger
import math
import datetime
import json
import os
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)


def getPMMData(vehicles):
    # 创建RSI消息帧
    PMM_msgCount = 0
    PMMData=MsgFrame.PMM_MsgFrame()
    try:
        PMM_msgCount += 1
        if PMM_msgCount>=127:
            PMM_msgCount = PMM_msgCount -127

        PMMData['msgCnt'] = PMM_msgCount
        # PMMData['id']='1' #rsu暂时无ID属性，暂置为1
        PMMData['id']=str.encode('00000001')
        PMMData['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
        bytes_pid = vehicles[0].to_bytes(11, 'big') 
        PMMData['pid']=bytes_pid   #str.encode(str(vehicles[0]))  #Platooning ID
        PMMData['role'] = 0
        PMMData['status'] = 0
        
        PMMData['leadingExt'] = {}
        memberList = []
        for i in range(len(vehicles)):
            bytes_vid= vehicles[i].to_bytes(8, 'big')    
            memberList.append({'vid':bytes_vid})
            # memberList.append({'vid':str.encode(str(vehicles[i]))})
        # PMMData['leadingExt']['memberList'] = [vehicles[1],vehicles[2],vehicles[3],vehicles[4]] 
        PMMData['leadingExt']['memberList'] = memberList
        PMMData['leadingExt']['joiningList'] = []
        PMMData['leadingExt']['leavingList'] = []
        PMMData['leadingExt']['capacity'] = 10
        PMMData['leadingExt']['openToJoin'] = True
        if len(PMMData['leadingExt']['joiningList']) == 0:
            PMMData['leadingExt'].pop('joiningList')
        if len(PMMData['leadingExt']['leavingList']) == 0:
            PMMData['leadingExt'].pop('leavingList')            

    except Exception as ex:
        print(ex)
        print(ex.__traceback__.tb_lineno) 
        return PMMData
 
    return PMMData



