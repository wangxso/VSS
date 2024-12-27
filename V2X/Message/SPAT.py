def SPAT_DF():
    df={}

    df['msgCnt']=0
    df['moy']=527040 #optioinal
    df['name']='spat' #optioinal
    df['intersections']=[]
    return df


def SPATIntersectionState_DF():
    df={}

    df['intersectionId']={}
    #id
    df['intersectionId']['region']=1 #optioinal
    df['intersectionId']['id']=0

    df['status']=([0,0], 16)
    df['moy']=527040 #optioinal
    df['timeStamp']=0 #optioinal
    df['timeConfidence']=0 #optioinal
    df['phases']=[]
    return df


def SPATPhase_DF():
    df={}

    df['id']=0
    df['phaseStates']=[]
    return df


def SPATPhaseState_DF():
    df={}

    df['light']=0
    #timing
    counting={}
    counting['startTime']=36001
    counting['likelyEndTime']=36001
    counting['nextDuration']=36001 #optioinal
    df['timing']=('counting', counting) #optioinal

    return df


def PrepareForCode(spat):
    import copy
    codetobe=copy.deepcopy(spat)
    for intersection in codetobe['intersections']:
        ba=bytearray(intersection['status'][0])
        intersection['status']=(bytes(ba), intersection['status'][1])
    return codetobe

if __name__=='__main__':

    spatData=SPAT_DF()
    intersection=SPATIntersectionState_DF()
    phase=SPATPhase_DF()
    phaseState=SPATPhaseState_DF()
    phase['phaseStates'].append(phaseState)
    intersection['phases'].append(phase)
    spatData['intersections'].append(intersection)

    import os
    import asn1tools

    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper',
    #cache_dir=dir+'\\code',
    numeric_enums=True)

    spatEncoded=ltevCoder.encode('SPAT', PrepareForCode(spatData))
    print(spatEncoded)
    spatDecoded=ltevCoder.decode('SPAT', spatEncoded)