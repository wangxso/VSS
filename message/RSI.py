from asn1tools.codecs.type_checker import Null


def RSI_DF():
    df = {}

    df['msgCnt'] = 0
    df['moy'] = 527040 #optioinal
    df['id'] = '00000000'
    
    df['refPos'] = {}
    #refPos
    df['refPos']['lat'] = 0
    df['refPos']['long'] = 0
    df['refPos']['elevation'] = 0 #optioinal
    df['rtss']=[]
    df['rtes']=[]

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

def RTSData_DF():
    df={}
    df['rtsId']=0
    df['signType']=0

    df['signPos']={} #optioinal
    #signPos
    df['signPos']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    df['signPos']['offsetV'] = ('elevation', 0)
    
    df['timeDetails']={} #optioinal
    #timeDetails
    df['timeDetails']['startTime']=0
    df['timeDetails']['endTime']=1000
    df['timeDetails']['endTimeConfidence']=0

    df['referencePaths']=[] #optioinal
    df['referenceLinks']=[] #optioinal

    return df

def ReferencePath_DF():
    df={}
    df['activePath']=[]
    df['pathRadius']=200
    return df

def ReferenceLink_DF():
    df={}
    df['upstreamNodeId']=0
    df['downstreamNodeId']=0
    df['referenceLanes']=([0,0], 15) #optioinal
    return df

def RSIPathPoint_DF():
    df = {}
    df['offsetLL'] = ('position-LatLon', {'lon':0, 'lat':0})
    df['offsetV'] = ('elevation', 0)
    return df

def PrepareForCode(rsi):
    import copy
    codetobe=copy.deepcopy(rsi)
    codetobe['id']=str.encode(rsi['id'])
    # if(codetobe.__contains__('rtes')):
    #     for rte in codetobe['rtes']:
    #         for link in rte['referenceLinks']:
    #             ba=bytearray(link['referenceLanes'][0])
    #             link['referenceLanes']=(bytes(ba), link['referenceLanes'][1])
    # if(codetobe.__contains__('rtss')):
    #     for rts in codetobe['rtss']:
    #         for link in rts['referenceLinks']:
    #             ba=bytearray(link['referenceLanes'][0])
    #             link['referenceLanes']=(bytes(ba), link['referenceLanes'][1])
    return codetobe

if __name__=='__main__':

    rsiData=RSI_DF()
    rte=RTEData_DF()
    rts=RTSData_DF()
    link=ReferenceLink_DF()
    path=ReferencePath_DF()
    point=RSIPathPoint_DF()
    path['activePath'].append(point)
    rte['referencePaths'].append(path)
    rte['referenceLinks'].append(link)
    rts['referencePaths'].append(path)
    rts['referenceLinks'].append(link)
    rsiData['rtes'].append(rte)
    rsiData['rtss'].append(rts)

    import os
    import asn1tools

    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper',
    #cache_dir=dir+'\\code',
    numeric_enums=True)

    rsiEncoded=ltevCoder.encode('RoadSideInformation', PrepareForCode(rsiData))
    print(rsiEncoded)
    rsiDecoded=ltevCoder.decode('RoadSideInformation', rsiEncoded)
