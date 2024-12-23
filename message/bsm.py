# BSM数据帧
def BSM_DF():
    df = {}

    df['msgCnt'] = 0
    df['id'] = '00000000'
    df['plateNo'] = '0000' #optioinal
    df['secMark'] = 0
    df['pos'] = {}

    #pos
    df['pos']['lat'] = 0
    df['pos']['long'] = 0
    df['pos']['elevation'] = 0 #optioinal

    df['posAccuracy'] = {}
    #accuracy
    df['posAccuracy']['semiMajor'] = 255 # 'unavailable'
    df['posAccuracy']['semiMinor'] = 255 #'unavailable' optioinal 
    df['posAccuracy']['orientation'] = 65535 #'unavailable' optioinal 

    df['posConfidence'] = {}
    #accuracy
    df['posConfidence']['pos'] = int(0) # 'unavailable'
    df['posConfidence']['elevation'] = int(0) #'unavailable' optioinal 

    df['transmission'] = 1 #'unavailable' 挡位
    df['speed'] = 0
    df['heading'] = 0
    df['angle'] = 0 #optioinal
    df['motionCfd'] = {} #optioinal
    #motionCfd
    df['motionCfd']['speedCfd'] = 0  #'unavailable' optioinal
    df['motionCfd']['headingCfd'] = 0  #'unavailable' optioinal
    df['motionCfd']['steerCfd'] = 0  #'unavailable' optioinal

    df['accelSet'] = {}
    #accelSet
    df['accelSet']['long'] = 0
    df['accelSet']['lat'] = 0
    df['accelSet']['vert'] = 0
    df['accelSet']['yaw'] = 0

    df['brakes'] = {}
    #brakes
    df['brakes']['brakePadel'] = 0  #'unavailable' optioinal
    df['brakes']['wheelBrakes'] = [[0], 5] #optioinal
    df['brakes']['traction'] = 0  #'unavailable' optioinal
    df['brakes']['abs'] = 0  #'unavailable' optioinal
    df['brakes']['scs'] = 0  #'unavailable' optioinal
    df['brakes']['brakeBoost'] = 0  #'unavailable' optioinal
    df['brakes']['auxBrakers'] = 0  #'unavailable' optioinal

    df['size'] = {}
    #size
    df['size']['width'] = 500
    df['size']['length'] = 180
    df['size']['height'] = 160 #optioinal

    df['vehicleClass'] = {}
    #vheicleClass
    df['vehicleClass']['classification'] = 0
    df['vehicleClass']['fuelType'] = 0 #optioinal

    df['safetyExt'] = {} #optioinal
    df['safetyExt']['events'] = [[0,0], 13] #optioinal
    df['safetyExt']['lights'] = [[0,0], 9] #optioinal

    df['emergencyExt']={}
    #emergencyExt
    df['emergencyExt']['responseType'] = 0 #optioinal
    df['emergencyExt']['sirenUse'] = 0 #optioinal
    df['emergencyExt']['lightsUse'] = 0 #optioinal

    return df

def PrepareForCode(bsm):
    import copy
    codetobe=copy.deepcopy(bsm)
    
    codetobe['id']=str.encode(bsm['id'])
    if(len(codetobe['id'])>8):
        codetobe['id']=codetobe['id'][0:7]
    else:
        while(len(codetobe['id'])<8):
            codetobe['id']=codetobe['id']+b'\x00'
    codetobe['plateNo']=str.encode(bsm['plateNo'])
    if(len(codetobe['plateNo'])>4):
        codetobe['plateNo']=codetobe['plateNo'][0:3]
    else:
        while(len(codetobe['plateNo'])<4):
            codetobe['plateNo']=codetobe['plateNo']+b'\x00'

    codetobe['secMark']=round(bsm['secMark'])
    codetobe['heading']=round(bsm['heading'])
    codetobe['speed']=round(bsm['speed'])
    codetobe['angle']=round(bsm['angle'])
    codetobe['pos']['lat']=round(bsm['pos']['lat'])
    codetobe['pos']['long']=round(bsm['pos']['long'])
    codetobe['pos']['elevation']=round(bsm['pos']['elevation'])
    codetobe['accelSet']['long']=round(bsm['accelSet']['long'])
    codetobe['accelSet']['lat']=round(bsm['accelSet']['lat'])
    codetobe['accelSet']['vert']=round(bsm['accelSet']['vert'])
    codetobe['accelSet']['yaw']=round(bsm['accelSet']['yaw'])
    codetobe['size']['width']=round(bsm['size']['width'])
    codetobe['size']['length']=round(bsm['size']['length'])
    codetobe['size']['height']=round(bsm['size']['height'])
    ba=bytearray(bsm['brakes']['wheelBrakes'][0])
    codetobe['brakes']['wheelBrakes']=(bytes(ba),5)

    ba=bytearray(bsm['safetyExt']['events'][0])
    codetobe['safetyExt']['events']=(bytes(ba), bsm['safetyExt']['events'][1]) 
    ba=bytearray(bsm['safetyExt']['lights'][0])
    codetobe['safetyExt']['lights']=(bytes(ba), bsm['safetyExt']['lights'][1])
    codetobe['safetyExt']['lights']=(bytes(ba), bsm['safetyExt']['lights'][1])
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