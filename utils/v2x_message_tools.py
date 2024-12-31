from entities.vehicle import Vehicle
from V2X import Build_BSM
from V2X.Message import BSM  

def build_bsm(idx, x, y, z, yaw, pitch, roll, speed, time, ltevCoder):
        rv_info = {}
        rv_info['ID'] = idx
        rv_info['Time'] = time
        rv_info['X'] = x
        rv_info['Y'] = y
        rv_info['Z'] = z
        rv_info['Yaw'] = yaw
        rv_info['Pitch'] = pitch
        rv_info['Roll'] = roll
        rv_info['Speed'] = speed
        rv_info['counter'] = 0
        rv_bsm_msg = Build_BSM.getBSMData(rv_info)
        rv_bsm_frame = ('bsmFrame', BSM.PrepareForCode(rv_bsm_msg))
        rv_bsmEncoded = ltevCoder.encode('MessageFrame', rv_bsm_frame)
        dsmpHeader_bsm = int(4).to_bytes(2, byteorder="big", signed=False)
        data_bsm = dsmpHeader_bsm + rv_bsmEncoded
        return data_bsm

def cal_ttc(s, v):
    v = v / 3.6
    ttc = 15
    if v < 0.1:
        ttc = - (s-4) / v
    if ttc > 15:
        ttc = 15
    # if s < 9:
    #     ttc = 0
    return ttc        