from machine import Pin, PWM
import time
import neopixel

pwm_r = PWM(Pin(4), freq=20000)
dir1_r=Pin(5, Pin.OUT)
dir2_r=Pin(6, Pin.OUT)

pwm_l = PWM(Pin(7), freq=20000)
dir1_l=Pin(8, Pin.OUT)
dir2_l=Pin(9, Pin.OUT)

def mover_motores(vel_izq, vel_der):
    '''Controla ambos motores valores entre
    -100 y 100 (Negativo= reversa, positivo=adelante)'''
    
    vel_izq=max(-100, min(100,vel_izq))
    vel_der=max(-100, min(100,vel_der))
    
    duty_izq= int(abs(vel_izq) * 655.35)
    duty_der= int(abs(vel_der) * 655.35)
    
    pwm_l.duty_u16(duty_izq)
    if vel_izq>=0:
        dir1_l.value(1)
        dir2_l.value(0)
    else:
        dir1_l.value(0)
        dir2_l.value(1)
    
    pwm_r.duty_u16(duty_der)
    if vel_der>=0:
        dir1_r.value(1)
        dir2_r.value(0)
    else:
        dir1_r.value(0)
        dir2_r.value(1)

def frenar():
    pwm_l.duty_u16(0)
    pwm_r.duty_u16(0)
    dir1_l.value(1)
    dir2_l.value(1)
    dir1_r.value(1)
    dir2_r.value(1)
    
try:
    print("Iniciando rutina de prueba")
    
    mover_motores(60,60)
    time.sleep(1.5)
    print("saliendo de mover motores avanzar al frente")
    
    mover_motores(70,-70)
    time.sleep(1.5)
    print("saliendo de giro rapido a la derecha")
    
    mover_motores(-50,-50)
    time.sleep(1.5)
    print("saliendo en reversa al 50%")
    
    frenar()
    print("Prueba finalizada")
    
except KeyboardInterrupt:
    frenar()
    print("Programa detenido por el usuario")
    


