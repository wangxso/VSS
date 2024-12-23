from itertools import groupby
import math
# from Message  import *
from V2X.Message  import *
import datetime
import json
# import trafficlight_phases
import V2X.trafficlight_phases



SPAT_msgCount = 0
def getSPATData(ego_time,SPAT_msg):
    tirffic_light_status_with_node = {}
    node_id_list = []
    nowtime = ego_time/1000  #单位 s
    trafficlight_color_num = {'R':3,'G':5,'Y':8}#3红 5绿 8黄
    for k, v in SPAT_msg.items():
        node_id_list.append(k)
        tirffic_light_status_all= []
        for k1,v1 in v.items():
            for i in range(4):
                if len(v1[2][i]) > 1:                                                                
                    v11 = [''.join(list(g)) for k, g in groupby(v1[2][i], key=lambda x: x.isdigit())]
                    if len(v11) == 8:
                        period = int(v11[1]) + int(v11[3]) + int(v11[5]) + int(v11[7])  #交通灯周期
                        period_ = [int(v11[1]),int(v11[1]) + int(v11[3]) ,int(v11[1]) + int(v11[3]) + int(v11[5]),period]
                        timer0 = nowtime % period

                        # if timer0 >= 0 and timer0 < period_[0]:
                        #     timer = period_[0] - timer0
                        #     colour = trafficlight_color_num[v11[0]]
                        # elif timer0 >= period_[0] and timer0 < period_[1]:
                        #     timer = period_[1] - timer0
                        #     colour = trafficlight_color_num[v11[2]]
                        # elif timer0 >= period_[1] and timer0 < period_[2]:
                        #     timer = period_[2] - timer0
                        #     colour = trafficlight_color_num[v11[4]]
                        # elif timer0 >= period_[2] and timer0 < period_[3]:
                        #     timer = period_[3] - timer0 + int(v11[1])
                        #     colour = trafficlight_color_num[v11[6]]
