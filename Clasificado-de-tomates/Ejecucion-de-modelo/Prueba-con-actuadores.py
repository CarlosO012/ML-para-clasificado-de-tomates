# -*- coding: utf-8 -*-

''' Script de clasificación y detección de tomates en tiempo real.

Este script captura video desde una cámara, utiliza un modelo de aprendizaje profundo
para detectar y clasificar tomates, y envía los resultados a un Arduino para la
activación de solenoides. La predicción se realiza mediante un modelo entrenado
con Keras y se muestran los resultados en el video en vivo.

Requisitos:
- OpenCV
- TensorFlow/Keras
- NumPy
- PySerial

Entradas:
- Video de una cámara en tiempo real.
- Datos seriales de un encoder desde Arduino.

Salidas:
- Visualización del video con cuadros delimitadores y etiquetas de clasificación.
- Envío de la clase detectada al Arduino a través de un puerto serial.

Created on Mon Oct 01 2024

@author: Carlos Ordoñez '''

import cv2
import time
import serial
import numpy as np
from collections import deque
from tensorflow.keras.models import load_model
import threading  # Para manejar la recepción de datos en un hilo separado

# Cargar el modelo entrenado de clasificación de tomates
model = load_model('D:/Clasificadora/Code/Proyectos/Workspaces/TomatoClass.keras')

# Inicializar la captura de video desde la cámara principal del sistema
cap = cv2.VideoCapture(0)

# Inicializar la conexión serial con el Arduino en el puerto COM6
ser = serial.Serial('COM6', 9600, timeout=1)  # Ajusta el puerto según sea necesario
time.sleep(2)  # Espera 2 segundos para asegurar que la conexión se establezca

# Configuración de las colas para almacenar las últimas cinco predicciones
coincidencia_maxima = 5    # Número máximo de predicciones almacenadas
coincidencia_minima = 4    # Número mínimo de coincidencias necesarias para una predicción válida
fila_predicciones = deque(maxlen=coincidencia_maxima)  # Cola para predicciones de clase
fila_confianza = deque(maxlen=coincidencia_maxima)   # Cola para niveles de confianza
fila_de_tiempos = deque(maxlen=coincidencia_maxima)        # Cola para tiempos de predicción
mandar_confirmacion = False  # Flag para controlar el envío de datos

def lectura_de_arduino():
    ''' Función que lee datos desde el puerto serial del Arduino de forma continua en un hilo separado.
    Este hilo permite recibir datos del encoder en tiempo real sin interrumpir el flujo principal.
    Imprime en consola los mensajes recibidos del Arduino. '''
    global mandar_confirmacion
    while True:
        if ser.in_waiting > 0:  # Verifica si hay datos disponibles en el puerto serial
            line = ser.readline().decode('utf-8', errors='ignore').strip()  # Lee y decodifica la línea
            print('Mensaje del Arduino:', line)  # Imprime el mensaje del Arduino en la consola
            if line == 'ok':
                mandar_confirmacion = True  # Arduino está listo para recibir datos

# Crear e iniciar el hilo de lectura del Arduino
arduino_thread = threading.Thread(target=lectura_de_arduino)
arduino_thread.daemon = True  # Esto asegura que el hilo termine cuando el script principal termine
arduino_thread.start()  # Inicia el hilo de lectura del Arduino

while True:
    # Captura un frame de la cámara
    ret, frame = cap.read()
    if not ret:  # Si no se pudo capturar el frame, sale del bucle
        break

    start_time = time.time()  # Inicia el temporizador para medir el tiempo de predicción

    # Preprocesamiento de la imagen antes de pasarla al modelo
    input_img = cv2.resize(frame, (224, 224))  # Redimensiona la imagen al tamaño de entrada del modelo
    input_img = input_img.astype(np.float32) / 255.0  # Normaliza los valores de los píxeles entre 0 y 1
    input_img = np.expand_dims(input_img, axis=0)  # Añade una dimensión extra para formar un batch

    # Realizar la predicción usando el modelo cargado
    predictions = model.predict(input_img)

    # Medir el tiempo después de la predicción
    end_time = time.time()
    prediction_time = end_time - start_time  # Calcula el tiempo total de predicción

    # Extrae la clase predicha y los valores del bounding box
    prediccion_de_clase = np.argmax(predictions[0][0])  # Índice de la clase con mayor probabilidad
    prediccion_de_confianza = np.max(predictions[0][0])  # Confianza de la clase predicha
    prediccion_de_bboxes = predictions[1][0]  # Coordenadas normalizadas del bounding box

    # Desnormalizar las coordenadas del bounding box al tamaño real de la imagen
    height, width, _ = frame.shape
    xmin = int(prediccion_de_bboxes[0] * width)
    ymin = int(prediccion_de_bboxes[1] * height)
    xmax = int(prediccion_de_bboxes[2] * width)
    ymax = int(prediccion_de_bboxes[3] * height)

    # Guardar las últimas predicciones en las colas
    fila_predicciones.append(prediccion_de_clase)
    fila_confianza.append(prediccion_de_confianza)
    fila_de_tiempos.append(prediction_time)

    # Analizar las últimas cinco predicciones para determinar si se confirma una clase
    if len(fila_predicciones) == coincidencia_maxima:
        # Encuentra la clase más común en las últimas predicciones
        clase_mas_comun = max(set(fila_predicciones), key=fila_predicciones.count)
        recuento_clase_mas_comun = fila_predicciones.count(clase_mas_comun)

        # Si la clase más común aparece al menos coincidencia_minima veces, se considera válida
        if recuento_clase_mas_comun >= coincidencia_minima:
            # Calcula la confianza y el tiempo promedio de las predicciones coincidentes
            promedio_confidence = np.mean([conf for cls, conf in zip(fila_predicciones, fila_confianza) if cls == clase_mas_comun])
            promedio_time = np.mean(fila_de_tiempos)
            mensaje_prediccion = f'Detectado: Tomate {clase_mas_comun}, Confianza promedio: {promedio_confidence:.2f}, Tiempo promedio: {promedio_time:.2f}s'
            print(f'El tipo de tomate es: {clase_mas_comun}')
            # Solo envía datos si se recibió la confirmación "ok" de Arduino
            if mandar_confirmacion:
                ser.write((str(clase_mas_comun) + '\n').encode())  # Enviar la clase predicha al Arduino
                mandar_confirmacion = False  # Restablece el permiso hasta recibir el próximo "ok"
        else:
            # Si la predicción no es confiable, envía un mensaje para "no identificado"
            mensaje = 'No se identificó correctamente'
            print('No reconocido')
            if mandar_confirmacion:
                ser.write('3'.encode())  # Enviar '3' para indicar "no identificado"
                mandar_confirmacion = False

        # Escribe el mensaje de predicción en el frame
        cv2.putText(frame, mensaje_prediccion, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Dibujar el bounding box y mostrar la etiqueta de clase en el frame
    cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
    label = f'Tomate: {prediccion_de_clase}, Conf: {prediccion_de_confianza:.2f}'
    cv2.putText(frame, label, (xmin, ymin - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Mostrar el frame con el cuadro delimitador y la etiqueta en la ventana
    cv2.imshow('Deteccion de Tomates', frame)

    # Presionar ESC para salir
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Liberar la cámara y cerrar todas las ventanas al finalizar
cap.release()
cv2.destroyAllWindows()
ser.close()
