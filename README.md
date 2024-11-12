# Sistema de Clasificación Automática de Tomates

Este proyecto tiene como objetivo diseñar e implementar un sistema automatizado para la clasificación de tomates utilizando redes neuronales y visión artificial. El sistema está destinado a mejorar la eficiencia en el proceso de clasificación. El proyecto emplea un enfoque de **aprendizaje automático**, utilizando una red neuronal convolucional (CNN) para clasificar los tomates en diferentes categorías, basadas en características como color, tamaño y madurez.

## Objetivos

- **Objetivo general**: Desarrollar un sistema automatizado para la clasificación de tomates utilizando redes neuronales y visión artificial.
- **Objetivos específicos**:
  1. Desarrollar una red neuronal convolucional (CNN) para clasificar los tomates en distintas categorías.
  2. Seleccionar e implementar un sistema de actuadores para el manejo de los tomates clasificados.
  3. Diseñar un sistema eléctrico para controlar de manera sincronizada los actuadores con el sistema de visión artificial y la red neuronal.

## Tecnologías Utilizadas

- **Lenguaje de programación**: Python
- **Framework de aprendizaje automático**: TensorFlow, Keras
- **Visión artificial**: OpenCV
- **Plataforma de hardware**: Arduino
- **Sistema de actuadores**: Solenoides y otros actuadores para clasificación física
- **Control**: Comunicación entre el sistema de visión y el actuador usando un controlador Arduino.

## Cómo Funciona el Sistema

El sistema consta de varias etapas:
1. **Captura de imágenes**: Una cámara captura imágenes de los tomates en la línea de producción.
2. **Procesamiento de imágenes**: Utilizando OpenCV, las imágenes se procesan para extraer características como color y forma.
3. **Clasificación con redes neuronales**: Las características extraídas se alimentan a una red neuronal entrenada para clasificar los tomates en diferentes categorías.
4. **Actuadores**: Los tomates clasificados son manipulados por actuadores controlados por un Arduino, que organiza los tomates según su categoría.

## Instrucciones de Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/CarlosO012/ML-para-clasificado-de-tomates.git

