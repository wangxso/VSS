import math
from V2X.Message import SSM
from .Message  import *
import datetime
import json
import os 

#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)

SSM_msgCount = 0
earth_radius = 6371004  # 地球半径
def OBUGetSSMData(obu_info,ego,participants,traffic_signs_info,obstacles):#obu_info['interface_car',id,type,shape,x,y,z,yaw,pitch,roll,speed]
    # print('000',obu_info)
    # print('111',ego)
    # print('222',participants)
    # print('333',traffic_signs_info)
    # print('444',obstacles)
    # 创建SSM消息帧
    SSMData=MsgFrame.SSM_MsgFrame()
    try:
        configurationpath=Agent_V2X_Dir + '\\' + r'static_configuration.json'
        configurationFile = open(configurationpath,"rb")
        configuration = json.load(configurationFile)
    except FileNotFoundError:
        print("-----static_configuration.json doesn't exist-----")
    try:
        # 拼接SSM数据
        SSMData['id']=str(obu_info[1])  #TODO
        global SSM_msgCount
        SSM_msgCount += 1
        if SSM_msgCount>=127:
            SSM_msgCount = SSM_msgCount -127
        SSMData['msgCnt'] = SSM_msgCount
        SSMData['equipmentType'] = 2
        # if sensor['type'] == 'RSU':          
        #     SSMData['equipmentType'] = 1 
        # if sensor['type'] == 'OBU':          
        #     SSMData['equipmentType'] = 2
        
        SSMData['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
        
        lat = (obu_info[5]) * 180.0 / (math.pi * earth_radius) + 37.788204
        longi = ((obu_info[4]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
        SSMData['sensorPos']['long']=int(10000000 * longi)
        SSMData['sensorPos']['lat']=int(10000000*lat)
        SSMData['sensorPos']['elevation']=int(obu_info[6])
        
        # #创建detectedRegion字段 交通标志牌的信息:[(shape,x,y,z,yaw,pitch,roll)]
        # if len(traffic_signs_info)>0:
        #     for i in range(5):  #
        #         polygonPoint=SSMData['polygon'] 
        #         lat = (traffic_signs_info[0][2]) * 180.0 / (math.pi * earth_radius) + 37.788204  #TODO
        #         longi = ((traffic_signs_info[0][1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
        #         if i == 0:
        #             polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi-1*5400), 'lat':int(10000000 * lat)})
        #         if i == 1:
        #             polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi+1*5400), 'lat':int(10000000 * lat)})
        #         if i == 2:
        #             polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
        #         if i == 3:
        #             polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat-1*5400)})
        #         if i == 4:
        #             polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat+1*5400)})
        #         SSMData['detectedRegion']['polygon'].append(polygonPoint)
        


        #创建participants字段
        msg_participants=[]
        participant_list = []


        #加上主车ego  [ego_x, ego_y, ego_z, ego_yaw, ego_pitch, ego_roll, ego_speed]  
        ego.insert(0,1)   #shape 与participants保持格式一致
        ego.insert(0,0)   #type
        ego.insert(0,0)   #id
        participants.append(ego) #SSM数据包暂时确定包含主车和所有rv
        for item in participants:#[type,x,y,z,yaw,pitch,roll,speed] id,type,shape,x,y,z,yaw,pitch,roll,speed
            participant = {}
            participant['id'] = item[0]
            participant['type'] = item[1]
            participant['shape'] = item[2]
            participant['X'] = item[3]
            participant['Y']= item[4]
            participant['Z'] = item[5]
            participant['Yaw'] = item[6]
            participant['Pitch'] = item[7]
            participant['Roll'] = item[8]
            participant['Speed'] = item[9]
            # if participant['id']!=obu_info[1]:#去掉RV自己 TODO test
            participant_list.append(participant)

            
        id=1
        for v in participant_list: #需要新的数据源  
            dx=obu_info[4]-v['X']
            dy=obu_info[5]-v['Y']
            dz=obu_info[6]-v['Z']
            dis=math.sqrt((dx**2)+(dy**2)+(dz**2))
            if(dis > 200): 
                continue
            p=RSM.RSMParticipantData_DF()
            p['ptcId']=id
            id=id+1
            p['ptcType']=0
            if(v['type']==1):
                p['ptcType']=3
                # print('v[X]',v['X'],v['Y'])

            integer_id = int(v['id'])
            # print('integer_id',integer_id)
            bytes_id= integer_id.to_bytes(8, 'big')
            p['id']=bytes_id
            # p['id']=str.encode(str(v['id']))
            # p['id']='00000'+str(v['id'])
            
            v_lat = (v['Y']) * 180.0 / (math.pi * earth_radius) + 37.788204
            v_longi = ((v['X']) * 180.0 / (math.pi * earth_radius)) / math.cos(v_lat * math.pi / 180.0) + (-122.399498)

            p['pos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * v_longi), 'lat':int(10000000 * v_lat)})
            p['pos']['offsetV']=('elevation', int(v['Z']))
            p['speed']=int(v['Speed']/0.02)
            p['heading']=v['Yaw']
            rsm_yaw =round(v['Yaw']-math.pi/2,4)
            if rsm_yaw<0:
                rsm_yaw = 2*math.pi-math.fabs(rsm_yaw)
            rsm_yaw = math.fabs(rsm_yaw-2*math.pi)  
            rsm_yaw2 = int(round((rsm_yaw*180/3.14)/0.0125)) 
            p['heading']=rsm_yaw2
            if p['heading'] > 359.9875/0.0125:
                p['heading'] = p['heading'] - 359.9875/0.0125
            p['heading'] = int(p['heading'])        
            p['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
            
            msg_participants.append({'ptc':p})
            
        # print('666',msg_participants)
        SSMData['participants']=msg_participants
        
        # 依然由水马进行rte事件的位置标识
        rte_object = [0.0,0.0,0]
        if len(obstacles)>0:
            for obstacle in obstacles:
                if(obstacle[0] == 4):                    
                    rte_object = [obstacle[2],obstacle[1],obstacle[3]]

        #创建rtes字段
        if configuration:
            if configuration["RSU"]["RSI"]["RTE"]!=None:
                RTEData=RSI.RTEData_DF() 
                RTEData['eventType']=configuration["RSU"]["RSI"]["RTE"]["eventType"]
                lat = (rte_object[0]) * 180.0 / (math.pi * earth_radius) + 37.788204
                longi = ((rte_object[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
                RTEData['eventPos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
                RTEData['eventPos']['offsetV'] = ('elevation', 0)
                RTEPathData=RSI.ReferencePath_DF()
                for i in range(5):
                    RTEPoint=RSI.RSIPathPoint_DF()
                    lat = (rte_object[0]) * 180.0 / (math.pi * earth_radius) + 37.788204
                    longi = ((rte_object[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
                    if i == 0:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi-1*5400), 'lat':int(10000000 * lat)})
                    if i == 1:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi+1*5400), 'lat':int(10000000 * lat)})
                    if i == 2:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
                    if i == 3:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat-1*5400)})
                    if i == 4:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat+1*5400)})
                    RTEPathData['activePath'].append(RTEPoint)
                RTEData['referencePaths'].append(RTEPathData)
                RTEData.pop('referenceLinks')
                SSMData['rtes'].append(RTEData)

   
    except Exception as ex:
        print(ex)
        return SSMData
    else:
        # BSMData_json = json.dumps(BSMData)
        # with open('C:\\Users\\15751002165\\Desktop\\BSM_message.txt','w') as FD:
        #     FD.write(BSMData_json)
        return SSMData


