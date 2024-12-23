def VIR_DF():
    df = {}

    df['msgCnt'] = 0
    #df['id'] = b'00000000'
    df['id'] = '00000000'

    df['secMark'] = 0

    df['refPos'] = {}
    #pos
    df['refPos']['lat'] = 0
    df['refPos']['long'] = 0
    df['refPos']['elevation'] = 0 #optioinal  -- vehicle real position relates to secMark
    
    df['intAndReq'] = {}# optioinal
    df['intAndReq']['currentPos'] = {} #当前点
    # df['intAndReq']['path-Planning'] = []  #计划轨迹点集   考虑 8s 规划, 1s 用 10 个点表示，共需 80 个点。预留到 100 个
    df['intAndReq']['currentBehavior'] = [[0,0], 14] 
    df['intAndReq']['reqs'] = []

    return df

def reqs():# optioinal
    df = {}
    df['reqID'] = '0' 
    df['status'] = 1
    df['reqPriority'] = '1'  #Value from B00000000 to B11100000 represents the lowest to the highest level  0b00110000 
    df['targetVeh'] = '00000002'
    df['targetRSU'] = '00001001'
    df['info'] = {} #组包时提供所有选项
    df['lifeTime'] = 5555 
    return df

def pathPlanningPoint():# optioinal
    df = {}    
    df['posInMap'] = {}
    df['posInMap'] ['upstreamNodeId']=0
    df['posInMap'] ['downstreamNodeId']=0
    df['posInMap'] ['referenceLanes']=[[0,0], 16]
    
    df['pos'] = {}
    df['pos']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    df['pos']['offsetV'] =('elevation', 0)
    
    df['posAccuracy'] = {}  
    df['speed'] = 0.0 
    df['speedCfd'] = {} 
    df['heading'] = 0.0 
    df['headingCfd'] ={} 
    
    df['accelSet'] = {}
    df['accelSet']['long']  = 0.0
    df['accelSet']['lat']  = 0.0
    df['accelSet']['vert']  = 0.0
    df['accelSet']['yaw']  = 0.0
    
    df['acc4WayConfidence'] = {} 
    df['estimatedTime'] = 10 #Units of of 10 mSec,
    df['timeConfidence'] = {}    
    return df



def PrepareForCode(vir):
    import copy
    codetobe=copy.deepcopy(vir)
    
    codetobe['id']=str.encode(vir['id'])
    if(len(codetobe['id'])>8):
        codetobe['id']=codetobe['id'][0:7]
    else:
        while(len(codetobe['id'])<8):
            codetobe['id']=codetobe['id']+b'\x00'

    codetobe['secMark']=round(vir['secMark']*1000)

    codetobe['pos']['lat']=round(vir['pos']['lat'])
    codetobe['pos']['long']=round(vir['pos']['long'])
    codetobe['pos']['elevation']=round(vir['pos']['elevation'])



    return codetobe

    
if __name__=='__main__':

    import os
    import asn1tools

    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper', numeric_enums=True)

    import json
    bsmPath=dir+'\\bsm.json'  #???????????来自哪
    bsmData=json.load(open(bsmPath,'r'))
    #bsmData=BSM_DF()

    bsmEncoded=ltevCoder.encode('BasicSafetyMessage', PrepareForCode(bsmData))
    print(bsmEncoded)
    bsmDecoded=ltevCoder.decode('BasicSafetyMessage', bsmEncoded)
    print('finish')