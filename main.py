from machine import Pin
from config import default, search
from ir_rx.nec import NEC_8
from ir_rx.print_error import print_error


# Define IR receiver pin
pin_ir = Pin(28, Pin.IN)


# Define output pins
pin_1 = Pin(2, Pin.OUT)
pin_2 = Pin(3, Pin.OUT)
pin_3 = Pin(4, Pin.OUT)
pin_4 = Pin(5, Pin.OUT)


# Function to turn off all LEDs
def off_all():
    pin_1.off()
    pin_2.off()
    pin_3.off()
    pin_4.off()
    pass


# Function to toggle the state of an LED
def switch_led(pin_id):
    if pin_id.value() == 0:
        pin_id.on()
        
    else:
        pin_id.off()


# Executes actions based on received remote control data
def remote_value(data):    
    if data == 22:
        off_all()
        
    elif data == 12:
        switch_led(pin_1)
        
    elif data == 24:
        switch_led(pin_2)
        
    elif data == 94:
        switch_led(pin_3)
        
    elif data == 8:
        switch_led(pin_4)
        

def decodeKeyValue(data):
    return data
    

# Here you can select type of callback by comment/uncomment functions
def callback(data, addr, ctrl):
    remote_value(data)   # default for this project
    #default(data)       # printing names of button on remote
    #search(data)        # searching for new values from other NEC remote  


# Debug information 
receiver = NEC_8(pin_ir, callback)
receiver.error_function(print_error)

try:
    while True:
        pass
except KeyboardInterrupt:
    receiver.close()

