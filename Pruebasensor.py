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

# Sensor ultrasonico HC-SR04
PIN_TRIGGER = 9
PIN_ECHO = 10

# NeoPixel integrado de la ESP32-S3 Mini (útil para ver los estados)
PIN_NEOPIXEL = 21

# --- PARÁMETROS ---
FRECUENCIA_PWM = 20000
DISTANCIA_ATAQUE_CM = 45
INTERVALO_ULTRASONICO_MS = 60

# Velocidades expresadas en porcentaje.
VELOCIDAD_BUSQUEDA = 100
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

trigger = Pin(PIN_TRIGGER, Pin.OUT, value=0)
echo = Pin(PIN_ECHO, Pin.IN)

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

# --- LECTURA DE SENSORES ---
def medir_distancia_cm():
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    duracion = time_pulse_us(echo, 1, 25000)

    if duracion < 0:
        return None

    return (duracion * 0.0343) / 2

# --- FUNCIONAMIENTO PRINCIPAL ---
def cambiar_estado(nuevo_estado):
    print("Estado:", NOMBRES_ESTADOS[nuevo_estado])
    return nuevo_estado

# Inicia directamente en estado de búsqueda al correr el programa
estado = BUSQUEDA
ultima_medicion = 0
distancia = None

detener()
set_color(0, 255, 0) # Led Verde = Buscando
print("Minisumo encendido: Modo de prueba (Solo Ultrasónico)")
print("Estado: BUSQUEDA")

try:
    while True:
        ahora = time.ticks_ms()

        if estado == BUSQUEDA:
            # El minisumo gira para barrer el dojo
            girar_derecha(VELOCIDAD_BUSQUEDA)

            if time.ticks_diff(ahora, ultima_medicion) >= INTERVALO_ULTRASONICO_MS:
                ultima_medicion = ahora
                distancia = medir_distancia_cm()

                if distancia is not None and distancia <= DISTANCIA_ATAQUE_CM:
                    print("Contrincante detectado: {:.1f} cm".format(distancia))
                    set_color(255, 0, 255) # Led Morado = Atacando
                    avanzar(VELOCIDAD_ATAQUE)
                    estado = cambiar_estado(ATAQUE)

        elif estado == ATAQUE:
            avanzar(VELOCIDAD_ATAQUE)

            if time.ticks_diff(ahora, ultima_medicion) >= INTERVALO_ULTRASONICO_MS:
                ultima_medicion = ahora
                distancia = medir_distancia_cm()

                # Si pierde de vista el objetivo, regresa a girar
                if distancia is None or distancia > DISTANCIA_ATAQUE_CM:
                    print("Contrincante perdido; regresando a busqueda")
                    set_color(0, 255, 0) 
                    girar_derecha(VELOCIDAD_BUSQUEDA)
                    estado = cambiar_estado(BUSQUEDA)

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