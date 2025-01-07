pki_switch = False

def update_pki_switch(val: bool):
    global pki_switch
    pki_switch = val
    

def get_pki_switch():
    global pki_switch
    return pki_switch