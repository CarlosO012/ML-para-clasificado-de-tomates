# -*- coding: utf-8 -*-

""" Script de Detección de Colores en Imágenes

Este script permite identificar y calcular el porcentaje de áreas con colores específicos
(rojo, verde, amarillo) en una imagen. Para ello, crea máscaras en el espacio de color HSV,
aplica la máscara a la imagen y calcula el área en píxeles de cada color para obtener un
porcentaje. Finalmente, visualiza las áreas de cada color mediante matplotlib.

Requisitos:
-----------
- OpenCV
- NumPy
- Matplotlib

Entradas:
- Una imagen cargada desde el disco.

Salidas:
- Porcentajes de área para cada color especificado.
- Visualización de las máscaras y áreas coloreadas.

Created on Mon Oct 01 2024

@author: Carlos Ordoñez """

import cv2
import numpy as np
import matplotlib.pyplot as plt

def crear_mascara_de_color(image, suave_color, alto_color):
    """ Crea una máscara para un rango de color especificado en una imagen dada.

    Parámetros:
    - image (numpy.ndarray): La imagen en la cual se buscará el rango de color.
    - suave_color (numpy.ndarray): Color inferior en el rango HSV.
    - alto_color (numpy.ndarray): Color superior en el rango HSV.

    Retorna:
    - numpy.ndarray: Máscara binaria donde los píxeles en el rango especificado son blancos (255) 
    y los demás son negros (0). """
    cuadro_en_HSV = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)  # Convertir la imagen de BGR a HSV
    mascara = cv2.inRange(cuadro_en_HSV, suave_color, alto_color)  # Crear la máscara para el rango
    return mascara

def aplicacion_de_mascara(image, mascara, color):
    """ Aplica una máscara a la imagen y colorea el área enmascarada con el color dado.

    Parámetros:
    - image (numpy.ndarray): La imagen original en la que se aplicará la máscara.
    - mascara (numpy.ndarray): La máscara binaria.
    - color (list): Color en formato RGB para aplicar en las áreas de la máscara.

    Retorna:
    - numpy.ndarray: Imagen donde el área de la máscara se ha coloreado con el color especificado. """
    coloreado_mascara = cv2.bitwise_and(image, image, mask=mascara)  # Aplicar la máscara
    coloreado_mascara[mascara > 0] = color  # Asignar color a las áreas enmascaradas
    return coloreado_mascara

def calculo_porcentaje_de_color(mascara, total_area):
    """ Calcula el porcentaje de área de un color específico en la imagen.

    Parámetros:
    - mascara (numpy.ndarray): Máscara binaria que representa el área del color.
    - total_area (int): Área total de la imagen en píxeles.

    Retorna:
    - float: Porcentaje del área de la imagen cubierta por el color. """
    area = np.sum(mascara == 255)  # Cuenta los píxeles blancos en la máscara
    return (area / total_area) * 100  # Calcula el porcentaje

def main():
    """ Función principal que ejecuta el proceso de detección de colores.

    Carga una imagen, define los rangos de colores, crea las máscaras para cada color,
    aplica las máscaras a la imagen, calcula el porcentaje de área para cada color y
    visualiza los resultados mediante subplots. """
    # Cargar la imagen desde el disco
    image = cv2.imread('D:/Documentos/Python/Proyectos/Workspaces/DatasetSuper/PruebasImg/Muestra167_3_jpg.rf.4fd529a06dee9e5bc2b7fc74b3eaef0a.jpg')
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)  # Convertir a RGB para visualización
    total_area = image.shape[0] * image.shape[1]  # Calcular el área total en píxeles

    # Definir rangos de colores en el espacio HSV
    suave_rojo_bajo = np.array([0, 50, 50])
    alto_rojo_bajo = np.array([10, 255, 255])
    suave_rojo_alto = np.array([120, 50, 50])
    alto_rojo_alto = np.array([180, 255, 255])
    suave_verde = np.array([34, 50, 50])
    alto_verde = np.array([90, 255, 255])
    suave_amarillo = np.array([11, 50, 50])
    alto_amarillo = np.array([33, 255, 255])

    # Crear máscaras de color para cada rango definido
    rojo_bajo_mascara = crear_mascara_de_color(image, suave_rojo_bajo, alto_rojo_bajo)
    rojo_alto_mascara = crear_mascara_de_color(image, suave_rojo_alto, alto_rojo_alto)
    verde_mascara = crear_mascara_de_color(image, suave_verde, alto_verde)
    amarillo_mascara = crear_mascara_de_color(image, suave_amarillo, alto_amarillo)

    # Aplicar las máscaras a la imagen y colorear las áreas
    rojo_coloreado_bajo = aplicacion_de_mascara(image_rgb, rojo_bajo_mascara, [255, 0, 0])
    rojo_coloreado_alto = aplicacion_de_mascara(image_rgb, rojo_alto_mascara, [255, 0, 0])
    verde_coloreado = aplicacion_de_mascara(image_rgb, verde_mascara, [0, 255, 0])
    amarillo_coloreado = aplicacion_de_mascara(image_rgb, amarillo_mascara, [255, 255, 0])

    # Calcular el porcentaje de área cubierta por cada color
    rojo_porciento_bajo = calculo_porcentaje_de_color(rojo_bajo_mascara, total_area)
    rojo_porciento_alto = calculo_porcentaje_de_color(rojo_alto_mascara, total_area)
    verde_porciento = calculo_porcentaje_de_color(verde_mascara, total_area)
    amarillo_porciento = calculo_porcentaje_de_color(amarillo_mascara, total_area)

    # Imprimir los porcentajes de cada color
    print(f'rojo bajo: {rojo_porciento_bajo:.2f}%')
    print(f'rojo alto: {rojo_porciento_alto:.2f}%')
    print(f'verde: {verde_porciento:.2f}%')
    print(f'amarillo: {amarillo_porciento:.2f}%')

    # Configuración de visualización para mostrar las máscaras y áreas coloreadas
    fig, axs = plt.subplots(4, 2, figsize=(10, 15))

    # Mostrar cada máscara y su correspondiente imagen coloreada en el subplot
    axs[0, 0].imshow(rojo_bajo_mascara, cmap='gray')
    axs[0, 0].set_title('rojo bajo mascara')
    axs[0, 0].axis('off')

    axs[0, 1].imshow(rojo_coloreado_bajo)
    axs[0, 1].set_title('rojo bajo coloreado')
    axs[0, 1].axis('off')

    axs[1, 0].imshow(rojo_alto_mascara, cmap='gray')
    axs[1, 0].set_title('rojo alto mascara')
    axs[1, 0].axis('off')

    axs[1, 1].imshow(rojo_coloreado_alto)
    axs[1, 1].set_title('rojo alto coloreado')
    axs[1, 1].axis('off')

    axs[2, 0].imshow(amarillo_mascara, cmap='gray')
    axs[2, 0].set_title('amarillo mascara')
    axs[2, 0].axis('off')

    axs[2, 1].imshow(amarillo_coloreado)
    axs[2, 1].set_title('amarillo coloreado')
    axs[2, 1].axis('off')

    axs[3, 0].imshow(verde_mascara, cmap='gray')
    axs[3, 0].set_title('verde mascara')
    axs[3, 0].axis('off')

    axs[3, 1].imshow(verde_coloreado)
    axs[3, 1].set_title('verde coloreado')
    axs[3, 1].axis('off')

    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    main()