#3红 5绿 8黄                                       #R60 G43 Y3 R14                                     #G 43, Y 3, R 14, G 60
                        if timer0 >= 0 and timer0 < period_[0]:
                            colour = [trafficlight_color_num[v11[0]],trafficlight_color_num[v11[2]],trafficlight_color_num[v11[4]]]
                            timer = [[0,period_[0] - timer0],[period_[0]-timer0, period_[0]-timer0+int(v11[3])],[period_[0]-timer0+int(v11[3]),period_[0]-timer0+int(v11[3])+int(v11[5])]]

                        elif timer0 >= period_[0] and timer0 < period_[1]:
                            colour = [trafficlight_color_num[v11[0]],trafficlight_color_num[v11[2]],trafficlight_color_num[v11[4]]]
                            timer = [[period_[1] - timer0+int(v11[5]),period_[1] - timer0+int(v11[5])+int(v11[7])+int(v11[1])],[0, period_[1] - timer0],[period_[1] - timer0,period_[1] - timer0+int(v11[5])]]

                        elif timer0 >= period_[1] and timer0 < period_[2]:
                            colour = [trafficlight_color_num[v11[0]],trafficlight_color_num[v11[2]],trafficlight_color_num[v11[4]]]
                            timer = [[period_[2] - timer0,period_[2] - timer0+int(v11[7])+int(v11[1])],[period_[2] - timer0+int(v11[7])+int(v11[1]), period_[2] - timer0+int(v11[7])+int(v11[1])+int(v11[3])],[0, period_[2] - timer0]]

                        elif timer0 >= period_[2] and timer0 < period_[3]:
                            colour = [trafficlight_color_num[v11[0]],trafficlight_color_num[v11[2]],trafficlight_color_num[v11[4]]]
                            timer = [[0,period_[3] - timer0+int(v11[1])],[period_[3] - timer0+int(v11[1]), period_[3] - timer0+int(v11[1])+int(v11[3])],[period_[3] - timer0+int(v11[1])+int(v11[3]), period_[3] - timer0+int(v11[1])+int(v11[3])+int(v11[5])]]

                        tirffic_light_status = [0, v1[1][i], colour, timer]
                        tirffic_light_status_all.append(tirffic_light_status)

                    if len(v11) == 6:
                        period = int(v11[1]) + int(v11[3]) + int(v11[5])  # 交通灯周期   G 43  Y 3  R 74 
                        period_ = [int(v11[1]), int(v11[1]) + int(v11[3]), period]
                        timer0 = nowtime % period
                        if timer0 >= 0 and timer0 < period_[0]:
                            colour = [trafficlight_color_num[v11[0]],trafficlight_color_num[v11[2]],trafficlight_color_num[v11[4]]]
                            timer = [[0,period_[0] - timer0],[period_[0]-timer0, period_[0]-timer0+int(v11[3])],[period_[0]-timer0+int(v11[3]),period_[0]-timer0+int(v11[3])+int(v11[5])]]
                        elif timer0 >= period_[0] and timer0 < period_[1]:
                            colour = [trafficlight_color_num[v11[0]],trafficlight_color_num[v11[2]],trafficlight_color_num[v11[4]]]
                            timer = [[period_[1] - timer0+int(v11[5]),period_[1] - timer0+int(v11[5])+int(v11[1])],[0,period_[1] - timer0],[period_[1] - timer0,period_[1] - timer0+int(v11[5])]]
                        elif timer0 >= period_[1] and timer0 < period_[2]:
                            colour = [trafficlight_color_num[v11[0]],trafficlight_color_num[v11[2]],trafficlight_color_num[v11[4]]]
                            timer = [[period_[2] - timer0,period_[2] - timer0+int(v11[1])],[period_[2] - timer0+int(v11[1]),period_[2] - timer0+int(v11[1])+int(v11[3])],[0,period_[2] - timer0]]
                        tirffic_light_status = [0, v1[1][i], colour, timer]
                        tirffic_light_status_all.append(tirffic_light_status)
                    # print(v11)
        tirffic_light_status_with_node[k] = tirffic_light_status_all

        # print('node_id_list',node_id_list)
        # print('tirffic_light_status_all',tirffic_light_status_all)
        # print('tirffic_light_status_all',len(tirffic_light_status_all))
        # print('tirffic_light_status_with_node',tirffic_light_status_with_node)
        # print('len_tirffic_light_status_with_node',len(tirffic_light_status_with_node))
        # print('ego_time',ego_time)
    # 创建SPAT消息帧
    SPATData=MsgFrame.SPAT_MsgFrame()
    try:      
        global SPAT_msgCount
        SPAT_msgCount += 1
        if SPAT_msgCount>=127:
            SPAT_msgCount = SPAT_msgCount -127
        SPATData['msgCnt'] = SPAT_msgCount
        SPATData['name']='trafficlight01'
        SPATData['timeStamp']=int((datetime.datetime.utcnow().timestamp()%60))

        now_time = int(ego_time/100) % 600

        for k,v in tirffic_light_status_with_node.items():
            node_id = k
            tirffic_light_status_raw = v
            intersections = V2X.trafficlight_phases.creat_intersection_phases(now_time,tirffic_light_status_raw,node_id)
            # print('intersections@@@@@@@@@@@@@@@@@@@@@@@@@',intersections)
            # SPATData['intersections'].append(V2X.trafficlight_phases.creat_intersection_phases(now_time)) 
            SPATData['intersections'].append(intersections) 



    except Exception as ex:
        print('@@@@@@@@@@@@@@@@@@@@@@@@@',ex)
        print(ex.__traceback__.tb_lineno) 
        return SPATData

    # SPATData_json = json.dumps(SPATData)
    # with open('C:\\Users\\15751002165\\Desktop\\SPAT_message.txt','w') as FD:
    #     FD.write(SPATData_json)
    return SPATData
