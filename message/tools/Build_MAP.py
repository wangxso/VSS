from ...message import MsgFrame
from loguru import logger
import math
import datetime
import json



def getMAPData(self):#需要新的地图数据API
    MAPData=MsgFrame.MAP_MsgFrame()
    try:       
        earth_radius = 6371004     
        edges=self.param['roadNet'].getNeighboringEdges(self.param['movement'][0], self.param['movement'][1], 200)
        # pick the closest edge
        if len(edges) > 0:
            FromNodes={}
            ToNodes={}
            for edge in edges:
                nodeS=edge[0].getFromNode()
                if(nodeS.getID() not in FromNodes):
                    FromNodes[nodeS.getID()]=nodeS
                nodeE=edge[0].getToNode()
                if( nodeE.getID() not in ToNodes):
                    ToNodes[nodeE.getID()]={}
                    ToNodes[nodeE.getID()]['x']=nodeE.getCoord()[0]
                    ToNodes[nodeE.getID()]['y']=nodeE.getCoord()[1]
                    ToNodes[nodeE.getID()]['edges']=[]
                ToNodes[nodeE.getID()]['edges'].append(edge)
        SingleNode=[]
        for nodeKey in FromNodes:
            if nodeKey not in ToNodes:
                SingleNode.append(FromNodes[nodeKey])
        MAPData['nodes']=[]
        for node in SingleNode:
            MapNode=MAP.MapNode_DF()
            MapNode['name']=node.getID()
            MapNode['id']['id']=self.scheduler.getIntID(node.getID())
            MapNode['refPos']={}
            #refPos
            lat = (nodeE.getCoord()[1]) * 180.0 / (math.pi * earth_radius) + 37.788204
            longi = ((nodeE.getCoord()[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
            MapNode['refPos']['lat']=int(10000000 * lat)
            MapNode['refPos']['long']=int(10000000 * longi)
            MapNode['refPos']['elevation']=0
            MAPData['nodes'].append(MapNode)

        for i in ToNodes.keys():
            MapNode=MAP.MapNode_DF()  
            MapNode['name']=i
            MapNode['id']['id']=self.scheduler.getIntID(i)
            MapNode['refPos']={}
            #refPos
            lat = (ToNodes[i]['y']) * 180.0 / (math.pi * earth_radius) + 37.788204
            longi = ((ToNodes[i]['x']) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
            MapNode['refPos']['lat']=int(10000000 * lat)
            MapNode['refPos']['long']=int(10000000 * longi)
            MapNode['refPos']['elevation']=0
            MapNode['inLinks']=[]
            spat_phaseId_count = 0 
            for edge in ToNodes[i]['edges']:
                MapLink=MAP.MapLink_DF()
                MapLink['name']=edge[0].getID()
                MapSpeedLimit=MAP.MapSpeedLimit_DF()
                MapSpeedLimit['type']=5
                MapSpeedLimit['speed']=int((edge[0].getSpeed())/0.02)
                MapLink['speedLimits'].append(MapSpeedLimit)
                for point in edge[0]._shape:
                    MapPoint=MAP.MapPoint_DF()
                    lat = (point[1]) * 180.0 / (math.pi * earth_radius) + 37.788204
                    longi = ((point[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
                    MapPoint['posOffset']['offsetLL']=('position-LatLon', {'lon':int(10000000*longi), 'lat':int(10000000*lat)})
                    MapLink['points'].append(MapPoint)
                Lanes=edge[0].getLanes()
                if(len(Lanes) > 0):
                    MapLink['linkWidth']=int(Lanes[0].getWidth()*100*len(Lanes))
                    MapLink['lanes']=[]
                    MapLink['upstreamNodeId']['id']=self.scheduler.getIntID(edge[0].getFromNode().getID())                     

                for j in range(len(Lanes)):#20220117 去掉非机动车道
                    if Lanes[j]._width<3.0:
                        continue
                        
                    MapLane=MAP.MapLane_DF()
                    MapLane['laneID']= self.scheduler.getIntID(Lanes[j].getID())

                    MapSpeedLimit=MAP.MapSpeedLimit_DF()
                    MapSpeedLimit['type']=5 #'vehicleMaxSpeed'
                    MapSpeedLimit['speed']=int(Lanes[j].getSpeed()/0.02)
                    MapLane['speedLimits'].append(MapSpeedLimit)

                    for point in Lanes[j]._shape:
                        MapPoint=MAP.MapPoint_DF()
                        lat = (point[1]) * 180.0 / (math.pi * earth_radius) + 37.788204
                        longi = ((point[0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
                        MapPoint['posOffset']['offsetLL']=('position-LatLon', {'lon':int(10000000*longi), 'lat':int(10000000*lat)})
                        MapLane['points'].append(MapPoint)

                    connections=Lanes[j].getOutgoing()
                    direction = []
                    AllowedManeuvers = [0,0,0,0,0,0,0,0,0]
                    for item in connections:
                        direction.append(item._direction)
                    direction = list(set(direction))
                    for item in direction:
                        if item=='s':
                            AllowedManeuvers[0] = 1
                        if item=='l':    
                            AllowedManeuvers[1] = 1
                        if item=='r':    
                            AllowedManeuvers[2] = 1
                        if item=='u':    
                            AllowedManeuvers[3] = 1
                    maneuvers=[0,0]
                    maneuvers[0]=128*AllowedManeuvers[0]+64*AllowedManeuvers[1]+32*AllowedManeuvers[2]+16*AllowedManeuvers[3]+8*AllowedManeuvers[4]+4*AllowedManeuvers[5]+2*AllowedManeuvers[6]+AllowedManeuvers[7]
                    maneuvers[1]=128*AllowedManeuvers[8]
                    MapLane['maneuvers'][0]=(maneuvers[0], MapLane['maneuvers'][0][1])
                    
                    for k in range(len(connections)):
                        MapConnection=MAP.MapConnection_DF()
                        toEdge=connections[k].getTo()
                        MapConnection['remoteIntersection']['id']=self.scheduler.getIntID(toEdge.getToNode().getID())
                        toLane=connections[k].getToLane()
                        MapConnection['connectingLane']['lane']=self.scheduler.getIntID(toLane.getID())
                        MapConnection['phaseId']= spat_phaseId_count%4  #k                   
                        MapLane['connectsTo'].append(MapConnection)
                        
                        #ludayong 20211208 当MapLane的connectsTo为空时，将该字段从主包中删除    
                        if len(MapLane['connectsTo'])== 0:  
                                MapLane.pop('connectsTo')
                                    
                        spat_phaseId_count+=1
                        if spat_phaseId_count>=16:
                            spat_phaseId_count -= 16
                        # print('*******',spat_phaseId_count)

                    MapLink['lanes'].append(MapLane)    
                MapNode['inLinks'].append(MapLink)#20211213包太大，无法decode，干掉optional字段
            MAPData['nodes'].append(MapNode)

            if len(MapNode['inLinks'])>=4:
                # pass
                for i in range(len(MapNode['inLinks'])):
                    for item in MapNode['inLinks'][i]['lanes']:
                        if len(item['connectsTo'])>0:
                            for item_connectsTO in item['connectsTo']:
                                self.tempdirt_for_remoteIntersection_id.append(item_connectsTO['remoteIntersection']['id'])                                   
                            
            if len(MapNode['inLinks'])>=4:
                edge_movement_num = int(len(self.tempdirt_for_remoteIntersection_id)/4)
                for i in range(len(MapNode['inLinks'])):    
                    if edge_movement_num == 4:
                        for k in range(edge_movement_num):
                            MapMovement=MAP.MapMovement_DF()
                            MapMovement['remoteIntersection']={}
                            MapMovement['remoteIntersection']['region']=0
                            MapMovement['remoteIntersection']['id']=self.tempdirt_for_remoteIntersection_id[k+(4*i)]
                            if k%4==0:
                                MapMovement['phaseId']=(0+(4*i))
                            if k%4==1:
                                MapMovement['phaseId']=(1+(4*i))
                            if k%4==2:
                                MapMovement['phaseId']=(1+(4*i))
                            if k%4==3:
                                MapMovement['phaseId']=(2+(4*i))
                            MapNode['inLinks'][i]['movements'].append(MapMovement)

                    if edge_movement_num == 5:
                        for k in range(edge_movement_num):
                            MapMovement=MAP.MapMovement_DF()
                            MapMovement['remoteIntersection']={}
                            MapMovement['remoteIntersection']['region']=0
                            MapMovement['remoteIntersection']['id']=self.tempdirt_for_remoteIntersection_id[k+(5*i)]
                            if k%5==0:
                                MapMovement['phaseId']=(0+(4*i))
                            if k%5==1:
                                MapMovement['phaseId']=(1+(4*i))
                            if k%5==2:
                                MapMovement['phaseId']=(1+(4*i))
                            if k%5==3:
                                MapMovement['phaseId']=(1+(4*i))
                            if k%5==4:
                                MapMovement['phaseId']=(2+(4*i))
                            MapNode['inLinks'][i]['movements'].append(MapMovement)

                    if edge_movement_num == 9:
                        for k in range(3):
                            MapMovement=MAP.MapMovement_DF()
                            MapMovement['remoteIntersection']={}
                            MapMovement['remoteIntersection']['region']=0
                            MapMovement['remoteIntersection']['id']=self.tempdirt_for_remoteIntersection_id[3*k+(9*i)]
                            if i%2==0 and k==0 :
                                MapMovement['phaseId']=1
                            if i%2==0 and k==1 :
                                MapMovement['phaseId']=1
                            if i%2==0 and k==2 :
                                MapMovement['phaseId']=2
                            if i%2==1 and k==0 :
                                MapMovement['phaseId']=3
                            if i%2==1 and k==1 :
                                MapMovement['phaseId']=3
                            if i%2==1 and k==2 :
                                MapMovement['phaseId']=4
                            MapNode['inLinks'][i]['movements'].append(MapMovement)
                                
        if len(MAPData['nodes']) >= 10:  
            for i in range(len(MAPData['nodes'])):   
                for j in range(len(MAPData['nodes'][i]['inLinks'])): 
                    MAPData['nodes'][i]['inLinks'][j].pop('movements')

    except Exception as ex:
        print(ex)
        return MAPData
    else:
        # MAPData_json = json.dumps(MAPData)
        # with open('C:\\Users\\15751002165\\Desktop\\MAP_message.txt','w') as FD:
        #     FD.write(MAPData_json)
        self.param['mapFrame']=MAPData
        return self.param['mapFrame']
