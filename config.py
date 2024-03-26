# Default configuration for remote from image 
def default(data):
    if data < 0: 
        pass
    
    elif data == 69:
        print("CH-")
        
    elif data == 70:
        print("CH")
        
    elif data == 71:
        print("CH+")
        
    elif data == 68:
        print("PREV")
        
    elif data == 64:
        print("NEXT")
        
    elif data == 67:
        print("PLAY/PAUSE")
        
    elif data == 7:
        print("VOL-")
        
    elif data == 21:
        print("VOL+")
        
    elif data == 9:
        print("EQ")
        
    elif data == 22:
        print("0")
        
    elif data == 25:
        print("100+")
        
    elif data == 13:
        print("200+")
        
    elif data == 12:
        print("1")
        
    elif data == 24:
        print("2")
        
    elif data == 94:
        print("3")
        
    elif data == 8:
        print("4")
        
    elif data == 28:
        print("5")
        
    elif data == 90:
        print("66")
        
    elif data == 66:
        print("7")
        
    elif data == 82:
        print("8")
        
    elif data == 74:
        print("9")


# Printing sent value of remote 
def search(data):
    if data < 0:
        pass
    
    else:
        print(f"{data}")
        
    