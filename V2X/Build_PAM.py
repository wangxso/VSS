import math
from .Message  import *
import datetime
import json
import os
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)


def getPAMData(participants,object,scenario,slots_number=60,building_Layer_Num=1): #可由场景获取的信息可作为形参
    # 创建PAM消息帧
    PAM_msgCount = 0
    PAMData=MsgFrame.PAM_MsgFrame()
    try:
        earth_radius = 6371004
        PAM_msgCount += 1
        if PAM_msgCount>=127:
            PAM_msgCount = PAM_msgCount -127

        PAMData['msgCnt'] = PAM_msgCount
        PAMData['timeStamp']=int((datetime.datetime.utcnow().timestamp()%60))

        PAMData['parkingLotInfo'] = {}
        #停车场信息
        PAMData['parkingLotInfo']['id'] = 1 # Unique id of this parking lot
        PAMData['parkingLotInfo']['name'] = 'Pano_Park01'
        PAMData['parkingLotInfo']['number'] = slots_number  # Total number of parking slots
        PAMData['parkingLotInfo']['buildingLayerNum'] = building_Layer_Num 
        PAMData['parkingLotInfo']['avpType'] = 4


        PAMData['pamNodes'] = []
        
        pamNodes=[]
        junctions = getJunctionList()
        print('////',len(junctions),junctions)
        for junction in junctions:
            if 1: #判断junction是否为停车场内部junction？？？TODO
                pamNodes.append(junction)
                
        
        for pamNode in pamNodes:
            PamNode=PAM.PAMNode_DF()
            
            PamNode['id']= 256  #INTEGER (0..65535)
            # -- The values zero through 255 are allocated for testing purposes 
            # -- Note that the value assigned to a node will be 
            # -- unique within a parking area

            PamNode['refPos']={}
            #refPos
            node_shape = getJunctionShape(pamNode)
            total_x = 0.0
            total_y = 0.0
            for item in node_shape:
                total_x = total_x+item[0]
                total_y = total_y+item[1]
            avg_x = total_x/len(node_shape)
            avg_y = total_y/len(node_shape)
            lat = (avg_y) * 180.0 / (math.pi * earth_radius) + 39.5427
            longi = ((avg_x) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)
            PamNode['refPos']['lat']=int(10000000 * lat)
            PamNode['refPos']['long']=int(10000000 * longi)
            PamNode['refPos']['elevation']=0

            PamNode['floor'] = 1 #判断该Node位于那一层？？？TODO
            
            # PAMData['attributes'] = ([0],8)
            PAM_attr=[0]
            attr = [0,0,0,0, 0,0,0,0]
            PAM_attr[0]=128*attr[0]+64*attr[1]+32*attr[2]+16*attr[3]+8*attr[4]+4*attr[5]+2*attr[6]+1*attr[7]
            PamNode['attributes'][0] = (bytes(PAM_attr),8) # PAM_attr  
            # PAMNodeAttributes ::= BIT STRING {
            # 	entrance(0),
            # 	exit(1),
            # 	toUpstair(2),
            # 	toDownstair(3),
            # 	etc(4),
            # 	mtc(5),
            # 	passAfterPayment(6),
            # 	blocked(7)
            # } (SIZE(8,...))
            
            #PamNode['inDrives'] = [] #-- all the links enter this Node
            
            edge_names=[]
            edge_names_all=[]
            
            lanes = getIncomingLanes(pamNode)
            print('222222',lanes)        
            for v in range(len(lanes)):
                edge_name = getEdgeByLane(lanes[v])
                edge_names_all.append(edge_name)
                if edge_name in edge_names:
                    pass
                else:    
                    edge_names.append(edge_name)

            for i in range(len(edge_names)): 
                InDrives = PAM.PAMDrive_DF()
                edge_lanes = getEdgeLanes(edge_names[i])
                Lanes=edge_lanes
                upstreamPAMNodeId = getFromJunction(Lanes[-1]) 
                if 'cluster_'  in upstreamPAMNodeId:
                    InDrives['upstreamPAMNodeId']=int(upstreamPAMNodeId[7:-1].split('_')[1])
                else:
                    array =[]
                    array_ =[]                   
                    for item in upstreamPAMNodeId:
                        array.append(item)
                    for s in array:
                        if s.isdigit():
                            array_.append(int(s))
                    print('array_',array_,upstreamPAMNodeId.split())
                    lastdigit = array_.pop() 
                    InDrives['upstreamPAMNodeId']=lastdigit 
                InDrives['upstreamPAMNodeId']= int(InDrives['upstreamPAMNodeId']%65535) #NTEGER (0..65535) OPTIONAL
                
                InDrives['driveID']= InDrives['upstreamPAMNodeId']*10 + i  #NTEGER (0..255) OPTIONAL 暂定为upstreamPAMNodeId*10+i TODO 规范数字化各类ID：upstreamPAMNodeId、driveID等
                #-- local id of this drive with same upsttramPAMNode and PAMNode 
                InDrives['twowaySepration']= False  #BOOLEAN  道路是否被分割为不同的两个运动方向  TODO 
                InDrives['speedLimit'] = int(10/0.05)
                InDrives['heightRestriction'] = 3.8/0.1
                InDrives['driveWidth'] = 3.5/0.01
                InDrives['laneNum'] = len(Lanes)
                
                link_points = []               
                for lane_ in Lanes:
                    laneShape_ = getLaneShape(lane_)
                    if len(laneShape_)>28: #剔除掉过多的道路形状点
                        laneShape_step = []
                        step = int(len(laneShape_)/10)
                        laneShape_step.append(laneShape_[0])
                        for n in range(10):  #points 的数量范围 2~31 考虑到包的大小,取12个点
                            laneShape_step.append(laneShape_[1+ step*n])
                        laneShape_step.append(laneShape_[-1])
                        link_points.append(laneShape_step)
                    else:
                        link_points.append(laneShape_)
                
                edgePoints_ = []        
                for ik in range(len(link_points[0])):   #将各lane的形状点集处理成edge的形状点集
                    temp_point_x = 0
                    temp_point_y = 0
                    for j in range(len(Lanes)):  
                        temp_point_x += link_points[j][ik][0]
                        temp_point_y += link_points[j][ik][1]                       
                    edgePoints_.append((temp_point_x/len(Lanes),temp_point_y/len(Lanes)))   
                # print('777777777777777-+-------------------------------++',link_points,len(link_points),edgePoints_)        
                for point in edgePoints_:
                    MapPoint=MAP.MapPoint_DF()
                    lat = (point[1]) * 180.0 / (math.pi * earth_radius) + 39.5427
                    longi = ((point[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)
                    MapPoint['posOffset']['offsetLL']=('position-LatLon', {'lon':int(10000000*longi), 'lat':int(10000000*lat)})
                    InDrives['points'].append(MapPoint)
                
                PAMMovementList = []
                for j in range(len(Lanes)):
                    connections= getValidDirections(Lanes[j])
                    for k in range(len(connections)): #:开头的是junction的内部lane，不可以用内部lane调用getToJunction函数                        
                        toLanes=getNextLanes(Lanes[j], connections[k])
                        tolane = []
                        for item in toLanes:
                            if item[0] != ':':
                                tolane.append(item)
                        if '_' in getToJunction(tolane[0]):
                            PAMMovemen_NodeID =  int(getToJunction(tolane[0])[8:-1].split('_')[0].translate({ ord("0"): None })) 
                        else:
                            PAMMovemen_NodeID =  int(getToJunction(tolane[0])[-1])
                        PAMMovementList.append(PAMMovemen_NodeID)

                list_movement = sorted(set(PAMMovementList),key=PAMMovementList.index)     
                
                InDrives['movements'] = list_movement #-- Define movements at intersection     SEQUENCE (SIZE(1..32)) OF PAMNodeID
                InDrives['parkingSlots'] = [] #-- Information of parking places of this drive   ？？？TODO         
                
                PamNode['inDrives'].append(InDrives)
                
            PAMData['pamNodes'].append(PamNode)
        
        for n in range(len(vehicles)):   
            ParkingGuide = PAM.ParkingGuide_DF()
            ParkingGuide['vehId'] = 'Pano_0' # OCTET STRING (SIZE(8)),
        
            ParkingGuide['drivePath'] = [] # SEQUENCE (SIZE(1..32)) OF PAMNodeID
                # -- the planned path for this vehicle
                # -- represented by a series of PAMNode id
                # -- in order from origin to destination
                            
            ParkingGuide['targetParkingSlot'] = 0  #  INTEGER (0..65535) OPTIONAL,
            # -- if the vehicle is looking for a parking slot,
            # -- then here is the recommended parking slot id,
            # -- which should be by the last drive road in above drivePath.
            # -- if a targetParkingSlot is not included in a ParkingGuide,
            # -- then probably the vehicle is going to the last PAMNode
            # -- whatever type the PAMNode is.`

            PAMData['parkingAreaGuidance'].append(ParkingGuide) 
            # -- parking area path guidance for individual vehicles
		    # -- are list here.

    except Exception as ex:
        print('ex',ex)
        return PAMData
    return PAMData




