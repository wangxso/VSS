def PSM_DF():
    df = {}

    df['msgCnt'] = 0
    df['id'] = '00000000'
    df['secMark'] = 0
    df['timeConfidence'] = 0
    df['pos'] = {}
    df['posAccuracy'] = {}
    df['posAccuracy']['semiMajor'] = 255 
    df['posAccuracy']['semiMinor'] = 255 
    df['posAccuracy']['orientation'] = 65535 
    df['speed'] = 0
    df['heading'] = 0

    df['accelSet'] = {}
    df['accelSet']['long'] = 0
    df['accelSet']['lat'] = 0
    df['accelSet']['vert'] = 0
    df['accelSet']['yaw'] = 0

    df['pathHistory'] = {}
    df['pathHistory']['initialPosition'] = {}
    df['pathHistory']['initialPosition']['utcTime'] = {}
    df['pathHistory']['initialPosition']['pos'] = {}
    df['pathHistory']['initialPosition']['heading'] = 0
    df['pathHistory']['initialPosition']['transmission'] = 0
    df['pathHistory']['initialPosition']['speed'] = 0
    df['pathHistory']['initialPosition']['posAccuracy'] = {}
    df['pathHistory']['initialPosition']['timeConfidence'] = 0
    df['pathHistory']['initialPosition']['motionCfd'] = {}


    df['pathHistory']['currGNSSstatus'] = ([0], 8) 
    df['pathHistory']['crumbData'] = {}

    df['path-Planning'] = []
    df['overallRadius'] = 200
    df['non-motorData'] = {}
    df['non-motorData']['basicType'] = 1
    df['non-motorData']['propulsion'] = ('human',0) 

    df['non-motorData']['clusterSize'] = 0
    df['non-motorData']['attachment'] = 0
    df['non-motorData']['personalExt'] = {}
    df['non-motorData']['personalExt']['useState'] = ([0,0], 9) 
    df['non-motorData']['personalExt']['assistType'] = ([0], 6) 
    df['non-motorData']['roadWorkerExt'] = {}
    df['non-motorData']['roadWorkerExt']['workerType'] = 0
    df['non-motorData']['roadWorkerExt']['activityType'] = ([0], 6) 
    df['non-motorData']['personalReq'] = {}
    df['non-motorData']['personalReq']['crossing'] = 0

    return df

    
    

def PrepareForCode(vir):
    pass
    
if __name__=='__main__':

    pass