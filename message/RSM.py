import os
import copy
import asn1tools

# Define the RSM Data Frame
def RSM_DF():
    df = {}

    df['msgCnt'] = 0
    df['id'] = '00000000'
    df['refPos'] = {}
    # refPos
    df['refPos']['lat'] = 0
    df['refPos']['long'] = 0
    df['refPos']['elevation'] = 0  # optional

    df['participants'] = []
    return df


# Define Participant Data Frame
def RSMParticipantData_DF():
    df = {}

    df['ptcType'] = 0  # unknown
    df['ptcId'] = 0
    df['source'] = 0  # unknown
    df['id'] = '00000000'  # optional
    df['plateNo'] = '0000'  # optional
    df['secMark'] = 0

    df['pos'] = {}
    # posOffset
    df['pos']['offsetLL'] = ('position-LatLon', {'lon': 0, 'lat': 0})
    df['pos']['offsetV'] = ('elevation', 0)

    df['posConfidence'] = {}
    # accuracy
    df['posConfidence']['pos'] = 0  # 'unavailable'
    df['posConfidence']['elevation'] = 0  # 'unavailable' optional

    df['transmission'] = 7  # 'unavailable' for transmission state
    df['speed'] = 0
    df['heading'] = 0
    df['angle'] = 0  # optional
    df['motionCfd'] = {}  # optional
    # motionCfd
    df['motionCfd']['speedCfd'] = 0  # 'unavailable' optional
    df['motionCfd']['headingCfd'] = 0  # 'unavailable' optional
    df['motionCfd']['steerCfd'] = 0  # 'unavailable' optional

    df['accelSet'] = {}  # optional
    # accelSet
    df['accelSet']['long'] = 0
    df['accelSet']['lat'] = 0
    df['accelSet']['vert'] = 0
    df['accelSet']['yaw'] = 0

    df['size'] = {}
    # size
    df['size']['width'] = 180
    df['size']['length'] = 500
    df['size']['height'] = 30  # optional

    df['vehicleClass'] = {}  # optional
    # vehicleClass
    df['vehicleClass']['classification'] = 0
    df['vehicleClass']['fuelType'] = 0  # optional
    return df


# Prepare the RSM for encoding (converts the necessary fields)
def PrepareForCode(rsm):
    codetobe = copy.deepcopy(rsm)
    codetobe['id'] = str.encode(rsm['id'])
    for participant in codetobe['participants']:
        participant['id'] = str.encode(participant['id'])
        participant['plateNo'] = str.encode(participant['plateNo'])
    return codetobe


if __name__ == '__main__':
    # Create RSM data and add a participant
    rsmData = RSM_DF()
    participant = RSMParticipantData_DF()
    rsmData['participants'].append(participant)
    participant['id'] = '00000001'
    participant['pos']['position-LatLon'] = {'lon': 10, 'lat': 20}
    # Path to ASN.1 schema
    dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    parent_directory = os.path.dirname(dir)
    asnPath = os.path.join(parent_directory, 'VSS','message','asn', 'LTEV.asn')
    print(rsmData)
    # Compile ASN.1 schema
    ltevCoder = asn1tools.compile_files(asnPath, 'uper', numeric_enums=True)
    rsmData = {'msgCnt': 0, 'id': '00000000', 'refPos': {'lat': -2, 'long': -1, 'elevation': 0}, 'participants': [{'ptcType': 0, 'ptcId': 0, 'source': 0, 'id': '00000000', 'plateNo': '0000', 'secMark': 0, 'pos': {'offsetLL': ('position-LatLon', {'lon': -2, 'lat': -4}), 'offsetV': ('elevation', 0)}, 'posConfidence': {'pos': 0, 'elevation': 0}, 'transmission': 7, 'speed': 0, 'heading': 0, 'angle': 0, 'motionCfd': {'speedCfd': 0, 'headingCfd': 0, 'steerCfd': 0}, 'accelSet': {'long': 0, 'lat': 0, 'vert': 0, 'yaw': 0}, 'size': {'width': 180, 'length': 500, 'height': 30}, 'vehicleClass': {'classification': 0, 'fuelType': 0}}]}
    # rsmData = {'msgCnt': 0, 'id': '00000000', 'refPos': {'lat': 0, 'long': 0, 'elevation': 0}, 'participants': [{'ptcType': 0, 'ptcId': 0, 'source': 0, 'id': '00000001', 'plateNo': '0000', 'secMark': 0, 'pos': {'offsetLL': ('position-LatLon', {'lon': 0, 'lat': 0}), 'offsetV': ('elevation', 0), 'position-LatLon': {'lon': 10, 'lat': 20}}, 'posConfidence': {'pos': 0, 'elevation': 0}, 'transmission': 7, 'speed': 0, 'heading': 0, 'angle': 0, 'motionCfd': {'speedCfd': 0, 'headingCfd': 0, 'steerCfd': 0}, 'accelSet': {'long': 0, 'lat': 0, 'vert': 0, 'yaw': 0}, 'size': {'width': 180, 'length': 500, 'height': 30}, 'vehicleClass': {'classification': 0, 'fuelType': 0}}]}
    # Encode the RSM data into the desired format
    rsmEncoded = ltevCoder.encode('RoadsideSafetyMessage', PrepareForCode(rsmData))
    print("Encoded RSM Data:", rsmEncoded)

    # Decode the encoded RSM data back to a Python object
    rsmDecoded = ltevCoder.decode('RoadsideSafetyMessage', rsmEncoded)
    print("Decoded RSM Data:", rsmDecoded)
