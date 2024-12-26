import bisect
import math
from .Message  import *
import datetime
import json
import os
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)


def getVIRData(ego,participants,object,scenario,VIRInfo):  #VIRInfo =  [taskRoute,currentEdge,currentEdgeLanes,plan_pathPoints]
    # 创建VIR消息帧
    VIR_msgCount = 0
    VIRData=MsgFrame.VIR_MsgFrame()
    try:
        earth_radius = 6371004
        VIR_msgCount += 1
        if VIR_msgCount>=127:
            VIR_msgCount = VIR_msgCount -127

        VIRData['msgCnt'] = VIR_msgCount
        VIRData['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)

        if object=='HV':
            integer_id = int(1)
            bytes_id= integer_id.to_bytes(8, 'big')            
            VIRData['id']=bytes_id #'00000001' #temperary vehicle ID   same as id in BSM
            lat = (ego[1]) * 180.0 / (math.pi * earth_radius) + VIRInfo[0][0]
            longi = ((ego[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (VIRInfo[0][1]) 
            VIRData['refPos']['lat']=int(10000000 * lat)
            VIRData['refPos']['long']=int(10000000 * longi)
            VIRData['refPos']['elevation']=int(ego[2])

        
        if object=='RV':
            # print('x,y',participants[0][3],participants[0][4])
            integer_id = int(2)
            bytes_id= integer_id.to_bytes(8, 'big')            
            VIRData['id']=bytes_id
            lat = (participants[0][4]) * 180.0 / (math.pi * earth_radius) + VIRInfo[0][0] 
            longi = ((participants[0][3]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (VIRInfo[0][1])      
            VIRData['refPos']['lat']=int(10000000 * lat)
            VIRData['refPos']['long']=int(10000000 * longi)
            VIRData['refPos']['elevation']=int(participants[0][5])


        # pathPlanningPoint_currentPos = VIR.pathPlanningPoint()
        # pathPlanningPoint_currentPos['posInMap'] ['upstreamNodeId']=0
        # pathPlanningPoint_currentPos['posInMap'] ['downstreamNodeId']=0
        # VIRData['intAndReq']['currentPos'] = pathPlanningPoint_currentPos

        cb_value = [1,0,0,0,0, 0,0,0,0,0, 0,0,0,0]
        cb = [0,0]
        
        cb[0] = 128*cb_value[0]+64*cb_value[1]+32*cb_value[2]+16*cb_value[3]+8*cb_value[4]+4*cb_value[5]+2*cb_value[6]+cb_value[7]
        cb[1] = 128*cb_value[8]+64*cb_value[9]+32*cb_value[10]+16*cb_value[11]+8*cb_value[12]+4*cb_value[13]
        # print('cb',cb)
        VIRData['intAndReq']['currentBehavior'] = (bytes(cb), VIRData['intAndReq']['currentBehavior'][1])
        
        reqs = VIR.reqs()
        reqs['reqID'] = 10 
        reqs['status'] = 1
        integer_reqPriority = 1
        bytes_reqPriority= integer_reqPriority.to_bytes(1, 'big')
        reqs['reqPriority'] = bytes_reqPriority #bytes(2) #'00000002'
        # reqs['reqPriority'] = [[0], 8] 
        integer_targetVeh = 2
        bytes_targetVeh = integer_targetVeh.to_bytes(8, 'big')
        reqs['targetVeh'] = bytes_targetVeh #bytes(2) #'00000002'
        # print('bytes_targetVeh',int.from_bytes(bytes_targetVeh,'big') )
        integer_targetRSU = 101
        bytes_targetRSU = integer_targetRSU.to_bytes(8, 'big')
        reqs['targetRSU'] = bytes_targetRSU #bytes(3)  #'00000101'
        reqs['info'] = {} #组包时提供所有选项
        reqs['lifeTime'] = 5 

        if scenario == 'CLC':
            laneChange ={'upstreamNode':{'region':3,'id':20},'downstreamNode':{'region':4,'id':30},'targetLane':2}  #TODO
            # laneChange['upstreamNode']['region'] = 3    #进入Link的Node
            # laneChange['upstreamNode']['id'] = 20
            # laneChange['downstreamNode']['region'] = 4  #出Link的Node
            # laneChange['downstreamNode']['id'] = 30
            # laneChange['targetLane'] = 2                #要变道的目标Lane
            reqs['info'] = ('laneChange',laneChange) 

			
        if scenario == 'CVM':
            laneChange ={'upstreamNode':{'region':3,'id':20},'downstreamNode':{'region':4,'id':30},'targetLane':2}  #TODO
            reqs['info'] = ('laneChange',laneChange) 


        if scenario == 'SSM':
            reqs['info']['reqType'] = 3
            activePath_points = []
            activePath_points.append({"lat": 89.1111110,
                                    "long": 135.1111100,
                                    "elevation": 99.9})
            activePath_points.append({"lat": 90.1111110,
                                    "long": 136.1111100,
                                    "elevation": 100.9})
            reqs['info']['sensorSharing']['detectArea']['activePath']  = activePath_points
            reqs['info']['sensorSharing']['detectArea']['pathRadius']  = 10.5


        if scenario == 'CIP':
            laneChange ={'upstreamNode':{'region':3,'id':20},'downstreamNode':{'region':4,'id':30},'targetLane':2}  #TODO
            reqs['info'] = ('laneChange',laneChange) 


        VIRData['intAndReq']['reqs'].append(reqs) 
        


        currentPos = VIR.pathPlanningPoint()   
        referenceLink = {}
        referenceLink['upstreamNodeId'] = {}
        referenceLink['upstreamNodeId']['region'] = 0
        referenceLink['upstreamNodeId']['id'] = 2
        referenceLink['downstreamNodeId'] = {}
        referenceLink['downstreamNodeId']['region'] = 0
        referenceLink['downstreamNodeId']['id'] = 1
        rl_value = [0,0,0,0, 0,0,0,0, 0,0,0,0, 0,0,0,0]
        rl = [0,0]
        for item in VIRInfo[3]:  #currentEdgeLanes
            if int(item)<=15:
                rl_value[int(item)] = 1
        rl[0] = 128*rl_value[0]+64*rl_value[1]+32*rl_value[2]+16*rl_value[3]+8*rl_value[4]+4*rl_value[5]+2*rl_value[6]+rl_value[7]
        rl[1] = 128*rl_value[8]+64*rl_value[9]+32*rl_value[10]+16*rl_value[11]+8*rl_value[12]+4*rl_value[13]+2*rl_value[14]+rl_value[15]
        referenceLink['referenceLanes'] = {}
        referenceLink['referenceLanes'] = (bytes(rl), 16)
        currentPos['posInMap'] = referenceLink  
        print('referenceLink',referenceLink)
        if object=='HV':
            lat = (ego[1]) * 180.0 / (math.pi * earth_radius) + VIRInfo[0][0]  #39.5427 
            longi = ((ego[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (VIRInfo[0][1])  #(116.2317)
        if object=='RV':
            lat = (participants[0][4]) * 180.0 / (math.pi * earth_radius) + VIRInfo[0][0] 
            longi = ((participants[0][3]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (VIRInfo[0][1])  
        currentPos['pos'] = {}      
        currentPos['pos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
        currentPos['pos']['offsetV'] = ('elevation', 0)
        posAccuracy = {}
        posAccuracy['pos'] = 9
        posAccuracy['elevation'] = 9
        currentPos['posAccuracy'] = posAccuracy
        if object=='HV':
            currentPos['speed'] = int(ego[6]*50)
            currentPos['heading'] = int(ego[3]/0.0125)
            currentPos['accelSet']['long']= 0
            currentPos['accelSet']['lat']= 0
            currentPos['accelSet']['vert']= 0
            currentPos['accelSet']['yaw']= 0
        if object=='RV':
            currentPos['speed'] = int(participants[0][9]*50)
            currentPos['heading'] = int(participants[0][6]/0.0125)
            currentPos['accelSet']['long']= 0
            currentPos['accelSet']['lat']= 0
            currentPos['accelSet']['vert']= 0
            currentPos['accelSet']['yaw']= 0
        currentPos['speedCfd'] = 4
        currentPos['headingCfd'] = 4
        currentPos['acc4WayConfidence']['lonAccConfidence'] = 4
        currentPos['acc4WayConfidence']['latAccConfidence'] = 4
        currentPos['acc4WayConfidence']['vertAccConfidence'] = 4
        currentPos['acc4WayConfidence']['yawRateCon'] = 4
        currentPos['estimatedTime'] = 1    # TimeOffset ::= INTEGER (1..65535)  -- Units of of 10 mSec, 
        currentPos['timeConfidence'] = 0    # Confidence ::= INTEGER (0..200) -- Units of 0.5 percent
        VIRData['intAndReq']['currentPos'] = currentPos
  
        # del VIRData['intAndReq']['currentPos']['posInMap']
        # del VIRData['intAndReq']['currentPos']['posAccuracy']
        # del VIRData['intAndReq']['currentPos']['heading']
        # del VIRData['intAndReq']['currentPos']['headingCfd']
        # del VIRData['intAndReq']['currentPos']['accelSet']
        # del VIRData['intAndReq']['currentPos']['acc4WayConfidence']
        # del VIRData['intAndReq']['currentPos']['estimatedTime']
        # del VIRData['intAndReq']['currentPos']['timeConfidence']


        sl_ego = VIRInfo[5]
        sl_list = [0]       #计算累计车辆位移距离
        sl_temp_list = [0]  #计算分段车辆位移距离
        s_ = 0
        for i in range(len(VIRInfo[4])):
            if len(VIRInfo[4])<2:
                print('!!! No PathPlanningPoint')
            else:
                if i >0:
                    temp_dis = math.sqrt((VIRInfo[4][i][0]-VIRInfo[4][i-1][0])*(VIRInfo[4][i][0]-VIRInfo[4][i-1][0])+(VIRInfo[4][i][1]-VIRInfo[4][i-1][1])*(VIRInfo[4][i][1]-VIRInfo[4][i-1][1]))
                    s_ += temp_dis
                    sl_list.append(s_)
                    sl_temp_list.append(temp_dis)

        pathPlanningPoints = []
        if sl_list[-1]<sl_ego+ego[6]*8:
            print('!!! No Enough PathPlanningPoint')
        else:
            index = bisect.bisect(sl_list, sl_ego)
            if sl_list[index] >= sl_ego+ego[6]*8:
                for i in range(80):
                    temp_dis2 = math.sqrt((VIRInfo[4][index][0]-ego[0])*(VIRInfo[4][index][0]-ego[0])+(VIRInfo[4][index][1]-ego[1])*(VIRInfo[4][index][1]-ego[1]))
                    pathPlanningPoints.append([ego[0]+ ego[6]*0.1*i*(VIRInfo[4][index][0]-ego[0])/(temp_dis2), ego[1]+ ego[6]*0.1*i*(VIRInfo[4][index][1]-ego[1])/(temp_dis2)])
            else: #暂时先简略处理
                index = bisect.bisect(sl_list, sl_ego+ego[6]*8)
                for i in range(80):
                    temp_dis2 = math.sqrt((VIRInfo[4][index][0]-ego[0])*(VIRInfo[4][index][0]-ego[0])+(VIRInfo[4][index][1]-ego[1])*(VIRInfo[4][index][1]-ego[1]))
                    pathPlanningPoints.append([ego[0]+ ego[6]*0.1*i*(VIRInfo[4][index][0]-ego[0])/(temp_dis2), ego[1]+ ego[6]*0.1*i*(VIRInfo[4][index][1]-ego[1])/(temp_dis2)])
                    
        # print('ego',ego)
        # print('VIRpathPlanningPoints',pathPlanningPoints)
            
        VIRData['intAndReq']['path-Planning'] = []
        for point in pathPlanningPoints:
            pathPlanningPoint = {}
            lat = (point[1]) * 180.0 / (math.pi * earth_radius) + VIRInfo[0][0]  #39.5427
            longi = ((point[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (VIRInfo[0][1])  #(116.2317)
            pathPlanningPoint['pos'] = {}      
            pathPlanningPoint['pos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
            pathPlanningPoint['pos']['offsetV'] = ('elevation', 0)
            VIRData['intAndReq']['path-Planning'].append(pathPlanningPoint)

    except Exception as ex:
        print('ex',ex)
        print(ex.__traceback__.tb_lineno) 
        print('VIRData',VIRData)

        return VIRData
    return VIRData




