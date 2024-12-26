def RTCM_DF():
    df = {}
    df['msgCnt'] = 0
    df['corrections'] = []

    return df

def RTCMmsg():
    df = {}
    df['rev'] = 1
    df['rtcmID'] = 1 
    df['payload'] = bytes(1)

    return df
    


    
if __name__=='__main__':
    pass

