# BSM数据帧
def SSM_DF():
    df = {}

    df['msgCnt'] = 0
    df['id'] = '00000000'
    df['equipmentType'] = 1
    df['secMark'] = 0
    df['sensorPos'] = {}

    #pos
    df['sensorPos']['lat'] = 0
    df['sensorPos']['long'] = 0
    df['sensorPos']['elevation'] = 0 #optioinal

    # df['detectedRegion'] = {} #TODO  
    # df['detectedRegion']['polygon'] = []#optioinal
    # # df['polygon'] = {}
    # df['polygon']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    # df['polygon']['offsetV']= ('elevation', 0)

    
    df['participants'] = [] #optioinal

    # df['obstacles'] = [] #optioinal

    df['rtes'] = [] #optioinal

    return df


def RTEData_DF():
    df={}
    df['rteId']=0
    df['eventType']=0
    df['eventSource']=0

    df['eventPos']={} #optioinal
    #signPos
    df['eventPos']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    df['eventPos']['offsetV'] = ('elevation', 0)

    df['eventRadius']=1000

    df['timeDetails']={} #optioinal
    #timeDetails
    df['timeDetails']['startTime']=0
    df['timeDetails']['endTime']=100
    df['timeDetails']['endTimeConfidence']=0

    df['referencePaths']=[] #optioinal
    df['referenceLinks']=[] #optioinal
    df['eventConfidence']=0 #optioinal
    return df

def SSMParticipantData_DF():
    df = {}

    df['ptcType'] = 0 #unknown
    df['ptcId'] = 0
    df['source'] = 0 #unknown
    df['id'] = bytes([0,0,0,0,0,0,0,0]) #'00000000' #optioinal
    df['plateNo'] = '0000' #optioinal
    df['secMark'] = 0

    df['pos'] = {}
    #posOffset
    df['pos']['offsetLL'] = ('position-LatLon', {'lon':0, 'lat':0})
    df['pos']['offsetV'] = ('elevation', 0)

    df['posConfidence'] = {}
    #accuracy
    df['posConfidence']['pos'] = 0 # 'unavailable'
    df['posConfidence']['elevation'] = 0 #'unavailable' optioinal 

    df['transmission'] = 7 #'unavailable' 挡位
    df['speed'] = 0
    df['heading'] = 0
    df['angle'] = 0 #optioinal
    df['motionCfd'] = {} #optioinal
    #motionCfd
    df['motionCfd']['speedCfd'] = 0  #'unavailable' optioinal
    df['motionCfd']['headingCfd'] = 0  #'unavailable' optioinal
    df['motionCfd']['steerCfd'] = 0  #'unavailable' optioinal

    df['accelSet'] = {} #optioinal
    #accelSet
    df['accelSet']['long'] = 0
    df['accelSet']['lat'] = 0
    df['accelSet']['vert'] = 0
    df['accelSet']['yaw'] = 0

    df['size'] = {}
    #size
    df['size']['width'] = 180
    df['size']['length'] = 500
    df['size']['height'] = 30 #optioinal

    df['vehicleClass'] = {} #optioinal
    #vheicleClass
    df['vehicleClass']['classification'] = 0
    df['vehicleClass']['fuelType'] = 0 #optioinal
    return df

def PrepareForCode(ssm):
    import copy
    codetobe=copy.deepcopy(ssm)
    
    codetobe['id']=str.encode(ssm['id'])
    if(len(codetobe['id'])>8):
        codetobe['id']=codetobe['id'][0:7]
    else:
        while(len(codetobe['id'])<8):
            codetobe['id']=codetobe['id']+b'\x00'
    # for participant in codetobe['participants']:       
    #     participant['id']=str.encode(participant['id'])
    return codetobe

    
if __name__=='__main__':


    import os
    import asn1tools

    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper',
    #cache_dir=dir+'\\code',
    numeric_enums=True)

    import json
    bsmPath=dir+'\\bsm.json'
    bsmData=json.load(open(bsmPath,'r'))
    #bsmData=BSM_DF()

    bsmEncoded=ltevCoder.encode('BasicSafetyMessage', PrepareForCode(bsmData))
    print(bsmEncoded)
    bsmDecoded=ltevCoder.decode('BasicSafetyMessage', bsmEncoded)
    print('finish')