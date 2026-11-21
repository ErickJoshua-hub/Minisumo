from machine import Pin, PWM, time_pulse_us
import time
import neopixel

# Motor A: lado izquierdo
PIN_MOTOR_A1 = 5
PIN_MOTOR_A2 = 6

# Motor B: lado derecho
PIN_MOTOR_B1 = 7
PIN_MOTOR_B2 = 8

# Sensor infrarrojo de borde
PIN_IR = 3

# Sensor ultrasonico HC-SR04
PIN_TRIGGER = 9
PIN_ECHO = 10

# Receptor de inicio: solamente funciona la salida READY.
# GPIO 12 queda libre para una ampliacion futura del GO
PIN_INICIO = 11
#PIN_INICIOGO = 12

# NeoPixel integrado de la ESP32-S3 Mini
PIN_NEOPIXEL = 21

# parámetro para ajustar

FRECUENCIA_PWM = 20000

# En el sensor: 0 = blanco y 1 = negro.
VALOR_BLANCO = 0

# Distancia maxima para considerar que hay un contrincante.
DISTANCIA_ATAQUE_CM = 45

# Tiempo entre mediciones del HC-SR04.
INTERVALO_ULTRASONICO_MS = 60

# Duraciones de la maniobra para escapar del borde.
TIEMPO_REVERSA_MIN_MS = 180
TIEMPO_REVERSA_MAX_MS = 500
TIEMPO_GIRO_ESCAPE_MS = 320

# Velocidades expresadas en porcentaje.
VELOCIDAD_BUSQUEDA = 55
VELOCIDAD_ATAQUE = 100
VELOCIDAD_REVERSA = 90
VELOCIDAD_GIRO_ESCAPE = 80

# ESTADOS DEL AUTOMATA
ESPERA = 0
BUSQUEDA = 1
ATAQUE = 2
ESCAPE_REVERSA = 3
ESCAPE_GIRO = 4

NOMBRES_ESTADOS = (
    "ESPERA",
    "BUSQUEDA",
    "ATAQUE",
    "ESCAPE_REVERSA",
    "ESCAPE_GIRO",
)

# configuración de los componentes de harware del minisumo
motor_a_1 = PWM(Pin(PIN_MOTOR_A1), freq=FRECUENCIA_PWM)
motor_a_2 = PWM(Pin(PIN_MOTOR_A2), freq=FRECUENCIA_PWM)
motor_b_1 = PWM(Pin(PIN_MOTOR_B1), freq=FRECUENCIA_PWM)
motor_b_2 = PWM(Pin(PIN_MOTOR_B2), freq=FRECUENCIA_PWM)

sensor_ir = Pin(PIN_IR, Pin.IN)

trigger = Pin(PIN_TRIGGER, Pin.OUT, value=0)
echo = Pin(PIN_ECHO, Pin.IN)

# Se usa una resistencia interna para que la entrada no quede flotando.
# Cuando RDY entrega un pulso con valor 1, comienza la secuencia de combate.
receptor_inicio = Pin(PIN_INICIO, Pin.IN, Pin.PULL_DOWN)

led = neopixel.NeoPixel(Pin(PIN_NEOPIXEL), 1)

def set_color(rojo, verde, azul):
    led[0] = (rojo, verde, azul)
    led.write()

# control de los motores

def convertir_velocidad(velocidad):
    #Convierte un porcentaje de 0 a 100 en PWM de 0 a 65535
    velocidad = max(0, min(100, velocidad))
    return int(velocidad * 655.35)

def mover_motor_a(velocidad):
    #Mueve el motor A entre -100 y 100
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
    #Mueve el motor B entre -100 y 100
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


def retroceder(velocidad):
    mover_motores(-velocidad, -velocidad)


def girar_izquierda(velocidad):
    mover_motores(-velocidad, velocidad)


def girar_derecha(velocidad):
    mover_motores(velocidad, -velocidad)

# lectura de los sensores

def borde_blanco_detectado():
    #Devuelve True cuando el infrarrojo detecta la franja blanca
    return sensor_ir.value() == VALOR_BLANCO


def medir_distancia_cm():
    #Mide distancia con el HC-SR04; devuelve None si no recibe eco
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    duracion = time_pulse_us(echo, 1, 25000)

    if duracion < 0:
        return None

    return (duracion * 0.0343) / 2

# recepción del pulso ready

# La interrupcion permite conservar un pulso corto aunque el programa
# se encuentre midiendo la distancia en ese momento.
pulso_inicio = False


def interrupcion_inicio(pin):
    global pulso_inicio
    pulso_inicio = True


