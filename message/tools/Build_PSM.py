from ...message import MsgFrame
from loguru import logger
import math
import datetime
import json
import os
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)


def getPSMData(PSMInfo):   #[basell,pedestrians,userData['pedestrians_points']]    [id,type,shape,x,y,z,yaw,pitch,roll,speed]
    PSM_msgCount = 0
    PSMData=MsgFrame.PSM_MsgFrame()
    try:
        pedestrian_num = 0
        earth_radius = 6371004
        PSM_msgCount += 1
        if PSM_msgCount>=127:
            PSM_msgCount = PSM_msgCount -127

        PSMData['msgCnt'] = PSM_msgCount
        PSMData['id'] = str.encode('00000000')
        PSMData['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
        lat = (PSMInfo[1][pedestrian_num][4]) * 180.0 / (math.pi * earth_radius) + PSMInfo[0][0]
        longi = ((PSMInfo[1][pedestrian_num][3]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (PSMInfo[0][1]) 
        PSMData['pos']['long']=int(10000000 * longi)
        PSMData['pos']['lat']=int(10000000*lat)
        PSMData['pos']['elevation']=int(PSMInfo[1][pedestrian_num][5])
        
        PSMData['speed']=round(PSMInfo[1][pedestrian_num][9]/0.02)
        
        ped_yaw = PSMInfo[1][pedestrian_num][6]
        if ped_yaw < 0:
            ped_yaw+=360
        if ped_yaw> 359.9875:
            ped_yaw -=359.9875 
        PSMData['heading']=round(ped_yaw/0.0125)
        PSMData['accelSet'] = {}
        PSMData['accelSet']['long'] = 0
        PSMData['accelSet']['lat'] = 0
        PSMData['accelSet']['vert'] = 0
        PSMData['accelSet']['yaw'] = 0

        PSMData['pathHistory'] = {}
        PSMData['pathHistory']['initialPosition'] = {}
        now = datetime.datetime.now()
        utcTime = {}
        utcTime['year'] = now.year
        utcTime['month'] = now.month
        utcTime['day'] = now.day
        utcTime['hour'] = now.hour
        utcTime['minute'] = now.minute 
        utcTime['second'] = now.microsecond
        utcTime['offset'] = 0
        PSMData['pathHistory']['initialPosition']['utcTime'] = utcTime

        PSMData['pathHistory']['initialPosition']['pos'] = {}
        pedestrian_num_key = list(PSMInfo[2].keys())[pedestrian_num]
        pedestrian_num_value = PSMInfo[2][pedestrian_num_key]

        if len(pedestrian_num_value)>0:
            lat = (PSMInfo[2][pedestrian_num_key][0][3]) * 180.0 / (math.pi * earth_radius) + PSMInfo[0][0] 
            longi = ((PSMInfo[2][pedestrian_num_key][0][2]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (PSMInfo[0][1]) 
            PSMData['pathHistory']['initialPosition']['pos']['lat'] = int(10000000 * lat)
            PSMData['pathHistory']['initialPosition']['pos']['long'] = int(10000000 * longi)
            PSMData['pathHistory']['initialPosition']['pos']['elevation'] = int(10 * PSMInfo[2][pedestrian_num_key][0][4])  # in 10 cm units
            if PSMInfo[2][pedestrian_num_key][0][5] < 0:
                PSMInfo[2][pedestrian_num_key][0][5]+=360
            if PSMInfo[2][pedestrian_num_key][0][5]> 359.9875:
                PSMInfo[2][pedestrian_num_key][0][5] -=359.9875 
            PSMData['pathHistory']['initialPosition']['heading'] = round(PSMInfo[2][pedestrian_num_key][0][5]/0.0125)
            PSMData['pathHistory']['initialPosition']['transmission'] = 7
            PSMData['pathHistory']['initialPosition']['speed'] = round(PSMInfo[2][pedestrian_num_key][0][8]/0.02)
            posAccuracy = {}
            posAccuracy['pos'] = 9
            posAccuracy['elevation'] = 9
            PSMData['pathHistory']['initialPosition']['posAccuracy'] = posAccuracy
            PSMData['pathHistory']['initialPosition']['timeConfidence'] = 0
            motionCfd = {} 
            motionCfd['speedCfd'] = 0
            motionCfd['headingCfd'] = 0
            motionCfd['steerCfd'] = 0
            PSMData['pathHistory']['initialPosition']['motionCfd'] = motionCfd
        else:
            PSMData['pathHistory'].pop('initialPosition')
    
        pinfo = [0,0,0,0,0,0,0,0]
        pb2 = [0]
        pb2[0] = 128*pinfo[0]+64*pinfo[1]+32*pinfo[2]+16*pinfo[3]+8*pinfo[4]+4*pinfo[5]+2*pinfo[6]+pinfo[7] 
        PSMData['pathHistory']['currGNSSstatus'] = (bytes(pb2),8) #((pb2[0]).to_bytes(1, byteorder="big"),8)
        if len(PSMInfo[2][pedestrian_num_key])>1:
            crumbData = []
            for i in range(len(PSMInfo[2][pedestrian_num_key])-1):
                pathHistoryPoint = {}
                llvOffset = {}
                Position_LL_24B = {}
                lat0 = (PSMInfo[2][pedestrian_num_key][i][3]) * 180.0 / (math.pi * earth_radius) + PSMInfo[0][0] 
                long0 = ((PSMInfo[2][pedestrian_num_key][i][2]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat0 * math.pi / 180.0) + (PSMInfo[0][1])
                lat1 = (PSMInfo[2][pedestrian_num_key][i+1][3]) * 180.0 / (math.pi * earth_radius) + PSMInfo[0][0] 
                long1 = ((PSMInfo[2][pedestrian_num_key][i+1][2]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat1 * math.pi / 180.0) + (PSMInfo[0][1])
                Position_LL_24B['lon'] = int(10000000 * (long1 - long0))
                Position_LL_24B['lat'] = int(10000000 * (lat1 - lat0))
                llvOffset['offsetLL'] = ('position-LL1',Position_LL_24B)
                # llvOffset['offsetLL'] = ('position-LatLon', {'lon':int(10000000 * long1), 'lat':int(10000000 * lat1)})
                llvOffset['offsetV'] = ('offset1',0)
                pathHistoryPoint['llvOffset'] = llvOffset
                pathHistoryPoint['timeOffset'] = 1
                pathHistoryPoint['speed'] = round(PSMInfo[2][pedestrian_num_key][i+1][8]/0.02)
                if PSMInfo[2][pedestrian_num_key][i+1][5] < 0:
                    PSMInfo[2][pedestrian_num_key][i+1][5]+=360
                if PSMInfo[2][pedestrian_num_key][i+1][5]> 359.9875:
                    PSMInfo[2][pedestrian_num_key][i+1][5] -=359.9875 
                pathHistoryPoint['heading'] = round(PSMInfo[2][pedestrian_num_key][i+1][5]/0.0125)
                crumbData.append(pathHistoryPoint)
            PSMData['pathHistory']['crumbData'] = crumbData  #SEQUENCE (SIZE(1..23)) OF PathHistoryPoint
        else:   
            PSMData['pathHistory'].pop('crumbData')


        pathPlanningPoints = []
        if len(PSMInfo[2][pedestrian_num_key])>1:
            dif_x = PSMInfo[2][pedestrian_num_key][-1][2] - PSMInfo[2][pedestrian_num_key][-2][2]   #每10ms的x方向上的距离差值
            dif_y = PSMInfo[2][pedestrian_num_key][-1][3] - PSMInfo[2][pedestrian_num_key][-2][3]   #每10ms的y方向上的距离差值
            for i in range(20):
                pathPlanningPoints.append([PSMInfo[2][pedestrian_num_key][-1][2]+dif_x*10*i ,PSMInfo[2][pedestrian_num_key][-1][3]+dif_y*10*i])
        for point in pathPlanningPoints:
            pathPlanningPoint = {}
            lat = (point[1]) * 180.0 / (math.pi * earth_radius) + PSMInfo[0][0]  #39.5427 
            longi = ((point[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (PSMInfo[0][1])  #(116.2317)
            pathPlanningPoint['pos'] = {}      
            pathPlanningPoint['pos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
            pathPlanningPoint['pos']['offsetV'] = ('elevation', 0)
            PSMData['path-Planning'].append(pathPlanningPoint)

        PSMData['overallRadius'] = 100 

        PSMData['non-motorData'] = {}
        PSMData['non-motorData']['basicType'] = 1
        PSMData['non-motorData']['propulsion'] = ('human',2)
        PSMData['non-motorData']['clusterSize'] = 1
        PSMData['non-motorData']['attachment'] = 0

        personalExt = {}
        state=[0,0]
        sta = [0,0,0,0, 0,0,0,0, 0]
        state[0]=128*sta[0]+64*sta[1]+32*sta[2]+16*sta[3]+8*sta[4]+4*sta[5]+2*sta[6]+sta[7]
        state[1]=128*sta[8]
        personalExt['useState'] = (bytes(state),9)
        assistType=[0]
        assistTy = [0,0,0,0, 0,0]
        assistType[0]=128*assistTy[0]+64*assistTy[1]+32*assistTy[2]+16*assistTy[3]+8*assistTy[4]+4*assistTy[5]
        personalExt['assistType'] = (bytes(assistType),6)
        PSMData['non-motorData']['personalExt'] = personalExt

        roadWorkerExt = {}
        roadWorkerExt['workerType'] = 0
        activityType=[0]
        activityTy = [0,0,0,0, 0,0]
        activityType[0]=128*activityTy[0]+64*activityTy[1]+32*activityTy[2]+16*activityTy[3]+8*activityTy[4]+4*activityTy[5]
        roadWorkerExt['activityType'] = (bytes(activityType),6)
        PSMData['non-motorData']['roadWorkerExt'] = roadWorkerExt

        personalReq = {}
        personalReq['crossing'] = 0
        PSMData['non-motorData']['personalReq'] = personalReq

        # PSMData.pop('pathHistory')
        # PSMData['pathHistory'].pop('initialPosition')
        # PSMData['pathHistory'].pop('currGNSSstatus')
        # PSMData['pathHistory'].pop('crumbData')

    except Exception as ex:
        print(ex)
        print(ex.__traceback__.tb_lineno) 
        return PSMData
 
    return PSMData