def RSUGetSSMData(rsu_info,participants,traffic_signs_info,*obstacles):#[(shape,x,y,z,yaw,pitch,roll,fov,range)]
    # 创建SSM消息帧
    SSMData=MsgFrame.SSM_MsgFrame()
    try:
        configurationpath=Agent_V2X_Dir + '\\' + r'static_configuration.json'
        configurationFile = open(configurationpath,"rb")
        configuration = json.load(configurationFile)
    except FileNotFoundError:
        print("-----static_configuration.json doesn't exist-----")
    try:
        earth_radius = 6371004
        # 拼接SSM数据
        SSMData['id']='10000000' #暂时用此ID
        global SSM_msgCount
        SSM_msgCount += 1
        if SSM_msgCount>=127:
            SSM_msgCount = SSM_msgCount -127
        SSMData['msgCnt'] = SSM_msgCount
        SSMData['equipmentType'] = 1
        # if sensor['type'] == 'RSU':          
        #     SSMData['equipmentType'] = 1 
        # if sensor['type'] == 'OBU':          
        #     SSMData['equipmentType'] = 2

        SSMData['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
        
        lat = (rsu_info[2]) * 180.0 / (math.pi * earth_radius) + 37.788204
        longi = ((rsu_info[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
        SSMData['sensorPos']['long']=10000000 * longi
        SSMData['sensorPos']['lat']=10000000*lat
        SSMData['sensorPos']['elevation']=rsu_info[3]

        #创建detectedRegion字段 交通标志牌的信息:[(shape,x,y,z,yaw,pitch,roll)]
        if len(traffic_signs_info)>0:
            for i in range(5):  #
                polygonPoint=SSMData['polygon'] 
                lat = (traffic_signs_info[2]) * 180.0 / (math.pi * earth_radius) + 37.788204  #TODO
                longi = ((traffic_signs_info[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
            if i == 0:
                polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi-1*5400), 'lat':int(10000000 * lat)})
            if i == 1:
                polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi+1*5400), 'lat':int(10000000 * lat)})
            if i == 2:
                polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
            if i == 3:
                polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat-1*5400)})
            if i == 4:
                polygonPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat+1*5400)})
            SSMData['detectedRegion']['polygon'].append(polygonPoint)



        #创建participants字段
        msg_participants=[]
        participant = {}
        participant_list = []

        for item in participants:
            participant['id'] = str(item[0])
            participant['type'] = item[1]
            participant['shape'] = item[2]
            participant['X'] = item[3]
            participant['Y']= item[4]
            participant['Z'] = item[5]
            participant['Yaw'] = item[6]
            participant['Pitch'] = item[7]
            participant['Roll'] = item[8]
            participant['Speed'] = item[9]
            participant_list.append(participant)

        id=1
        print('participant_list',len(participant_list))
        for v in participant_list: #需要新的数据源  
            dx=rsu_info[1]-v['X']
            dy=rsu_info[2]-v['Y']
            dz=rsu_info[3]-v['Z']
            dis=math.sqrt((dx**2)+(dy**2)+(dz**2))
            if(dis > 200): 
                continue
            p=RSM.RSMParticipantData_DF()
            p['ptcId']=id
            id=id+1
            p['ptcType']=0
            if(v['type']==1):
                p['ptcType']=3
            # p['id']=str(v['id'])
            p['id']=str.encode(str(v['id']))
            
            v_lat = (v['Y']) * 180.0 / (math.pi * earth_radius) + 37.788204
            v_longi = ((v['X']) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
            p['pos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * v_longi), 'lat':int(10000000 * v_lat)})
            p['pos']['offsetV']=('elevation', int(v['Z']))
            p['speed']=int(v['Speed']/0.02)
            p['heading']=v['Yaw']
            rsm_yaw =round(v['Yaw'],4)-math.pi/2
            if rsm_yaw<0:
                rsm_yaw = 2*math.pi-math.fabs(rsm_yaw)
            rsm_yaw = math.fabs(rsm_yaw-2*math.pi)  
            rsm_yaw2 = int(round((rsm_yaw*180/3.14)/0.0125)) 
            p['heading']=rsm_yaw2
            if p['heading'] > 359.9875/0.0125:
                p['heading'] -= 359.9875/0.0125
            p['heading'] = int(p['heading'])        
            p['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
            msg_participants.append({'ptc':p})
            # msg_participants.append(p)
        SSMData['participants']=msg_participants
        
        # 依然由水马进行rte事件的位置标识
        rte_object = [0.0,0.0,0]
        if len(obstacles)>0:
            for obstacle in obstacles:
                if(obstacle[0] == 4):                    
                    rte_object = [obstacle[2],obstacle[1],obstacle[3]]
        #创建rtes字段
        if configuration and len(rte_object)>0:
            if configuration["RSU"]["RSI"]["RTE"]!=None:
                RTEData=RSI.RTEData_DF() 
                RTEData['eventType']=configuration["RSU"]["RSI"]["RTE"]["eventType"]
                lat = (rte_object[0]) * 180.0 / (math.pi * earth_radius) + 37.788204
                longi = ((rte_object[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
                RTEData['eventPos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
                RTEData['eventPos']['offsetV'] = ('elevation', 0)
                RTEPathData=RSI.ReferencePath_DF()
                for i in range(5):
                    RTEPoint=RSI.RSIPathPoint_DF()
                    lat = (rte_object[0]) * 180.0 / (math.pi * earth_radius) + 37.788204
                    longi = ((rte_object[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (-122.399498)
                    if i == 0:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi-1*5400), 'lat':int(10000000 * lat)})
                    if i == 1:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi+1*5400), 'lat':int(10000000 * lat)})
                    if i == 2:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
                    if i == 3:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat-1*5400)})
                    if i == 4:
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat+1*5400)})
                    RTEPathData['activePath'].append(RTEPoint)
                RTEData['referencePaths'].append(RTEPathData)
                RTEData.pop('referenceLinks')
                SSMData['rtes'].append(RTEData)

   
    except Exception as ex:
        print(ex)
        return SSMData
    else:
        # BSMData_json = json.dumps(BSMData)
        # with open('C:\\Users\\15751002165\\Desktop\\BSM_message.txt','w') as FD:
        #     FD.write(BSMData_json)
        return SSMData
