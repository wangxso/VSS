def Map_DF():
    df={}

    df['msgCnt']=0
    df['nodes']=[]
    return df


def MapNode_DF():
    df={}

    df['name']='' #optioinal
    df['id']={}
    #id
    df['id']['region']=0 #optioinal
    df['id']['id']=0

    df['refPos']={}
    #refPos
    df['refPos']['lat']=0
    df['refPos']['long']=0
    df['refPos']['elevation']=0 #optioinal

    df['inLinks']=[] #optioinal
    return df


def MapLink_DF():
    df={}

    df['name']='' #optioinal
    df['upstreamNodeId']={}
    #upstreamNodeId
    df['upstreamNodeId']['region']=0 #optioinal
    df['upstreamNodeId']['id']=0
    df['speedLimits']=[] #optioinal
    df['linkWidth']=350
    df['points']=[]
    df['movements']=[]
    df['lanes']=[]
    return df


def MapSpeedLimit_DF():
    df={}

    df['type']=0 #unknown optioinal
    df['speed']=0
    return df


def MapPoint_DF():
    df={}

    df['posOffset']={}
    #posOffset
    df['posOffset']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    df['posOffset']['offsetV']=('elevation', 0)
    return df


def MapMovement_DF():
    df={}

    df['remoteIntersection']={}
    #remoteIntersection
    df['remoteIntersection']['region']=0 #optioinal
    df['remoteIntersection']['id']=0

    df['phaseId']=[]
    return df


def MapLane_DF():
    df={}

    df['laneID']=0
    df['laneWidth']=350
    df['laneAttributes']={} #optioinal
    #laneAttributes
    df['laneAttributes']['shareWith']=([0,0], 10) #optioinal
    df['laneAttributes']['laneType']=('vehicle', ([0], 8))

    df['maneuvers']=[[255,0], 12] #optioinal
    df['connectsTo']=[] #optioinal
    df['speedLimits']=[] #optioinal
    df['points']=[] #optioinal

    return df


def MapConnection_DF():
    df={}

    df['remoteIntersection']={}
    #remoteIntersection
    df['remoteIntersection']['region']=0 #optioinal
    df['remoteIntersection']['id']=0

    df['connectingLane']={}
    #connectingLane
    df['connectingLane']['lane']=0
    df['connectingLane']['maneuvers']=([255,255], 12) #optioinal

    df['phaseId']=[]
    return df

def PrepareForCode(map):
    
    import copy
    codetobe=copy.deepcopy(map)
    for node in codetobe['nodes']:
        for link in node['inLinks']:
            for lane in link['lanes']:
                ba=bytearray(lane['laneAttributes']['shareWith'][0])
                lane['laneAttributes']['shareWith']=(bytes(ba), lane['laneAttributes']['shareWith'][1]) 
                ba=bytearray(lane['laneAttributes']['laneType'][1][0])
                if len(link['lanes'])==1:
                    ba = bytearray([1])
                lane['laneAttributes']['laneType']=(lane['laneAttributes']['laneType'][0],
                    (bytes(ba), lane['laneAttributes']['laneType'][1][1]))
                ba=bytearray(lane['maneuvers'][0])
                lane['maneuvers']=(bytes(ba), lane['maneuvers'][1])                    
                for connection in lane['connectsTo']:
                    ba=bytearray(connection['connectingLane']['maneuver'][0])
                    connection['connectingLane']['maneuver']=(bytes(ba), connection['connectingLane']['maneuver'][1])
    return codetobe

if __name__=='__main__':

    mapData=Map_DF()
    mapNode=MapNode_DF()
    mapLink=MapLink_DF()
    mapSpeedLimit=MapSpeedLimit_DF()
    mapPoint=MapPoint_DF()
    mapMovement=MapMovement_DF()
    mapLane=MapLane_DF()
    mapConnection=MapConnection_DF()

    mapLane['connectsTo'].append(mapConnection)
    mapLane['speedLimits'].append(mapSpeedLimit)
    mapLane['points'].append(mapPoint)

    mapLink['speedLimits'].append(mapSpeedLimit)
    mapLink['points'].append(mapPoint)
    mapLink['movements'].append(mapMovement)
    mapLink['lanes'].append(mapLane)

    mapNode['inLinks'].append(mapLink)

    mapData['nodes'].append(mapNode)
    
    '''
    from osgeo import osr,ogr
    source=osr.SpatialReference()
    source.ImportFromEPSG(4326)
    #google
    target=osr.SpatialReference()
    target.ImportFromEPSG(3857)
    #简单投影转换
    global coordTrans
    coordTrans=osr.CoordinateTransformation(source,target)
    '''

    import os
    import asn1tools
    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper',
    numeric_enums=True)

    mapEncoded=ltevCoder.encode('MapData', PrepareForCode(mapData))
    print(mapEncoded)
    mapDecoded=ltevCoder.decode('MapData', mapEncoded)