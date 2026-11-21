# Robot Mini-Sumo Autónomo

Robot de competición diseñado para la categoría Mini-Sumo a nivel federal. El proyecto combina diseño electrónico, programación de bajo nivel y estrategias algorítmicas de búsqueda y ataque para la detección y neutralización de oponentes en el dohyo.

## Hardware y Sensores
*   **Microcontrolador: ESP32 S3 zero mini.
*   **Detección de Oponente: Sensores ultrasónicos y de laser para detectar al rival   
*   **Detección de Borde: Sensores infrarrojos para evitar la salida del ring.
*   **Locomoción: Motores de alta tracción controlados mediante PWM (motores n20 de 300rpm).

## Estrategia de Software (Python / MicroPython)
El código está estructurado en módulos para manejar cada subsistema (`Infrarojo.py`, `SensorUltrasonico.py`, `motor.py`) e integra la siguiente lógica de combate:
*   **Rutina de Búsqueda:** Patrones de movimiento optimizados (barridos rápidos) para localizar al oponente antes de ser detectado.
*   **Lógica de Evasión/Ataque:** Toma de decisiones en milisegundos para priorizar el ataque frontal o la evasión de bordes basados en interrupciones de los sensores.

*Todo fue programado en MicroPython, de esta forma se asegura que el robot pueda trabajar de forma adecuada, además es el esfuerzo de meses de programación y lógica para perfeccionarlo cada vez mas 
