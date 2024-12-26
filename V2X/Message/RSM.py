def RSM_DF():
    df = {}

    df['msgCnt'] = 0
    df['id'] = '00000000'
    df['refPos'] = {}
    #refPos
    df['refPos']['lat'] = 0
    df['refPos']['long'] = 0
    df['refPos']['elevation'] = 0 #optioinal

    df['participants'] = []
    return df


def RSMParticipantData_DF():
    df = {}

    df['ptcType'] = 0 #unknown
    df['ptcId'] = 0
    df['source'] = 0 #unknown
    df['id'] = '00000000' #optioinal
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


def PrepareForCode(rsm):
    import copy
    codetobe=copy.deepcopy(rsm)
    codetobe['id']=str.encode(rsm['id'])
    for participant in codetobe['participants']:       
        participant['id']=str.encode(participant['id'])
        participant['plateNo']=str.encode(participant['plateNo'])
    return codetobe

if __name__=='__main__':

    rsmData=RSM_DF()
    participant=RSMParticipantData_DF()
    rsmData['participants'].append(participant)

    import os
    import asn1tools

    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper',
    #cache_dir=dir+'\\code',
    numeric_enums=True)

    rsmEncoded=ltevCoder.encode('RoadsideSafetyMessage', PrepareForCode(rsmData))
    print(rsmEncoded)
    rsmDecoded=ltevCoder.decode('RoadsideSafetyMessage', rsmEncoded)