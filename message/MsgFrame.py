if __name__!='__main__':
    from . import *
    from . import BSM
    from . import SPAT
    from . import MAP
    from . import RSI
    from . import RSM
    from . import SSM
    from . import PMM
    from . import RSC
    from . import VIR
    # from . import PAM
    from . import RTCM 
    from . import PSM

# 返回BSM数据帧
def BSM_MsgFrame():
    #return ('bsmFrame', BSM.BSM_DF())
    return BSM.BSM_DF()

def RSMParticipantData_DF():
    #return ('bsmFrame', BSM.BSM_DF())
    return RSM.RSMParticipantData_DF()

# 返回MAP数据帧
def MAP_MsgFrame():
    #return ('mapFrame', MAP.Map_DF())
    return MAP.Map_DF()

# 返回RSM数据帧
def RSM_MsgFrame():
    #return ('rsmFrame', RSM.RSM_DF())
    return RSM.RSM_DF()

# 返回SPAT数据帧
def SPAT_MsgFrame():
    #return ('spatFrame', SPAT.SPAT_DF())
    return SPAT.SPAT_DF()

# 返回RSI数据帧
def RSI_MsgFrame():
    #return ('rsiFrame', RSI.RSI_DF())
    return RSI.RSI_DF()

def SSM_MsgFrame():
    return SSM.SSM_DF()

def VIR_MsgFrame():
    return VIR.VIR_DF()

def RSC_MsgFrame():
    return RSC.RSC_DF()

def PMM_MsgFrame():
    return PMM.PMM_DF()

# def PAM_MsgFrame():
#     return PAM.PAM_DF()

def RTCM_MsgFrame():
    return RTCM.RTCM_DF()

def PSM_MsgFrame():
    return PSM.PSM_DF()

if __name__=='__main__':
    
    import BSM
    import SPAT
    import MAP
    import RSI
    import RSM

    bsmFrame=('bsmFrame', BSM.PrepareForCode(BSM.BSM_DF()))
    mapFrame=('mapFrame', MAP.PrepareForCode(MAP.Map_DF()))
    rsmFrame=('rsmFrame', RSM.PrepareForCode(RSM.RSM_DF()))
    spatFrame=('spatFrame', SPAT.SPAT_DF())
    rsiFrame=('rsiFrame', RSI.PrepareForCode(RSI.RSI_DF()))

    import os
    import asn1tools
    dir=os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    asnPath=dir+'\\asn\\LTEV.asn'
    ltevCoder=asn1tools.compile_files(asnPath, 'uper',
    #cache_dir=dir+'\\code',
    numeric_enums=True)

    bsmEncoded=ltevCoder.encode('MessageFrame', bsmFrame)
    bsmDecoded=ltevCoder.decode('MessageFrame', bsmEncoded)

    mapEncoded=ltevCoder.encode('MessageFrame', mapFrame)
    mapDecoded=ltevCoder.decode('MessageFrame', mapEncoded)

    rsmEncoded=ltevCoder.encode('MessageFrame', rsmFrame)
    rsmDecoded=ltevCoder.decode('MessageFrame', rsmEncoded)

    spatEncoded=ltevCoder.encode('MessageFrame', spatFrame)
    spatDecoded=ltevCoder.decode('MessageFrame', spatEncoded)

    rsiEncoded=ltevCoder.encode('MessageFrame', rsiFrame)
    rsiDecoded=ltevCoder.decode('MessageFrame', rsiEncoded)