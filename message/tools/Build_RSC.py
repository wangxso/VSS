import bisect
import math
from .Message  import *
import datetime
import json


def getRSCData(rsu_info,RSCInfo):
    # 创建RSC消息帧
    RSC_msgCount = 0
    RSCData=MsgFrame.RSC_MsgFrame()
    try:
        earth_radius = 6371004
        RSC_msgCount += 1
        if RSC_msgCount>=127:
            RSC_msgCount = RSC_msgCount -127
        RSCData['msgCnt'] = RSC_msgCount
        # RSCData['id']=str.encode('1') 
        integer_id = int(1)
        bytes_id= integer_id.to_bytes(8, 'big')            
        RSCData['id']=bytes_id
        RSCData['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
        lat = (rsu_info[2]) * 180.0 / (math.pi * earth_radius) + 37.788204
        longi = ((rsu_info[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (122.399498)
        RSCData['refPos']['lat']=int(10000000 * lat)
        RSCData['refPos']['long']=int(10000000 * longi)
        RSCData['refPos']['elevation']=int(rsu_info[3])


        coordinates = RSC.coordinates()
        integer_id = int(1)  #demo里这边是主车的ID
        bytes_id= integer_id.to_bytes(8, 'big')            
        coordinates['vehId'] = bytes_id
        cb_value = [0,0,0,0,0, 0,0,0,0,0, 0,1,0,0]  #slow-down(11)
        RSCInfo[6][6] = RSCInfo[6][6]*0.6           #主车减速 
        coordinates['driveSuggestion'] = {}
        # cb = [0,0]
        # cb[0] = 128*cb_value[0]+64*cb_value[1]+32*cb_value[2]+16*cb_value[3]+8*cb_value[4]+4*cb_value[5]+2*cb_value[6]+cb_value[7]
        # cb[1] = 128*cb_value[8]+64*cb_value[9]+32*cb_value[10]+16*cb_value[11]+8*cb_value[12]+4*cb_value[13]
        # coordinates['driveSuggestion']['suggestion'] = (bytes(bytearray(cb)), 14)
        cb = [0]
        cb[0] = (128*cb_value[0]+64*cb_value[1]+32*cb_value[2]+16*cb_value[3]+8*cb_value[4]+4*cb_value[5]+2*cb_value[6]+cb_value[7]) *64 + 32*cb_value[8]+16*cb_value[9]+8*cb_value[10]+4*cb_value[11]+2*cb_value[12]+1*cb_value[13]
        coordinates['driveSuggestion']['suggestion'] = ((cb[0]).to_bytes(2, byteorder="big"), 14)
        coordinates['driveSuggestion']['lifeTime'] = 10
        # coordinates['pathGuidance'] = {}
        # coordinates['pathGuidance']['pos'] = {}
        # coordinates['pathGuidance']['pos']['lat']= 23 
        # coordinates['pathGuidance']['pos']['long']= 121
        # coordinates['pathGuidance']['pos']['elevation']= 0
        # coordinates['pathGuidance']['estimatedTime'] = 7.89
        # coordinates['pathGuidance']['timeConfidence'] = 456
        sl_ego = RSCInfo[5]
        sl_list = [0]       #计算累计车辆位移距离
        sl_temp_list = [0]  #计算分段车辆位移距离
        s_ = 0
        for i in range(len(RSCInfo[4])):
            if len(RSCInfo[4])<2:
                print('No PathPlanningPoint')
            else:
                if i >0:
                    temp_dis = math.sqrt((RSCInfo[4][i][0]-RSCInfo[4][i-1][0])*(RSCInfo[4][i][0]-RSCInfo[4][i-1][0])+(RSCInfo[4][i][1]-RSCInfo[4][i-1][1])*(RSCInfo[4][i][1]-RSCInfo[4][i-1][1]))
                    s_ += temp_dis
                    sl_list.append(s_)
                    sl_temp_list.append(temp_dis)

        pathPlanningPoints = []
        if sl_list[-1]<sl_ego+RSCInfo[6][6]*8:
            print('No Enough PathPlanningPoint')
        else:
            index = bisect.bisect(sl_list, sl_ego)
            if sl_list[index] >= sl_ego+RSCInfo[6][6]*8:
                for i in range(80):
                    temp_dis2 = math.sqrt((RSCInfo[4][index][0]-RSCInfo[6][0])*(RSCInfo[4][index][0]-RSCInfo[6][0])+(RSCInfo[4][index][1]-RSCInfo[6][1])*(RSCInfo[4][index][1]-RSCInfo[6][1]))
                    pathPlanningPoints.append([RSCInfo[6][0]+ RSCInfo[6][6]*0.1*i*(RSCInfo[4][index][0]-RSCInfo[6][0])/(temp_dis2), RSCInfo[6][1]+ RSCInfo[6][6]*0.1*i*(RSCInfo[4][index][1]-RSCInfo[6][1])/(temp_dis2)])
            else: #暂时先简略处理
                index = bisect.bisect(sl_list, sl_ego+RSCInfo[6][6]*8)
                for i in range(80):
                    temp_dis2 = math.sqrt((RSCInfo[4][index][0]-RSCInfo[6][0])*(RSCInfo[4][index][0]-RSCInfo[6][0])+(RSCInfo[4][index][1]-RSCInfo[6][1])*(RSCInfo[4][index][1]-RSCInfo[6][1]))
                    pathPlanningPoints.append([RSCInfo[6][0]+ RSCInfo[6][6]*0.1*i*(RSCInfo[4][index][0]-RSCInfo[6][0])/(temp_dis2), RSCInfo[6][1]+ RSCInfo[6][6]*0.1*i*(RSCInfo[4][index][1]-RSCInfo[6][1])/(temp_dis2)])
        # print('RSCInfo[6]',RSCInfo[6]) 
        # print('RSCpathPlanningPoints',pathPlanningPoints)
            
        coordinates['pathGuidance'] = []
        for point in pathPlanningPoints:
            pathPlanningPoint = {}
            lat = (point[1]) * 180.0 / (math.pi * earth_radius) + RSCInfo[0][0]  #39.5427 
            longi = ((point[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (RSCInfo[0][1])  #(116.2317)
            pathPlanningPoint['pos'] = {}      
            pathPlanningPoint['pos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
            pathPlanningPoint['pos']['offsetV'] = ('elevation', 0)
            coordinates['pathGuidance'].append(pathPlanningPoint)

        cinfo = [0,0,0,0,0,0,1,0]
        cb2 = [0]
        cb2[0] = 128*cinfo[0]+64*cinfo[1]+32*cinfo[2]+16*cinfo[3]+8*cinfo[4]+4*cinfo[5]+2*cinfo[6]+cinfo[7] 
        # bytes_cinfo= cb2[0].to_bytes(1, 'big')  
        # cb2 = bytearray(cb2)
        # coordinates['info'] = (bytes(cb2), 8)
        coordinates['info'] = ((cb2[0]).to_bytes(1, byteorder="big"),8)

        RSCData['coordinates'].append(coordinates) 


        laneCoordinates = RSC.laneCoordinates()
        referenceLink = {}
        referenceLink['upstreamNodeId'] = {}
        referenceLink['upstreamNodeId']['region'] = 0
        referenceLink['upstreamNodeId']['id'] = 2
        referenceLink['downstreamNodeId'] = {}
        referenceLink['downstreamNodeId']['region'] = 0
        referenceLink['downstreamNodeId']['id'] = 1
        rl_value = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
        rl = [0,0]
        for item in RSCInfo[3]:  #currentEdgeLanes
            if int(item)<=15:
                rl_value[int(item)] = 1
        rl[0] = 128*rl_value[0]+64*rl_value[1]+32*rl_value[2]+16*rl_value[3]+8*rl_value[4]+4*rl_value[5]+2*rl_value[6]+rl_value[7]
        rl[1] = 128*rl_value[8]+64*rl_value[9]+32*rl_value[10]+16*rl_value[11]+8*rl_value[12]+4*rl_value[13]+2*rl_value[14]+rl_value[15]
        referenceLink['referenceLanes'] = {}
        referenceLink['referenceLanes'] = (bytes(rl), 16)
        laneCoordinates['targetLane'] = referenceLink
        ReferencePath = {}
        ReferencePath['activePath'] = []
        activePathPoints = RSCInfo[4]  #plan_pathPoints [(x,y,type,lane)]
        for i in range(len(activePathPoints)):
            activePathPoint=RSI.RSIPathPoint_DF()
            lat1 = (activePathPoints[i][1]) * 180.0 / (math.pi * earth_radius) + RSCInfo[0][0] 
            longi1 = ((activePathPoints[i][0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat1 * math.pi / 180.0) + (RSCInfo[0][1])
            activePathPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi1), 'lat':int(10000000 * lat1)})
            ReferencePath['activePath'].append(activePathPoint)
        ReferencePath['pathRadius'] = 200
        laneCoordinates['relatedPath'] = ReferencePath
        tBegin = {}
        now = datetime.datetime.now()
        tBegin['year'] = now.year
        tBegin['month'] = now.month
        tBegin['day'] = now.day
        tBegin['hour'] = now.hour
        tBegin['minute'] = now.minute 
        tBegin['second'] = now.microsecond
        tBegin['offset'] = 0
        laneCoordinates['tBegin'] = tBegin
        tEnd = {} 
        tEnd['year'] = now.year
        tEnd['month'] = now.month
        tEnd['day'] = now.day
        tEnd['hour'] = now.hour
        tEnd['minute'] = now.minute 
        tEnd['second'] = now.microsecond
        tEnd['offset'] = 0
        laneCoordinates['tEnd'] = tEnd
        laneCoordinates['recommendedSpeed'] = int(RSCInfo[6][6]*0.6*50)       #主车减速
        cb_value = [0,0,0,0,0, 1,0,0,    0,0, 0,1,0,0]
        cb = [0,0]
        cb[0] = 128*cb_value[0]+64*cb_value[1]+32*cb_value[2]+16*cb_value[3]+8*cb_value[4]+4*cb_value[5]+2*cb_value[6]+cb_value[7]
        cb[1] = 128*cb_value[8]+64*cb_value[9]+32*cb_value[10]+16*cb_value[11]+8*cb_value[12]+4*cb_value[13]
        laneCoordinates['recommendedBehavior'] = (bytes(cb), 14)
        laneCoordinates['info'] = ((cb2[0]).to_bytes(1, byteorder="big"),8)
        laneCoordinates['description'] = ('textGB2312','No description'.encode("gb2312", 'ignore'))

        # del laneCoordinates['targetLane']
        # del laneCoordinates['relatedPath']
        # del laneCoordinates['tBegin']
        # del laneCoordinates['tEnd']
        # del laneCoordinates['recommendedSpeed']
        # del laneCoordinates['recommendedBehavior']
        # del laneCoordinates['info']
        # del laneCoordinates['description']

        RSCData['laneCoordinates'].append(laneCoordinates)
    except Exception as ex:
        print('ex',ex)
        print(ex.__traceback__.tb_lineno) 
        return RSCData
    else:
        return RSCData
