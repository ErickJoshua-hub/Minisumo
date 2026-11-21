from machine import Pin, PWM
import time
import neopixel

sensor_ir =Pin(3, Pin_IN)
PIN_LED=21
np =neopixel.NeoPixel(Pin(PIN_LED),1)

def set_color(r,g,b):
    np[0]=(r,g,b)
    np.write()

print("Sistema de deteccion de blanco y negro")

set_color(0,0,0)

while True:
    lectura=sensor_ir.value()
    
    if lectura==0:
        print("Color Blanco detectado")
        set_color(255,0,0)
    else:
        print("Color negro detectado")
        set_color(0,0,255)
    
    sleep(0.2)
        