receptor_inicio.irq(trigger=Pin.IRQ_RISING, handler=interrupcion_inicio)


# funcionamiento del autómata

def cambiar_estado(nuevo_estado):
    print("Estado:", NOMBRES_ESTADOS[nuevo_estado])
    return nuevo_estado

def comenzar_escape(ahora, giro_siguiente):
    #Inicia la primera fase de escape: retroceder
    detener()
    time.sleep_ms(20)
    retroceder(VELOCIDAD_REVERSA)
    set_color(255, 0, 0)
    inicio = time.ticks_ms()
    limite = time.ticks_add(inicio, TIEMPO_REVERSA_MAX_MS)
    return cambiar_estado(ESCAPE_REVERSA), inicio, limite, giro_siguiente

# funcionamiento principal

estado = ESPERA
inicio_estado = 0
limite_estado = 0
ultima_medicion = 0
distancia = None

# Al existir solamente un sensor de borde, se alterna el sentido de escape.
giro_escape_derecha = True

detener()
set_color(255, 0, 0)

print("Minisumo encendido")
print("Esperando pulso de inicio RDY en GPIO 11...")


try:
    while True:
        ahora = time.ticks_ms()

        # Un pulso RDY con valor 1 inicia inmediatamente el combate.
        if pulso_inicio and estado == ESPERA:
            pulso_inicio = False
            set_color(0, 255, 0)
            girar_derecha(VELOCIDAD_BUSQUEDA)
            ultima_medicion = time.ticks_add(
                ahora,
                -INTERVALO_ULTRASONICO_MS,
            )
            estado = cambiar_estado(BUSQUEDA)
        elif pulso_inicio:
            pulso_inicio = False

        # Seguridad principal: el borde tiene prioridad durante el combate.
        if estado in (BUSQUEDA, ATAQUE, ESCAPE_GIRO) and borde_blanco_detectado():
            estado, inicio_estado, limite_estado, giro_escape_derecha = comenzar_escape(
                ahora,
                giro_escape_derecha,
            )

        elif estado == ESPERA:
            detener()

        elif estado == BUSQUEDA:
            # El minisumo gira para barrer el dojo con el HC-SR04.
            girar_derecha(VELOCIDAD_BUSQUEDA)

            if time.ticks_diff(ahora, ultima_medicion) >= INTERVALO_ULTRASONICO_MS:
                ultima_medicion = ahora
                distancia = medir_distancia_cm()

                if distancia is not None and distancia <= DISTANCIA_ATAQUE_CM:
                    print("Contrincante detectado: {:.1f} cm".format(distancia))
                    set_color(255, 0, 255)
                    avanzar(VELOCIDAD_ATAQUE)
                    estado = cambiar_estado(ATAQUE)

        elif estado == ATAQUE:
            avanzar(VELOCIDAD_ATAQUE)

            if time.ticks_diff(ahora, ultima_medicion) >= INTERVALO_ULTRASONICO_MS:
                ultima_medicion = ahora
                distancia = medir_distancia_cm()

                if distancia is None or distancia > DISTANCIA_ATAQUE_CM:
                    print("Contrincante perdido; regresando a busqueda")
                    set_color(0, 255, 0)
                    girar_derecha(VELOCIDAD_BUSQUEDA)
                    estado = cambiar_estado(BUSQUEDA)

        elif estado == ESCAPE_REVERSA:
            # Sigue retrocediendo hasta regresar al negro. El tiempo minimo
            # evita detener la maniobra por una lectura inestable del sensor.
            tiempo_retroceso = time.ticks_diff(ahora, inicio_estado)
            regreso_al_negro = not borde_blanco_detectado()
            termino_tiempo_maximo = time.ticks_diff(ahora, limite_estado) >= 0

            if (
                regreso_al_negro and tiempo_retroceso >= TIEMPO_REVERSA_MIN_MS
            ) or termino_tiempo_maximo:
                if giro_escape_derecha:
                    girar_derecha(VELOCIDAD_GIRO_ESCAPE)
                else:
                    girar_izquierda(VELOCIDAD_GIRO_ESCAPE)

                limite_estado = time.ticks_add(ahora, TIEMPO_GIRO_ESCAPE_MS)
                estado = cambiar_estado(ESCAPE_GIRO)

        elif estado == ESCAPE_GIRO:
            if time.ticks_diff(ahora, limite_estado) >= 0:
                giro_escape_derecha = not giro_escape_derecha
                set_color(0, 255, 0)
                girar_derecha(VELOCIDAD_BUSQUEDA)
                ultima_medicion = time.ticks_add(
                    ahora,
                    -INTERVALO_ULTRASONICO_MS,
                )
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
