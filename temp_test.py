AID_1 = int(1).to_bytes(length=4, byteorder='big')
AID_bsm = int(1).to_bytes(length=4, byteorder='big')

print(AID_1==AID_bsm)