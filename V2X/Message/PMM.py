def PMM_DF():
    df = {}

    df['msgCnt'] = 0

    df['id'] = '00000000'

    df['secMark'] = 0
    
    df['pid'] = 0
    

    df['role'] = 0
    #RoleInPlatooning
	# RoleInPlatooning ::= ENUMERATED {
	# 	leader (0),
	# 	follower (1),
	# 	tail(2),
	# 	free-vehicle(3),
	# 	...
	# }

  
    df['status'] = 0
    #StatusInPlatooning
	# StatusInPlatooning ::= ENUMERATED {
	# 	-- possible states of platooning members
	# 	-- a complete platooning process can include all or part of them
	# 	navigating (0),
	# 	beginToDissmiss (1),
	# 	askForJoining (2),
	# 	joining (3),
	# 	following (4),
	# 	askForLeaving (5),
	# 	leaving (6),
	# 	...
	# }

    df['leadingExt'] = {}
    #MemberManagement
    df['leadingExt']['memberList'] = [] 
    df['leadingExt']['joiningList'] = []
    df['leadingExt']['leavingList'] = []
    df['leadingExt']['capacity'] = 10
    df['leadingExt']['openToJoin'] = True

    return df

def MemberList():
    df = []
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