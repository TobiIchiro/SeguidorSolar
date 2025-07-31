# Mecanismo de Seguimiento Solar de dos Grados de Libertad con Visualización en Tiempo Real de la Aproximación de la Radiación Solar Global y Directa
Este proyecto consiste en un mecanismo de dos grados de libertad con interfaz gráfica desarrollada en Python. Fue diseñado e implementado en el Trabajo Terminal "Mecanismo de Seguimiento Solar de Dos Grados de Libertad" para obtener el título de Ingeniería Mecatrónica del Instituto Politécnico Nacional.<br/>
<p align="center">
  <img width="238" height="347" alt="image" src="https://github.com/user-attachments/assets/322d3d1c-2609-402d-bde2-145f2fc741da" />
</p>

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

## Capturad de Pantalla de la interfaz
<img width="735" height="388" alt="image" src="https://github.com/user-attachments/assets/73346818-ebcf-491b-8064-8779a30fc68b" />
<img width="736" height="389" alt="image" src="https://github.com/user-attachments/assets/3e6782e3-ecc9-4cee-b489-4f4bcb2363cc" />
<img width="743" height="392" alt="image" src="https://github.com/user-attachments/assets/b3b98444-44c9-46c7-aaf6-7b5f432d2d1b" />
<img width="762" height="403" alt="image" src="https://github.com/user-attachments/assets/ec7da3a7-7a64-4d8d-9460-efdaf75db42f" />

## Gráficas
### Radiación Solar Global estimada
<img width="501" height="331" alt="image" src="https://github.com/user-attachments/assets/b06971e0-9100-4f3f-ba72-e38533cb0ff1" /><br/>
### Radiación Solar Directa estimada
<img width="568" height="458" alt="image" src="https://github.com/user-attachments/assets/d386941c-ff69-40ed-8bf2-75f502170d00" />





