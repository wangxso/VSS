def PAM_DF():
    df = {}

    df['msgCnt'] = 0

    df['timeStamp'] = 0

  
    df['parkingLotInfo'] = {}
    #停车场信息
    df['parkingLotInfo']['id'] = 1 # Unique id of this parking lot
    df['parkingLotInfo']['name'] = 'Pano_Park01'
    df['parkingLotInfo']['number'] = 60  # Total number of parking slots
    df['parkingLotInfo']['buildingLayerNum'] = 1 
    df['parkingLotInfo']['avpType'] = 4
    
    # AVPType ::=  ENUMERATED {
	# 	p0(0),
	# 	-- Original parking lot
	# 	p1(1),
	# 	-- Standard parking lot
	# 	p2(2),
	# 	-- Parking lot with special identification
	# 	p3(3),
	# 	-- Parking lot with roadside infrastructure
	# 	p4(4),
	# 	-- Parking lot with roadside infrastructure and V2X
	# 	p5(5),
	# 	-- AVP dedicated parking lot
	# 	...
	# }

    df['pamNodes'] = [] # -- intersections or road endpoints in parking area
    #场站地图节点信息
     
    df['parkingAreaGuidance'] = []
    #连接到此节点的道路信息

    return df

def PAMNode_DF():
    df={}
    df['id']= 256  #INTEGER (0..65535)
    # -- The values zero through 255 are allocated for testing purposes 
	# -- Note that the value assigned to a node will be 
	# -- unique within a parking area

    df['refPos']={}
    #refPos
    df['refPos']['lat']=0
    df['refPos']['long']=0
    df['refPos']['elevation']=0 #optioinal

    df['floor'] = 1
    df['attributes'] = ([0],8)
    # PAMNodeAttributes ::= BIT STRING {
	# 	entrance(0),
	# 	exit(1),
	# 	toUpstair(2),
	# 	toDownstair(3),
	# 	etc(4),
	# 	mtc(5),
	# 	passAfterPayment(6),
	# 	blocked(7)
	# } (SIZE(8,...))
    df['inDrives'] = [] #-- all the links enter this Node
    return df

def PAMDrive_DF():
    df={}
    df['upstreamPAMNodeId']= 0
    df['driveID']= 0   #NTEGER (0..255) OPTIONAL,
    #-- local id of this drive with same upsttramPAMNode and PAMNode 
    df['twowaySepration']= False  #BOOLEAN  道路是否被分割为不同的两个运动方向
    df['speedLimit'] = 10/0.05
    df['heightRestriction'] = 3.8/0.1
    df['driveWidth'] = 3.5/0.01
    df['laneNum'] = 2
    df['points'] = []
    df['movements'] = [] #-- Define movements at intersection     SEQUENCE (SIZE(1..32)) OF PAMNodeID
    df['parkingSlots'] = [] #-- Information of parking places of this drive
    
    return df
    
def ParkingSlot_DF():
    df={}
    df['slotID']= 0
    df['position']= {}
    df['position']['topLeft'] = {} #PositionOffsetLLV
    df['position']['topLeft']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    df['position']['topLeft']['offsetV']=('elevation', 0)
    df['position']['topRight'] = {}
    df['position']['topRight']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    df['position']['topRight']['offsetV']=('elevation', 0)
    df['position']['bottomLeft'] = {}
    df['position']['bottomLeft']['offsetLL']=('position-LatLon', {'lon':0, 'lat':0})
    df['position']['bottomLeft']['offsetV']=('elevation', 0)
    df['sign']= 'B101'  #-- Parking slot sign like "B101"
    df['parkingType'] = ([0,0],10)
    df['status'] = 0
    # SlotStatus ::= ENUMERATED {
	# 	unknown(0),
	# 	available(1),
	# 	occupied(2),
	# 	reserved(3),
	# 	...
	# }
    df['parkingSpaceTheta'] = 0
    # ParkingSpaceTheta ::= ENUMERATED {
	# 	unknown(0),
	# 	vertical(1),
	# 	side(2),
	# 	oblique(3),
	# 	...
	# }
    df['parkingLock'] = 0
	# ParkingLock ::= ENUMERATED {
	# 	unknown(0),
	# 	nolock(1),
	# 	locked(2),
	# 	unlocked(3),
	# 	...
	# }
    
    return df

    
def ParkingGuide_DF():
    df={}
    df['vehId'] = 'Pano_0' # OCTET STRING (SIZE(8)),
    
    df['drivePath'] = [] # SEQUENCE (SIZE(1..32)) OF PAMNodeID
    # -- the planned path for this vehicle
    # -- represented by a series of PAMNode id
    # -- in order from origin to destination
    
    df['targetParkingSlot'] = 0  #  INTEGER (0..65535) OPTIONAL,
    # -- if the vehicle is looking for a parking slot,
    # -- then here is the recommended parking slot id,
    # -- which should be by the last drive road in above drivePath.
    # -- if a targetParkingSlot is not included in a ParkingGuide,
    # -- then probably the vehicle is going to the last PAMNode
    # -- whatever type the PAMNode is.
    



def PrepareForCode(pam):
    import copy
    codetobe=copy.deepcopy(pam)
    
    codetobe['id']=str.encode(pam['id'])
    if(len(codetobe['id'])>8):
        codetobe['id']=codetobe['id'][0:7]
    else:
        while(len(codetobe['id'])<8):
            codetobe['id']=codetobe['id']+b'\x00'

    # codetobe['secMark']=round(vir['secMark']*1000)

    # codetobe['pos']['lat']=round(vir['pos']['lat'])
    # codetobe['pos']['long']=round(vir['pos']['long'])
    # codetobe['pos']['elevation']=round(vir['pos']['elevation'])


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