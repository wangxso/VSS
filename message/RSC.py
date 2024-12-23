def RSC_DF():
    df = {}

    df['msgCnt'] = 0
    df['id'] = '00000001'
    df['secMark'] = 0
    df['refPos'] = {}
    #refPos
    df['refPos']['lat'] = 0
    df['refPos']['long'] = 0
    df['refPos']['elevation'] = 0 #optioinal

    df['coordinates'] = [] #optioinal
    df['laneCoordinates'] = [] #optioinal
    return df


def coordinates():
    df = {}

    df['vehId'] = '00000000'  
    df['driveSuggestion'] = 0  
    df['pathGuidance'] = 0   
    df['info'] = [[0], 8] 
    return df

def laneCoordinates():
    df = {}

    df['targetLane'] = {}
    df['targetLane'] ['upstreamNodeId']=0
    df['targetLane'] ['downstreamNodeId']=0
    df['targetLane'] ['referenceLanes']=([0,0], 16)
    
    df['relatedPath'] = {} 
    df['relatedPath']['activePath']=[] #SEQUENCE (SIZE(2..32)) OF PositionOffsetLLV
    df['relatedPath']['pathRadius']=200   
    
    df['tBegin'] = {} 
    df['tBegin']['year'] = 0
    df['tBegin']['month'] = 0
    df['tBegin']['day'] = 0
    df['tBegin']['hour'] = 0
    df['tBegin']['minute'] = 0
    df['tBegin']['second'] = 0
    df['tBegin']['offset'] = 0
    
    df['tEnd'] = {}
    df['tEnd']['year'] = 0
    df['tEnd']['month'] = 0
    df['tEnd']['day'] = 0
    df['tEnd']['hour'] = 0
    df['tEnd']['minute'] = 0
    df['tEnd']['second'] = 0
    df['tEnd']['offset'] = 0
    
    df['recommendedSpeed'] = 0 
    df['recommendedBehavior'] = ([0,0], 14) 
    df['info'] =[[0], 8]  
    df['description'] = '0' #GB2312-80
    return df


def PrepareForCode(rsc):
    import copy
    codetobe=copy.deepcopy(rsc)
    codetobe['id']=str.encode(rsc['id'])
    # for participant in codetobe['participants']:       
    #     participant['id']=str.encode(participant['id'])
    #     participant['plateNo']=str.encode(participant['plateNo'])
    return codetobe

if __name__=='__main__':

    rscData=RSC_DF()
    participant=coordinates()
    rscData['participants'].append(participant)

    import os
    import asn1tools

    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper',
    #cache_dir=dir+'\\code',
    numeric_enums=True)

    rscEncoded=ltevCoder.encode('RoadsideSafetyMessage', PrepareForCode(rscData))
    print(rscEncoded)
    rscDecoded=ltevCoder.decode('RoadsideSafetyMessage', rscEncoded)