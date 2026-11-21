from machine import Pin, PWM, time_pulse_us
import time
import neopixel

# --- PINES ---
# Motor A: lado izquierdo
PIN_MOTOR_A1 = 5
PIN_MOTOR_A2 = 6

# Motor B: lado derecho
PIN_MOTOR_B1 = 7
PIN_MOTOR_B2 = 8

# Sensor ultrasonico Frontal
PIN_TRIG_FRENTE = 9
PIN_ECHO_FRENTE = 10

# Sensor ultrasonico Izquierdo (CAMBIAR POR PINES REALES)
PIN_TRIG_IZQ = 11
PIN_ECHO_IZQ = 12

# Sensor ultrasonico Derecho (CAMBIAR POR PINES REALES)
PIN_TRIG_DER = 3
PIN_ECHO_DER = 4

# NeoPixel integrado
PIN_NEOPIXEL = 21

# --- PARÁMETROS ---
FRECUENCIA_PWM = 20000
DISTANCIA_ATAQUE_CM = 45
INTERVALO_ULTRASONICO_MS = 60

VELOCIDAD_BUSQUEDA = 70
VELOCIDAD_ATAQUE = 100

# ESTADOS DEL AUTOMATA SIMPLIFICADO
BUSQUEDA = 1
ATAQUE = 2

NOMBRES_ESTADOS = {
    1: "BUSQUEDA",
    2: "ATAQUE",
}

# --- CONFIGURACIÓN DE HARDWARE ---
motor_a_1 = PWM(Pin(PIN_MOTOR_A1), freq=FRECUENCIA_PWM)
motor_a_2 = PWM(Pin(PIN_MOTOR_A2), freq=FRECUENCIA_PWM)
motor_b_1 = PWM(Pin(PIN_MOTOR_B1), freq=FRECUENCIA_PWM)
motor_b_2 = PWM(Pin(PIN_MOTOR_B2), freq=FRECUENCIA_PWM)

trig_frente = Pin(PIN_TRIG_FRENTE, Pin.OUT, value=0)
echo_frente = Pin(PIN_ECHO_FRENTE, Pin.IN)

trig_izq = Pin(PIN_TRIG_IZQ, Pin.OUT, value=0)
echo_izq = Pin(PIN_ECHO_IZQ, Pin.IN)

trig_der = Pin(PIN_TRIG_DER, Pin.OUT, value=0)
echo_der = Pin(PIN_ECHO_DER, Pin.IN)

led = neopixel.NeoPixel(Pin(PIN_NEOPIXEL), 1)

def set_color(rojo, verde, azul):
    led[0] = (rojo, verde, azul)
    led.write()

# --- CONTROL DE MOTORES ---
def convertir_velocidad(velocidad):
    velocidad = max(0, min(100, velocidad))
    return int(velocidad * 655.35)

def mover_motor_a(velocidad):
    velocidad = max(-100, min(100, velocidad))
    potencia = convertir_velocidad(abs(velocidad))
    if velocidad > 0:
        motor_a_1.duty_u16(potencia)
        motor_a_2.duty_u16(0)
    elif velocidad < 0:
        motor_a_1.duty_u16(0)
        motor_a_2.duty_u16(potencia)
    else:
        motor_a_1.duty_u16(0)
        motor_a_2.duty_u16(0)

def mover_motor_b(velocidad):
    velocidad = max(-100, min(100, velocidad))
    potencia = convertir_velocidad(abs(velocidad))
    if velocidad > 0:
        motor_b_1.duty_u16(potencia)
        motor_b_2.duty_u16(0)
    elif velocidad < 0:
        motor_b_1.duty_u16(0)
        motor_b_2.duty_u16(potencia)
    else:
        motor_b_1.duty_u16(0)
        motor_b_2.duty_u16(0)

def mover_motores(velocidad_a, velocidad_b):
    mover_motor_a(velocidad_a)
    mover_motor_b(velocidad_b)

def detener():
    mover_motores(0, 0)

def avanzar(velocidad):
    mover_motores(velocidad, velocidad)

def girar_derecha(velocidad):
    mover_motores(velocidad, -velocidad)
    
def girar_izquierda(velocidad):
    mover_motores(-velocidad, velocidad)

# --- LECTURA DE SENSORES ---
def medir_distancia_cm(pin_trig, pin_echo):
    pin_trig.off()
    time.sleep_us(2)
    pin_trig.on()
    time.sleep_us(10)
    pin_trig.off()

    duracion = time_pulse_us(pin_echo, 1, 25000)

    if duracion < 0:
        return 999 # Retorna un valor alto si no detecta nada

    return (duracion * 0.0343) / 2

# --- FUNCIONAMIENTO PRINCIPAL ---
def cambiar_estado(nuevo_estado):
    print("Estado:", NOMBRES_ESTADOS[nuevo_estado])
    return nuevo_estado

estado = BUSQUEDA
ultima_medicion = 0

detener()
set_color(0, 255, 0)
print("Minisumo encendido: Modo de prueba (3 Ultrasónicos)")
print("Estado: BUSQUEDA")

try:
    while True:
        ahora = time.ticks_ms()

        if time.ticks_diff(ahora, ultima_medicion) >= INTERVALO_ULTRASONICO_MS:
            ultima_medicion = ahora
            
            # Leer los tres sensores
            dist_frente = medir_distancia_cm(trig_frente, echo_frente)
            dist_izq = medir_distancia_cm(trig_izq, echo_izq)
            dist_der = medir_distancia_cm(trig_der, echo_der)

            # Lógica de detección y movimiento
            if dist_frente <= DISTANCIA_ATAQUE_CM:
                if estado != ATAQUE:
                    set_color(255, 0, 255) # Morado = Atacando de frente
                    estado = cambiar_estado(ATAQUE)
                avanzar(VELOCIDAD_ATAQUE)
                
            elif dist_izq <= DISTANCIA_ATAQUE_CM:
                set_color(0, 0, 255) # Azul = Girando a la izquierda hacia objetivo
                girar_izquierda(VELOCIDAD_ATAQUE)
                estado = BUSQUEDA # Se mantiene en búsqueda hasta que lo tenga enfrente
                
            elif dist_der <= DISTANCIA_ATAQUE_CM:
                set_color(255, 255, 0) # Amarillo = Girando a la derecha hacia objetivo
                girar_derecha(VELOCIDAD_ATAQUE)
                estado = BUSQUEDA
                
            else:
                if estado != BUSQUEDA:
                    print("Contrincante perdido; regresando a busqueda libre")
                    set_color(0, 255, 0) # Verde = Buscando
                    estado = cambiar_estado(BUSQUEDA)
                girar_derecha(VELOCIDAD_BUSQUEDA)

        time.sleep_ms(2)

except KeyboardInterrupt:
    detener()
    set_color(0, 0, 0)
    print("Programa detenido por el usuario")

except Exception as error:
    detener()
    set_color(255, 0, 0)
    print("Error; motores detenidos:", error)
    raise