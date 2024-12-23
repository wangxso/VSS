import math
from .Message  import *
import datetime
import json
import os
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)

def getRTCMData():

    RTCM_msgCount = 0
    RTCMData=MsgFrame.RTCM_MsgFrame()
    try:
        RTCM_msgCount += 1
        if RTCM_msgCount>=127:
            RTCM_msgCount = RTCM_msgCount -127

        RTCMData['msgCnt'] = RTCM_msgCount

        rTCMmsg = RTCM.RTCMmsg()
        rTCMmsg['rev'] = 1

        rTCMmsg['rtcmID'] = 1
        rTCMmsg['payload'] = bytes(1)
        RTCMData['corrections'].append(rTCMmsg)

    except Exception as ex:
        print(ex)
        print(ex.__traceback__.tb_lineno) 
        return RTCMData
 
    return RTCMData



