from V2X.Message  import *

# id表示World文件TrafficLight标签的自然序号，direction取值为0U1L2S3R，state取值为0R1Y2G（0 1 2 对应 红 黄 绿灯）,timer为剩余时间   id,direction,state,timer
# tirffic_light_ststus{'id':id,'direction':direction,'state':state,'timer':timer}

#十字路口，每个相位用同一id下的交通灯信息表达，如果有direction的方向有缺失，那么：
# 1.有直行信息：右转同直行；左转同直行；掉头也同左转。
# 2.无直行信息：使用默认交通灯时间表，Green:27s,Yellow:3s,Red:30。

#一些规则：
#1.交通灯默认信号按顺序循环，东西向起始状态为绿G，南北向为红R。
#2.北向为道路方向与地图正北方向顺时针夹角最小的方向。



def creat_intersection_phases(now_time,tirffic_light_status_raw,node_id):  # phase['light'] 3红 5绿 8黄
    try:   
        tirffic_light_status = []
        direction = ['R','S','L','U']  #['U','L','S','R']
        light_0_27 =  [5,5,5,5, 3,3,3,3, 5,5,5,5, 3,3,3,3]  #默认交通灯时间表
        light_27_30 = [8,8,8,8, 3,3,3,3, 8,8,8,8, 3,3,3,3]
        light_30_33 = [3,3,3,3, 8,8,8,8, 3,3,3,3, 8,8,8,8]
        light_33_60 = [3,3,3,3, 5,5,5,5, 3,3,3,3, 5,5,5,5]
        # print('+++++++++++++++++++++++++++++++++++++++',len(tirffic_light_status_raw),tirffic_light_status_raw)
        if len(tirffic_light_status_raw) == 0 :# or len(tirffic_light_status_raw) == 1: #tirffic_light_status_raw = [[]]  time@i,64@[,id@i,direction@b,state@b,timer@i
            for i in range(16):
                if 0<=now_time<2700:   
                    tirffic_light_status.append({'id':i+1,'direction':direction[i%4],'state':light_0_27[i],'timer':270-now_time/10})   
                if 2700<=now_time<3000:   
                    tirffic_light_status.append({'id':i+1,'direction':direction[i%4],'state':light_27_30[i],'timer':300-now_time/10})
                if 3000<=now_time<3300:   
                    tirffic_light_status.append({'id':i+1,'direction':direction[i%4],'state':light_30_33[i],'timer':600-now_time/10})
                if 3300<=now_time<6000:   
                    tirffic_light_status.append({'id':i+1,'direction':direction[i%4],'state':light_33_60[i],'timer':600-now_time/10})
                    
        # elif len(tirffic_light_status_raw) == 4:
        #     for i in range(16):   # 0-3 4-7 8-11 12-15 交通灯的颜色一致
        #         tirffic_light_status.append({'id':i+1,'direction':direction[i%4],'state':tirffic_light_status_raw[int(i/4)][2],'timer':tirffic_light_status_raw[int(i/4)][3]})
        # elif len(tirffic_light_status_raw) == 12: #基于PanoCity的情况,每个交通灯有3个灯态 右转 直行 左转
        #     tirffic_light_status_raw.insert(3,tirffic_light_status_raw[2])
        #     tirffic_light_status_raw.insert(7,tirffic_light_status_raw[6])
        #     tirffic_light_status_raw.insert(11,tirffic_light_status_raw[10])
        #     tirffic_light_status_raw.insert(15,tirffic_light_status_raw[14]) #补齐U(掉头),与左转一致
        #     for i in range(16):
        #         tirffic_light_status.append({'id':i+1,'direction':direction[i%4],'state':tirffic_light_status_raw[i][2],'timer':tirffic_light_status_raw[i][3]})          
        # elif len(tirffic_light_status_raw) == 16:
        #     for i in range(16):
        #         tirffic_light_status.append({'id':i+1,'direction':direction[i%4],'state':tirffic_light_status_raw[i][2],'timer':tirffic_light_status_raw[i][3]})        
        else:
            # pass
            for i in range(len(tirffic_light_status_raw)):
                tirffic_light_status.append({'id':tirffic_light_status_raw[i][1],'direction':direction[i%4],'state':tirffic_light_status_raw[i][2],'timer':tirffic_light_status_raw[i][3]}) 
                
            #还是根据id确定属于那盏交通灯，保证每个交通灯的信息填满四个相位

            
        #这里还有好多情况，例如用户配置了主车方向上的交通的某几个方向而并未配置其他同路口的交通灯的时间表  
        #最好是做一张16相位表，默认为len(tirffic_light_status_raw) == 0时的情况，其他情况，有多少用户确定的信息，替换掉多少信息
        
        intersection=SPAT.SPATIntersectionState_DF()
        if node_id.isdigit():
            intersection['intersectionId']['id'] = int(node_id)%65535
        else:
            intersection['intersectionId']['id'] = 55555  #int(node_id[-1])
        
        #不管实际交通灯的配置情况如何（是否把0U1L2S3R四个方向都配齐），对于十字路口，配齐16个相位1~16,4个一组
        
        if len(tirffic_light_status) == 16:
            for i in range(16): #tirffic_light_status的长度必须保证为16，在进入creat_intersection_phases函数前必须补全                        
                phases=SPAT.SPATPhase_DF()   
                phases['id']=tirffic_light_status[i]['id']         

                for j in range(3):
                    phase=SPAT.SPATPhaseState_DF()                          
                    phase['light'] = tirffic_light_status[i]['state'][j]   #0->3 1->8 2->5
                    counting={}
                    counting['startTime']=int(tirffic_light_status[i]['timer'][j][0]*10)
                    counting['likelyEndTime']=int(tirffic_light_status[i]['timer'][j][1]*10)
                    phase['timing']=('counting', counting)
                    phases['phaseStates'].append(phase)
                
                intersection['phases'].append(phases) 
        else:
            for i in range(len(tirffic_light_status)):
                phases=SPAT.SPATPhase_DF()   
                phases['id']=tirffic_light_status[i]['id']        

                for j in range(3):
                    phase=SPAT.SPATPhaseState_DF()                          
                    phase['light'] = tirffic_light_status[i]['state'][j]   #0->3 1->8 2->5
                    counting={}
                    counting['startTime']=int(tirffic_light_status[i]['timer'][j][0]*10)
                    counting['likelyEndTime']=int(tirffic_light_status[i]['timer'][j][1]*10)
                    phase['timing']=('counting', counting)
                    phases['phaseStates'].append(phase)
                
                intersection['phases'].append(phases) 
         
     
    except Exception as ex:
        print('~~~~~~~~~~~~~~~~~~~~~~~',ex)
        print(ex.__traceback__.tb_lineno) 
        return intersection

    return intersection
