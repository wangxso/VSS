from ...message import MsgFrame
from loguru import logger
import math
import datetime
import json
import os 
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)

BSM_msgCount = 0
earth_radius = 6371004  # 地球半径
def getBSMData(veh_information):#需要新的数据源
    # 创建BSM消息帧
    BSMData=MsgFrame.BSM_MsgFrame()
    try:
        configurationpath=Agent_V2X_Dir + '\\' + r'static_configuration.json'
        configurationFile = open(configurationpath,"rb")
        configuration = json.load(configurationFile)
    except FileNotFoundError:
        logger.info("-----static_configuration.json doesn't exist-----")
    try:
        #EARTH_RADIUS=6371004
        #ORIGIN_LAT=39.5427
        #ORIGIN_ELE=0.0
        #ORIGIN_LON=116.2317
        earth_radius = 6371004
        # 通过节点所有者标识符，获取主车数据
        ego=veh_information  #将主车的信息赋予ego
        # 拼接BSM数据
        BSMData['id']=ego['ID']

        global BSM_msgCount
        BSM_msgCount += 1
        if BSM_msgCount>=127:
            BSM_msgCount = BSM_msgCount -127
        BSMData['msgCnt'] = BSM_msgCount
        
        lat = (ego['Y']) * 180.0 / (math.pi * earth_radius) + 39.5427
        # Longitude is in 1/10 micro degrees in BSM frame - long %
        longi = ((ego['X']) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)
        BSMData['pos']['long']=10000000 * longi
        BSMData['pos']['lat']=10000000*lat
        BSMData['pos']['elevation']=0.0
        BSMData['secMark']=int((datetime.datetime.utcnow().timestamp()%60)*1000)
        BSMData['speed']=round(ego['Speed']/0.02)
        
        bsm_yaw =ego['Yaw'] 
        if bsm_yaw < 0:
            bsm_yaw += 360
        if bsm_yaw> 359.9875:
            bsm_yaw =359.9875 
        BSMData['heading']=round(bsm_yaw/0.0125)

        BSMData['accelSet']['long']= 0.0
        BSMData['accelSet']['lat']= 0.0
        BSMData['accelSet']['vert']=0.0
        BSMData['accelSet']['yaw']=0.0
        BSMData['size']['width']=1.8 * 100 # in unit of 1 cm
        BSMData['size']['length']=5.0 *100 # in unit of 1 cm
        BSMData['size']['height']=1.52 * (100/5) # in unit of 5 cm
        BSMData['vehicleClass']['classification']=61


        light_status_list = []
        if configuration:
            if ego['counter'] != 1:
                for k,v in configuration['HV_1']['Body']['light'].items():
                    if v['Start_time'] < ego['Time']  and ego['Time']  < v['End_time']:
                        light_status_list.append(v['Light_status'])
                    else:
                        light_status_list.append(0)

                lights=[0,0]
                lights[0]=128*light_status_list[0]+64*light_status_list[1]+32*light_status_list[2]+16*light_status_list[3]+8*light_status_list[4]+4*light_status_list[5]+2*light_status_list[6]+light_status_list[7]
                lights[1]=128*light_status_list[8]
                BSMData['safetyExt']['lights'][0]=lights

                temp_json1 = configuration['HV_1']['Body']['Out-of-control_vehicle_condition']
                if temp_json1['brakePadel']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['brakePadel']['End_time']:
                    BSMData['brakes']['brakePadel']=temp_json1['brakePadel']['brakePadel_status']

                if temp_json1['wheelBrakes']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['wheelBrakes']['End_time']:
                    temp_wB=temp_json1['wheelBrakes']['wheelBrakes_status']
                    wheelBrakes=[0]
                    if temp_wB['unavailable'] != 0:
                        wheelBrakes[0] = 0
                        BSMData['brakes']['wheelBrakes'][0] = wheelBrakes
                    else:
                        wheelBrakes[0] = (temp_wB['unavailable']*16+temp_wB['leftFront']*8+temp_wB['leftRear']*4+temp_wB['rightFront']*2+temp_wB['rightRear'])*8
                        BSMData['brakes']['wheelBrakes'][0] = wheelBrakes

                if temp_json1['traction']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['traction']['End_time']:
                    BSMData['brakes']['traction']=temp_json1['traction']['traction_status']

                if temp_json1['abs']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['abs']['End_time']:
                    BSMData['brakes']['abs']=temp_json1['abs']['abs_status']

                if temp_json1['scs']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['scs']['End_time']:
                    BSMData['brakes']['scs']=temp_json1['scs']['scs_status']

                if temp_json1['brakeBoost']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['brakeBoost']['End_time']:
                    BSMData['brakes']['brakeBoost']=temp_json1['brakeBoost']['brakeBoost_status']

                if temp_json1['auxBrakes']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['auxBrakes']['End_time']:
                    BSMData['brakes']['auxBrakes']=temp_json1['auxBrakes']['auxBrakes_status']
                events=[0,0]
                eve = [0,0,0,0,0,0,0,0,0,0,0,0,0] #event在此修改
                events[0]= 128*eve[0]+64*eve[1]+32*eve[2]+16*eve[3]+8*eve[4]+4*eve[5]+2*eve[6]+1*eve[7]
                events[1]= (16*eve[8]+8*eve[9]+4*eve[10]+2*eve[11]+1*eve[12])*8
                BSMData['safetyExt']['events'][0] = events

            else:
                for k,v in configuration['HV_2']['Body']['light'].items():
                    if v['Start_time'] < ego['Time']  and ego['Time']  < v['End_time']:
                        light_status_list.append(v['Light_status'])
                    else:
                        light_status_list.append(0)

                lights=[0,0]
                lights[0]=128*light_status_list[0]+64*light_status_list[1]+32*light_status_list[2]+16*light_status_list[3]+8*light_status_list[4]+4*light_status_list[5]+2*light_status_list[6]+light_status_list[7]
                lights[1]=128*light_status_list[8]
                BSMData['safetyExt']['lights'][0]=lights

                temp_json1 = configuration['HV_2']['Body']['Out-of-control_vehicle_condition']
                if temp_json1['brakePadel']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['brakePadel']['End_time']:
                    BSMData['brakes']['brakePadel']=temp_json1['brakePadel']['brakePadel_status']

                if temp_json1['wheelBrakes']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['wheelBrakes']['End_time']:
                    temp_wB=temp_json1['wheelBrakes']['wheelBrakes_status']
                    wheelBrakes=[0]
                    if temp_wB['unavailable'] != 0:
                        wheelBrakes[0] = 0
                        BSMData['brakes']['wheelBrakes'][0] = wheelBrakes
                    else:
                        wheelBrakes[0] = (temp_wB['unavailable']*16+temp_wB['leftFront']*8+temp_wB['leftRear']*4+temp_wB['rightFront']*2+temp_wB['rightRear'])*8
                        BSMData['brakes']['wheelBrakes'][0] = wheelBrakes

                if temp_json1['traction']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['traction']['End_time']:
                    BSMData['brakes']['traction']=temp_json1['traction']['traction_status']

                if temp_json1['abs']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['abs']['End_time']:
                    BSMData['brakes']['abs']=temp_json1['abs']['abs_status']

                if temp_json1['scs']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['scs']['End_time']:
                    BSMData['brakes']['scs']=temp_json1['scs']['scs_status']

                if temp_json1['brakeBoost']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['brakeBoost']['End_time']:
                    BSMData['brakes']['brakeBoost']=temp_json1['brakeBoost']['brakeBoost_status']

                if temp_json1['auxBrakes']['Start_time'] < ego['Time']  and ego['Time']  < temp_json1['auxBrakes']['End_time']:
                    BSMData['brakes']['auxBrakes']=temp_json1['auxBrakes']['auxBrakes_status']

                events=[0,0]
                eve = [0,0,0,0,0,0,0,0,0,0,0,0,0]
                events[0]=128*eve[0]+64*eve[1]+32*eve[2]+16*eve[3]+8*eve[4]+4*eve[5]+2*eve[6]+1*eve[7]
                events[1]=(16*eve[8]+8*eve[9]+4*eve[10]+2*eve[11]+1*eve[12])*8
                BSMData['safetyExt']['events'][0] = events
        else:
            BSMData.pop('safetyExt')
            BSMData.pop('brakes')
        
    except Exception as ex:
        logger.error(ex)
        return BSMData
    else:
        return BSMData
