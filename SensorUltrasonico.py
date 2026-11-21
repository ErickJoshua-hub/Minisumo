from machine import Pin, time_pulse_us
import time

# Configurar los pines correspondientes al ESP32-S3 Zero
trig = Pin(1, Pin.OUT)
echo = Pin(2, Pin.IN)

while True:
    # Asegurar que el pin TRIG esté en bajo
    trig.value(0)
    time.sleep_us(2)
    
    # Enviar un pulso de 10 microsegundos
    trig.value(1)
    time.sleep_us(10)
    trig.value(0)
    
    # Leer el tiempo que tarda el pulso en volver (timeout de 30ms)
    try:
        duracion = time_pulse_us(echo, 1, 30000)
        
        if duracion > 0:
            # Convertir el tiempo en distancia (cm)
            distancia = (duracion * 0.0343) / 2
            print("Distancia: {:.1f} cm".format(distancia))
        else:
            print("Distancia: Fuera de rango")
            
    except OSError:
        print("Error de lectura o sin respuesta del sensor")
        
    # Esperar 200 milisegundos antes de la siguiente medición
    time.sleep_ms(200)