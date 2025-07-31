# Mecanismo de Seguimiento Solar de dos Grados de Libertad con Visualización en Tiempo Real de la Aproximación de la Radiación Solar Global y Directa
Este proyecto consiste en un mecanismo de dos grados de libertad con interfaz gráfica desarrollada en Python. Fue diseñado e implementado en el Trabajo Terminal "Mecanismo de Seguimiento Solar de Dos Grados de Libertad" para obtener el título de Ingeniería Mecatrónica del Instituto Politécnico Nacional.
<img width="476" height="695" alt="image" src="https://github.com/user-attachments/assets/322d3d1c-2609-402d-bde2-145f2fc741da" />


## Autores
- Manriquez Chavez Yasser Aben-Amar
- Ochoa Garcia Jesus
- Toledo Lopez Israel

## Objetivo
Diseñar y construir un mecanismo de dos grados de libertad que realice el seguimiento de trayectoria solar, mediante el cambio de posición de los ángulos de azimut e inclinación, con capacidad de adaptar diferentes tipos de colectores solares; además de estimar la radiación solar global y directa mediante el uso de un pirheliómetro y un piranómetro, respectivamente.

## Características
- Interfaz gráfica en Python para mostrar:
  - Radiación global y directa
  - Angulo de inclinación y rotación del mecanismo
- Lectura de sensores y control del movimiento del mecanismo con Arduino

## Tecnologías
- Python (PyQT5 / Matplotlib)
- Arduino + Biblioteca para el MPU9250
- Sensores de Radiación
  - Radiómetro solar de onda corta RY-EBN-1
  - Piranómetro apogee
- Giroscopio MPU9250

