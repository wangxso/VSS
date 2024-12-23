from cmath import sqrt
import math
from .Message  import *
import datetime
import json
import os
#获取文件父目录
Agent_V2X_Dir = os.path.dirname(__file__)

RSI_msgCount = 0
def getRSIData(rsu_info, traffic_signs_info_raw,pathpoints, *obstacles):
    # 创建RSI消息帧
    traffic_signs_info = []  
    RSIData=MsgFrame.RSI_MsgFrame()
    try:
        earth_radius = 6371004
        
        global RSI_msgCount
        RSI_msgCount += 1
        if RSI_msgCount>=127:
            RSI_msgCount = RSI_msgCount -127

        RSIData['msgCnt'] = RSI_msgCount
        RSIData['id']='00000001'  #rsu暂时无ID属性，暂置为1
        RSIData['moy']=int((datetime.datetime.utcnow().timestamp()%60)) 
        
        lat = (rsu_info[3]) * 180.0 / (math.pi * earth_radius) + 39.5427 
        longi = ((rsu_info[2]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)
        RSIData['refPos']['lat']=int(10000000 * lat)
        RSIData['refPos']['long']=int(10000000 * longi)
        RSIData['refPos']['elevation']=int(rsu_info[4])

        if len(traffic_signs_info_raw) <= 16:
            traffic_signs_info = traffic_signs_info_raw
        else:
            traffic_signs_info = traffic_signs_info_raw[0,16]

        
        if(len(traffic_signs_info)>0):         
            for info in traffic_signs_info:
                RSIPathData=RSI.ReferencePath_DF()
                pathponits_temp1 = []
                pathponits_temp2 = []
                if len(pathpoints) == 2:
                    distance = math.sqrt(math.pow(pathpoints[0][0]-pathpoints[1][0],2) + math.pow(pathpoints[0][1]-pathpoints[1][1],2))
                    datle_x = pathpoints[1][0]-pathpoints[0][0]
                    datle_y = pathpoints[1][1]-pathpoints[0][1]
                    if distance <= 100:
                        pathponits_temp1.append(pathpoints[0])
                        for i in range(4):
                            pathponits_temp1.append([pathpoints[0][0] + datle_x*(i+1)/5,pathpoints[0][1] + datle_y*(i+1)/5])
                        pathponits_temp1.append(pathpoints[1])
                    else:
                        pathponits_num1 = int(distance/20)
                        pathponits_temp1.append(pathpoints[0])
                        for i in range(pathponits_num1):
                            pathponits_temp1.append([pathpoints[0][0] + datle_x*(i+1)/(pathponits_num1+1),pathpoints[0][1] + datle_y*(i+1)/(pathponits_num1+1)])
                        pathponits_temp1.append(pathpoints[1])
                else:                  
                    pathponits_temp1 =  pathpoints

                if len(pathponits_temp1) < 32: #保证activePath数量小于32
                    pathponits_temp2 = pathponits_temp1
                else:
                    points_interval= int(len(pathponits_temp1)/10)
                    for i in range(10): #考虑包的大小，留11个点
                        pathponits_temp2.append(pathponits_temp1[points_interval*i])
                    pathponits_temp2.append(pathponits_temp1[-1])

                pathponits_11 = pathponits_temp2
                # print('pathponits_',len(pathponits_11),pathponits_11)

                pathponits_22  = []
                for i in range(len(pathponits_11)):  #traffic_signs_info[[id,delay_time,shape,x,y,z,yaw,pitch,roll]]
                    dx = pathponits_11[i][0] - info[3]
                    dy = pathponits_11[i][1] - info[4]
                    dis = math.sqrt((dx**2)+(dy**2)) 
                    if dis < 3000: 
                        pathponits_22.append(pathponits_11[i])
                # print('pathponits_2200000',len(pathponits_22))

                for i in range(len(pathponits_22)):
                    RSIPoint=RSI.RSIPathPoint_DF()
                    lat1 = (pathponits_22[i][1]) * 180.0 / (math.pi * earth_radius) + 39.5427 
                    longi1 = ((pathponits_22[i][0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat1 * math.pi / 180.0) + (116.2317)
                    RSIPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi1), 'lat':int(10000000 * lat1)})
                    # print('offsetLL',RSIPoint['offsetLL'])
                    RSIPathData['activePath'].append(RSIPoint)
                
                RTSData=RSI.RTSData_DF()  
                RTSData['rtsId'] =  info[0]   

                # RTS标志牌代码
                traffic_signs = {
                    '114':1,  #交叉路口
                    '234':2,  #注意急转弯 向左急转
                    '235':2,  #注意急转弯 向右急转
                    '220':3,  #反向弯路
                    '221':3,  #反向弯路
                    '250':4,  #连续弯路
                    '253':5,  #注意陡坡 上
                    '254':5,  #注意陡坡 下
                    '233':6,  #连续下坡
                    '251':7,  #窄路 两侧变窄
                    '256':7,  #窄路 右侧变窄
                    '257':7,  #窄路 左侧变窄
                    '267':8,  #注意窄桥 
                    '259':9,  #双向交通
                    '260':10,  #注意行人
                    '261':11,  #注意儿童
                    '242':12,  #注意驼峰桥
                    ' ':13,  #注意野生动物***
                    '255':14,  #注意信号灯
                    '212':15,  #注意落石
                    '258':16,  #注意横风
                    '263':17,  #小心路滑 易滑
                    '213':18,  #傍山险路
                    '215':19,  #堤坝路 左
                    '216':19,  #堤坝路 右
                    '249':20,  #村庄
                    '287':21,  #前方隧道
                    '217':22,  #渡口
                    '242':23,  #驼峰桥
                    '248':24,  #路面不平
                    ' ':25,  #路面高突***
                    ' ':26,  #路面低洼***
                    '247':27,  #过水路面
                    '239':28,  #有人看守铁路道口
                    '238':29,  #无人看守铁路道口
                    '240':30,  #叉形符号
                    ' ':31,  #斜杠符号***
                    '218':32,  #注意非机动车
                    '219':33,  #注意残疾人
                    '237':34,  #事故易发路段
                    '252':35,  #慢行
                    '265':36,  #注意障碍物 右
                    '266':36,  #注意障碍物 左 
                    '264':37,  #注意危险
                    '236':38,  #正在施工
                    '232':39,  #建议速度
                    ' ':40,  #隧道开车灯***
                    '214':41,  #注意潮汐车道
                    '268':42,  #注意保持车距
                    '241':43,  #注意分离式道路
                    '35':44,  #注意会车 合流
                    ' ':45,  #避险车道***
                    ' ':46,  #注意路面结冰、注意雨(雪)天、注意雾天、注意不利气象条件 ***
                    ' ':47,  #注意前方车辆排队 ***
                    '46':48,  #停车让行
                    '44':49,  #减速让行
                    '35':50,  #会车让行
                    '50':51,  #禁止通行
                    '45':52,  #禁止驶入
                    '37':53,  #禁止机动车驶入
                    '34':54,  #禁止载货汽车驶入
                    '30':55,  #禁止电动三轮车驶入
                    '31':56,  #禁止大型客车驶入
                    '51':57,  #禁止小型客车驶入
                    '47':58,  #禁止挂车、半挂车驶入
                    '49':59,  #禁止拖拉机驶入
                    '42':60,  #禁止三轮汽车、低速货车驶入
                    '41':61,  #禁止摩托车驶入
                    ' ':62,  #禁止某两种车驶入***
                    '15':63,  #禁止非机动车进入
                    '12':64,  #禁止畜力车进入
                    ' ':65,  #禁止人力客运三轮车进入***
                    '13':66,  #禁止人力货运三轮车进入
                    '14':67,  #禁止人力车进入
                    '52':68,  #禁止行人进入
                    '58':69,  #禁止向左转弯
                    '57':70,  #禁止向右转弯
                    '61':71,  #禁止直行
                    '17':72,  #禁止向左向右转弯
                    '65':73,  #禁止直行和向左转弯
                    '54':74,  #禁止直行和向右转弯
                    '32':75,  #禁止掉头
                    '28':76,  #禁止超车
                    '36':77,  #解除禁止超车
                    '48':78,  #全路段禁止停车
                    '29':79,  #禁止长时停车
                    '40':80,  #禁止鸣笛
                    '38':81,  #限制宽度
                    '33':82,  #限制高度
                    '60':83,  #限制质量
                    '25':84,  #限制轴重
                    '53':85,  #限制车速
                    '55':85,  #限制车速
                    '54':86,  #解除限制速度
                    '26':87,  #停车检査
                    '11':88,  #禁止运输危险物品车辆驶入
                    '27':89,  #海关
                    '19':90,  #区域限制速度
                    '20':91,  #区域限制速度解除
                    '21':92,  #区域禁止长时停车
                    '22':93,  #区域禁止长时停车解除
                    '23':94,  #区域禁止停车
                    '24':95,  #区域禁止停车解除
                    '184':96,  #直行
                    '185':97,  #向左转弯
                    '186':98,  #向右转弯
                    '187':99,  #直行和向左转弯
                    '188':100,  #直行和向右转弯
                    '189':101,  #向左和向右转弯
                    '190':102,  #靠右侧道路行驶
                    '191':103,  #靠左侧道路行驶
                    '192':104,  #立体交叉直行和左转弯行驶
                    '193':105,  #立体交叉直行和右转弯行驶
                    '194':106,  #环岛行驶
                    '195':107,  #单行路（向左或向右）
                    '196':108,  #单行路（直行）
                    '197':109,  #步行
                    '198':110,  #鸣喇叭
                    '199':111,  #最低限速
                    '200':112,  #路口优先通行
                    '201':113,  #会车先行
                    '202':114,  #人行横道
                    '9':115,  #右转车道
                    '3':116,  #左转车道
                    '203':117,  #直行车道
                    '204':118,  #直行和右转合用车道
                    ' ':119,  #直行和左转合用车道***
                    '2':120,  #掉头车道
                    '1':121,  #掉头和左转合用车道
                    '205':122,  #分向行驶车道
                    '206':123,  #公交线路专用车道
                    '207':124,  #机动车行驶
                    '208':125,  #机动车车道
                    '209':126,  #非机动车行驶
                    '210':127,  #非机动车车道
                    '10':128,  #快速公交系统专用车道
                    '4':129,  #多乘员车辆专用车道
                    ' ':130,  #停车位
                    '211':131,  #允许掉头
                    ' ':132,  #四车道及以上公路交叉路口预告
                    ' ':133,  #大交通量的四车道以上公路交叉路口预告
                    ' ':134,  #箭头杆上标识公路编号、道路名称的公路交叉路口预告
                    ' ':135,  #十字交叉路口
                    ' ':136,  #丁字交叉路口
                    '148':137,  #Y型交叉路口
                    ' ':138,  #环形交叉路口
                    '149':139,  #互通式立体交叉
                    '123':140,  #分岔处
                    ' ':141,  #国道编号
                    ' ':142,  #省道编号
                    ' ':143,  #县道编号
                    ' ':144,  #乡道编码
                    ' ':145,  #街道名称
                    '164':146,  #路名牌
                    '141':147,  #地点距离
                    ' ':148,  #地名
                    ' ':149,  #著名地点
                    ' ':150,  #行政区划分界
                    ' ':151,  #道路管理分界
                    ' ':152,  #地点识别
                    '5':153,  #停车场
                    ' ':154,  #错车道
                    '134':155,  #注意人行天桥
                    '166':156,  #人行地下通道
                    '118':157,  #残疾人专用设施
                    '151':158,  #观景台
                    '121':159,  #应急避难设施（场所）
                    ' ':160,  #休息区
                    ' ':161,  #绕行
                    '122':162,  #此路不通
                    '132':163,  #车道数变少
                    '133':163,  #车道数变少
                    '140':164,  #车道数增加
                    '169':165,  #交通监控设备
                    '127':166,  #隧道出口距离预告
                    ' ':167,  #基本单元
                    ' ':168,  #组合使用
                    ' ':169,  #两侧通行
                    '144':170,  #右侧通行
                    '145':171,  #左側通行
                    '124':172,  #入口预告
                    '82':173,  #地点、方向
                    '83':173,  #地点、方向
                    ' ':174,  #编号
                    '116':175,  #命名编号
                    ' ':176,  #路名
                    '146':177,  #地点距离
                    ' ':178,  #城市区域多个出口时的地点距离
                    '74':179,  #下一出口预告
                    ' ':180,  #岀口编号
                    '78':181,  #右侧出口预告
                    ' ':182,  #左侧出口预告
                    '80':183,  #出口标志及出口地点方向
                    '70':184,  #髙速公路起点
                    '71':185,  #终点预告
                    '72':186,  #终点提示
                    '73':187,  #国家髙速公路、省级高速公路终点
                    '103':188,  #道路交通信息
                    '105':189,  #里程牌
                    '104':190,  #百米牌
                    '163':191,  #停车领卡
                    '102':192,  #车距确认
                    ' ':193,  #特殊天气建议速度
                    '91':194,  #紧急电话
                    '92':195,  #电话位置指示
                    '93':195,  #电话位置指示
                    ' ':196,  #救援电话
                    '89':197,  #不设电子不停车收费(ETC)车道的收费站预告及收费站
                    '90':197,  #不设电子不停车收费(ETC)车道的收费站预告及收费站
                    ' ':198,  #设有电子不停车收费(ETC)车道的收费站预告及收费站
                    '155':199,  #ETC车道指示
                    ' ':200,  #计重收费
                    '94':201,  #前方加油站
                    '95':202,  #紧急停车带
                    '96':203,  #服务区预告
                    '97':204,  #停车区预告
                    '98':205,  #停车场预告
                    '99':206,  #停车场
                    '101':207,  #爬坡车道
                    ' ':208,  #超限超载检测站
                    ' ':209,  #设置在指路标志版面中的方向
                    ' ':210,  #设置在指路标志版面外的方向
                    ' ':211,  #旅游区距离
                    '321':212,  #旅游区方向
                    '319':213,  #问讯处
                    '318':214,  #徒步
                    '317':215,  #索道
                    '324':216,  #野营地
                    '320':217,  #营火
                    '322':218,  #游戏场
                    '315':219,  #骑马
                    '310':220,  #钓鱼
                    '311':221,  #高尔夫球
                    '316':222,  #潜水
                    '323':223,  #游泳
                    '313':224,  #划船
                    '309':225,  #冬季游览区
                    '314':226,  #滑雪
                    '312':227,  #滑冰
                    '269':228,  #时间范围
                    '270':228,  #时间范围
                    '279':229,  #除公共汽车外
                    '284':230,  #机动车
                    '281':231,  #货车
                    '282':232,  #货车、抱拉机
                    '289':233,  #私人专属
                    '271':234,  #行驶方向标志 271--278
                    '292':235,  #向前200m
                    '294':236,  #向左100m
                    '296':237,  #向左、向右各50m
                    '295':238,  #向右100m
                    '280':239,  #某区域内
                    ' ':240,  #距离某地200m
                    '285':241,  #长度
                    '293':242,  #前方学校
                    '283':243,  #海关
                    '288':244,  #事故
                    '290':245,  #塌方
                    '286':246,  #教练车行驶路线
                    ' ':247,  #驾驶考试路线  ？有icon确没在csv中找到
                    '291':248,  #校车停集站点
                    '297':249,  #组合辅助

                    '217':60010  #前方桥梁 @大唐
                }
                if str(info[2]) in traffic_signs:
                    RTSData['signType'] = traffic_signs[str(info[2])] 
                else:
                    RTSData['signType'] = 0
                # print('7777777777777777777777',RTSData['signType'])
                if len(RSIPathData['activePath'])>1 and len(RSIPathData['activePath'])< 32:
                    RTSData['referencePaths'].append(RSIPathData)
                else:
                    RTSData.pip('referencePaths')

                speed_limit = 30
                speed_limit2 = [51,48]
                speed_limit3 = [3,0]
                # RTSData['description'] = ('textGB2312',speed_limit.to_bytes(2, byteorder="big", signed=False)) 
                RTSData['description'] = ('textGB2312','30'.encode("gb2312", 'ignore')) 
                # RTSData['description'] = ('textGB2312',speed_limit3[0].to_bytes(1, byteorder="big", signed=False)+speed_limit3[1].to_bytes(1, byteorder="big", signed=False))   


                #ludayong 20211208 当rtss的referenceLinks为空时，将该字段从主包中删除    
                if len(RTSData['referenceLinks']) == 0:  
                        RTSData.pop('referenceLinks')
                        
                RTSData['signPos']['offsetLL']=('position-LatLon', {'lon':RSIData['refPos']['long'], 'lat':RSIData['refPos']['lat']})
                RTSData['signPos']['offsetV'] = ('elevation', 0)
                RSIData['rtss'].append(RTSData)
        
        # 依然由水马进行rte事件的位置标识
        rte_object = [0.0,0.0,0]
        # print('obstacles',obstacles)
        if len(obstacles)>0 and len(obstacles[0])>0:
            for obstacle in obstacles:
                if(obstacle[0][0] == 4):                    
                    rte_object = [obstacle[0][2],obstacle[0][1],obstacle[0][3]]
            
            try:
                configurationpath=Agent_V2X_Dir + '\\' + r'static_configuration.json'
                configurationFile = open(configurationpath,"rb")
                configuration = json.load(configurationFile)
            except FileNotFoundError:
                print("-----static_configuration.json doesn't exist-----")
        
            if configuration:
                if configuration["RSU"]["RSI"]["RTE"]!=None:
                    RTEData=RSI.RTEData_DF() 
                    RTEData['eventType']= 501
                    lat = (rte_object[0]) * 180.0 / (math.pi * earth_radius) + 39.5427 
                    longi = ((rte_object[1]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat * math.pi / 180.0) + (116.2317)
                    RTEData['eventPos']['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi), 'lat':int(10000000 * lat)})
                    RTEData['eventPos']['offsetV'] = ('elevation', 0)
                    RTEPathData=RSI.ReferencePath_DF()

                    pathponits_temp1 = []
                    pathponits_temp2 = []
                    if len(pathpoints) == 2:
                        distance = math.sqrt(math.pow(pathpoints[0][0]-pathpoints[1][0],2) + math.pow(pathpoints[0][1]-pathpoints[1][1],2))
                        datle_x = pathpoints[1][0]-pathpoints[0][0]
                        datle_y = pathpoints[1][1]-pathpoints[0][1]
                        if distance <= 100:
                            pathponits_temp1.append(pathpoints[0])
                            for i in range(4):
                                pathponits_temp1.append([pathpoints[0][0] + datle_x*(i+1)/5,pathpoints[0][1] + datle_y*(i+1)/5])
                            pathponits_temp1.append(pathpoints[1])
                        else:
                            pathponits_num1 = int(distance/20)
                            pathponits_temp1.append(pathpoints[0])
                            for i in range(pathponits_num1):
                                pathponits_temp1.append([pathpoints[0][0] + datle_x*(i+1)/(pathponits_num1+1),pathpoints[0][1] + datle_y*(i+1)/(pathponits_num1+1)])
                            pathponits_temp1.append(pathpoints[1])
                    else:
                        pathponits_temp1 =  pathpoints

                    if len(pathponits_temp1) < 32: #保证activePath数量小于32
                        pathponits_temp2 = pathponits_temp1
                    else:
                        points_interval= int(len(pathponits_temp1)/10)
                        for i in range(10): #考虑包的大小，留11个点
                            pathponits_temp2.append(pathponits_temp1[points_interval*i])
                        pathponits_temp2.append(pathponits_temp1[-1])

                    pathponits_11 = pathponits_temp2
                    # print('pathponits_',len(pathponits_11),pathponits_11)


                    pathponits_22 = []
                    for i in range(len(pathponits_11)):  #traffic_signs_info[[id,delay_time,shape,x,y,z,yaw,pitch,roll]]
                        dx = pathponits_11[i][0] - rte_object[1]
                        dy = pathponits_11[i][1] - rte_object[0]
                        dis = math.sqrt((dx**2)+(dy**2)) 
                        # print('00000',dis)
                        if dis < 3000: 
                            pathponits_22.append(pathponits_11[i])
                    # print('pathponits_3311111',len(pathponits_22))

                    for i in range(len(pathponits_22)):
                        RTEPoint=RSI.RSIPathPoint_DF()
                        lat1 = (pathponits_22[i][1]) * 180.0 / (math.pi * earth_radius) + 39.5427 
                        longi1 = ((pathponits_22[i][0]) * 180.0 / (math.pi * earth_radius)) / math.cos(lat1 * math.pi / 180.0) + (116.2317)
                        RTEPoint['offsetLL']=('position-LatLon', {'lon':int(10000000 * longi1), 'lat':int(10000000 * lat1)})
                        RTEPathData['activePath'].append(RTEPoint)

                    RTEData['referencePaths'].append(RTEPathData)
                    RTEData.pop('referenceLinks')
                    RSIData['rtes'].append(RTEData)

        else:
            RSIData.pop('rtes')
            # pass

        #ludayong 20211117 当rtes为空，将该字段从主包中删除    
        if 'rtes' in RSIData and len(RSIData['rtes']) == 0:  
            RSIData.pop('rtes')

        if 'rtss' in RSIData and len(RSIData['rtss']) == 0:  
            RSIData.pop('rtss')

    except Exception as ex:
        # print('RSIData00',RSIData)
        print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!') 
        print(ex)   
        print(ex.__traceback__.tb_lineno)   
        return RSIData

    if 'rtes' in RSIData and len(RSIData['rtes']) == 0:
            RSIData.pop('rtes')
    return RSIData







