/*
  Proyecto: Sistema de Clasificación y Activación de Solenoides por Tipo de Tomate
  
  Created on Mon Oct 01 2024

  @author: Carlos Ordoñez 

  Descripción:
  Este programa utiliza un encoder para clasificar tomates según su tipo y activar solenoides
  en función de la posición registrada del encoder. El sistema se comunica con un dispositivo
  externo a través del puerto serial para recibir el tipo de tomate (0: verde, 1: tinto, 2: rojo).
  Dependiendo del tipo de tomate, el sistema registra la posición del encoder y activa el
  solenoide correspondiente cuando el tomate llega a una posición específica en la línea de clasificación.

  El programa incluye:
    - Control de un encoder para rastrear la posición en pulsos.
    - Almacenamiento y clasificación de tomates en tres tipos (verde, tinto y rojo).
    - Activación de solenoides según la posición del encoder y el tipo de tomate.
    - Desactivación de solenoides después de un tiempo de activación definido (100 ms).

  Hardware requerido:
    - Encoder conectado a los pines 2 y 3.
    - Tres solenoides conectados a los pines 5 (rojo), 8 (tinto), y 11 (verde).
    - Comunicación serial para recibir el tipo de tomate.

  Variables y Constantes:
    - `ENCODER_PIN_A`, `ENCODER_PIN_B`: Pines del encoder.
    - `SOLENOIDE_ROJO`, `SOLENOIDE_TINTO`, `SOLENOIDE_VERDE`: Pines de salida de los solenoides.
    - `DURACION_ACTIVACION`: Duración en milisegundos para mantener el solenoide activado.
    - `DISTANCIA_ROJO`, `DISTANCIA_TINTO`, `DISTANCIA_VERDE`: Distancias en pulsos del encoder para activar cada solenoide según el tipo de tomate.
    - `posicion_rojo`, `posicion_tinto`, `posicion_verde`: Arrays para almacenar las posiciones de cada tipo de tomate.

  Funciones principales:
    - `almacenarTomate(tipo, posicion)`: Almacena la posición del encoder cuando se recibe un tipo de tomate.
    - `revisarFilaRojo`, `revisarFilaTinto`, `revisarFilaVerde`: Verifica si el encoder ha alcanzado la posición para activar cada solenoide.
    - `manejarTiempoSolenoides`: Apaga los solenoides una vez que ha pasado el tiempo de activación.

  Ejecución:
    - El programa se ejecuta en un bucle infinito. Cada vez que el encoder registra un número suficiente de pulsos
      (definido en `TAMANO_POSICION`), verifica si hay un nuevo tipo de tomate en el puerto serial.
    - Si hay un tipo de tomate, lo registra en el array correspondiente y verifica si es necesario activar un solenoide.
    - Cuando un tomate llega a la distancia adecuada, el solenoide correspondiente se activa.
    - `manejarTiempoSolenoides` apaga los solenoides una vez que ha pasado el tiempo de activación.

  Nota:
    - Este código utiliza `millis()` para manejar tiempos sin bloquear el programa, permitiendo múltiples tareas
      sin interrupciones. La comunicación serial debe enviar datos con pausas para evitar sobrecarga en el buffer de Arduino.
*/

#include <Encoder.h>  // Librería para manejar el encoder

// Pines del encoder
#define ENCODER_PIN_A 2
#define ENCODER_PIN_B 3

// Pines de los solenoides
#define SOLENOIDE_ROJO 5
#define SOLENOIDE_TINTO 8
#define SOLENOIDE_VERDE 11

// Variables de control
long ultima_posicion_lectura = 0;
long previousPosition = 0; // Para mantener el conteo de los pulsos
unsigned long tiempoInicioRojos = 0; // Variable para almacenar el tiempo de activación del solenoide
unsigned long tiempoInicioTinto = 0; // Variable para almacenar el tiempo de activación del solenoide
unsigned long tiempoInicioVerde = 0; // Variable para almacenar el tiempo de activación del solenoide

// Estados de activación de los solenoides
bool solenoideRojoActivo = false;
bool solenoideTintoActivo = false;
bool solenoideVerdeActivo = false;

// Distancias de activación de solenoides
const int DISTANCIA_ROJO = 250;
const int DISTANCIA_TINTO = 500;
const int DISTANCIA_VERDE = 750;

// Posiciones de tomates en pulsos del encoder
const int TAMANO_POSICION = 100;

//Tiempo de activacion de solenoides
const int DURACION_ACTIVACION = 100;  // Duración de la activación en milisegundos

// Inicialización del encoder
Encoder encoder(ENCODER_PIN_A, ENCODER_PIN_B);

// Variables para almacenar las posiciones de tomates
const int FILA = 10;
long posicion_rojo[FILA], posicion_tinto[FILA], posicion_verde[FILA];
int indice_rojo = 0, indice_tinto = 0, indice_verde = 0;

void setup() {
  Serial.begin(9600);  // Comunicación serial
  pinMode(SOLENOIDE_ROJO, OUTPUT);
  pinMode(SOLENOIDE_TINTO, OUTPUT);
  pinMode(SOLENOIDE_VERDE, OUTPUT);
  encoder.write(0);  // Inicializar el encoder en 0
}

void loop() {
  // Obtener la posición actual del encoder
  long posicion_actual = encoder.read();

  // Mandar a consola el conteo de los pulsos
  conteoPulsos(posicion_actual);

  // Leer el tipo de tomate desde la comunicación serial si han pasado al menos 50 pulsos
  if (posicion_actual - ultima_posicion_lectura >= TAMANO_POSICION) {

    ultima_posicion_lectura = posicion_actual;
    Serial.println("ok");
    Serial.println("Inicia toma de datos");

    // Leer el tipo de tomate desde el serial
    if (Serial.available() > 0) {
      int tipo_tomate = Serial.parseInt();
      Serial.print("Tomate capturado: ");
      Serial.println(tipo_tomate);  // 'tipo' se imprimirá como un número
      Serial.print("En la posicion: ");
      Serial.println(posicion_actual);  // 'tipo' se imprimirá como un número

      /* Se guarda el tomate junto con su ubicacion en el momento que fueron 
      capturados de la forma '2 50' donde 2 es el tomate rojo y 50 el numero de pulsos del encoder en ese momento qque se 
      tomo la captura para indicar su poscion */
      almacenarTomate(tipo_tomate, posicion_actual); 
    }
  }

  // Activar solenoides según las posiciones de cada tipo de tomate
  revisarFilaVerde(posicion_actual);
  revisarFilaRojo(posicion_actual);
  revisarFilaTinto(posicion_actual);

  // Apagar solenoides si ha pasado el tiempo de activación
  manejarTiempoSolenoides();
}

void conteoPulsos(long posicion_actual){
  // Si la posición ha cambiado, se envia a través del puerto serie
  if (posicion_actual != previousPosition) {
    Serial.println(posicion_actual);
    previousPosition = posicion_actual;
  }
}

/* La fila circular (o cola circular) es una estructura de datos que permite reutilizar el 
espacio en un array cuando este llega al final de su capacidad, reiniciando la posición de 
almacenamiento desde el principio del array.

Cuando se detecta un nuevo tomate, se guarda su posición en el índice actual de la fila (array).
Aquí se utiliza el array posicion_ y el índice indice_ para almacenar la posición de cada tomate detectado.
Después de almacenar la posición, indice_ se incrementa en 1.

Si indice_ alcanza el límite de la fila (en este caso, 10), vuelve al principio de la fila 
gracias a la operación de módulo (%).

Esto significa que si indice_ es 9, al sumar 1 se obtiene 10, y 10 % 10 es 0, así que el índice vuelve a 0. 
De esta forma, el próximo dato se guarda en la primera posición del array. */

void almacenarTomate(int tipo, long posicion) {
  switch (tipo) {
    case 0:  // Verde
      posicion_verde[indice_verde] = posicion;
      indice_verde = (indice_verde + 1) % FILA; // Avanza el índice de forma circular
      Serial.print("Se guardo el tomate verde en: ");
      Serial.print(indice_verde);
      Serial.print(" ");
      Serial.println(posicion);
      break;
    case 1:  // Tinto
      posicion_tinto[indice_tinto] = posicion;
      indice_tinto = (indice_tinto + 1) % FILA; // Avanza el índice de forma circular
      Serial.print("Se guardo el tomate tinto en: ");
      Serial.print(indice_tinto);
      Serial.print(" ");
      Serial.println(posicion);
      break;
    case 2:  // Rojo
      posicion_rojo[indice_rojo] = posicion;
      indice_rojo = (indice_rojo + 1) % FILA;  // Avanza el índice de forma circular
      Serial.print("Se guardo el tomate rojo en: ");
      Serial.print(indice_rojo);
      Serial.print(" ");
      Serial.println(posicion);
      break;
  }
}

/*
  Función: revisarFilaX
  Propósito:
    Verificar la posición actual del encoder y activar el solenoide para los tomates Xs 
    cuando alcanzan la distancia específica para activación.

  Parámetros:
    - posicion_actual (long): La posición actual del encoder en pulsos.

  Descripción:
    Esta función recorre el array ‘posicion_X’, el cual almacena las posiciones de los tomates Xs
    detectados anteriormente. Para cada posición almacenada, verifica si el tomate ha avanzado 
    lo suficiente como para llegar a la posición de activación definida por ‘DISTANCIA_X’.
    
    - Si el tomate ha alcanzado o superado la posición de activación (calculada como ‘posicion_X[i] + DISTANCIA_X’), 
      la función:
        1. Activa el solenoide X (‘SOLENOIDE_X’) configurando su pin de salida en ‘HIGH’.
        2. Registra el tiempo de activación en la variable ‘tiempoInicioXs’ usando ‘millis()’ para realizar
           un control de duración en otra parte del programa.
        3. Cambia ‘solenoideXActivo’ a ‘true’, indicando que el solenoide está activo.
        4. Imprime en el Monitor Serial la posición del tomate en la que se activó el solenoide, 
           facilitando la depuración.
        5. Resetea el valor de ‘posicion_X[i]’ a 0, indicando que esa posición ya ha sido procesada 
           y evitando que el solenoide se active nuevamente para el mismo tomate.

  Nota:
    - ‘FILA’ es el tamaño del array ‘posicion_X’, definido para limitar la cantidad de posiciones que
      se pueden almacenar y procesar simultáneamente.
    - ‘DISTANCIA_X’ define la distancia en pulsos del encoder que un tomate debe recorrer desde la posición 
      en que fue registrado para que el solenoide X se active.

  Ejemplo de uso:
    Esta función se debe llamar desde el bucle principal (‘loop()’) pasando la posición actual del encoder 
    para verificar continuamente si algún tomate X ha alcanzado la distancia de activación.
*/

// Función para revisar y activar el solenoide de tomates rojos
void revisarFilaRojo(long posicion_actual) {
  for (int i = 0; i < FILA; i++) {
    if (posicion_rojo[i] > 0 && (posicion_actual >= posicion_rojo[i] + DISTANCIA_ROJO)) {
      digitalWrite(SOLENOIDE_ROJO, HIGH);
      tiempoInicioRojos = millis();
      solenoideRojoActivo = true;
      Serial.print("Se acciona el selenoide Rojo en: ");
      Serial.println(posicion_rojo[i]);
      posicion_rojo[i] = 0;  // Resetea la posición después de activación
    }
  }
}

// Función para revisar y activar el solenoide de tomates tintos
void revisarFilaTinto(long posicion_actual) {
  for (int i = 0; i < FILA; i++) {
    if (posicion_tinto[i] > 0 && (posicion_actual >= posicion_tinto[i] + DISTANCIA_TINTO)) {
      digitalWrite(SOLENOIDE_TINTO, HIGH);
      tiempoInicioTinto = millis();
      solenoideTintoActivo = true;
      Serial.print("Se acciona el selenoide Tinto en: ");
      Serial.println(posicion_tinto[i]);
      posicion_tinto[i] = 0;
    }
  }
}

// Función para revisar y activar el solenoide de tomates verdes
void revisarFilaVerde(long posicion_actual) {
  for (int i = 0; i < FILA; i++) {
    if (posicion_verde[i] > 0 && (posicion_actual >= posicion_verde[i] + DISTANCIA_VERDE)) {
      digitalWrite(SOLENOIDE_VERDE, HIGH);
      tiempoInicioVerde = millis();
      solenoideVerdeActivo = true;
      Serial.print("Se acciona el selenoide Verde en: ");
      Serial.println(posicion_verde[i]);
      posicion_verde[i] = 0;
    }
  }
}

// Apaga los solenoides si han estado activos más de la duración especificada
void manejarTiempoSolenoides() {
  unsigned long tiempoActual = millis();

  if (solenoideRojoActivo && (tiempoActual - tiempoInicioRojos >= DURACION_ACTIVACION)) {
    digitalWrite(SOLENOIDE_ROJO, LOW);
    solenoideRojoActivo = false;
  }
  
  if (solenoideTintoActivo && (tiempoActual - tiempoInicioTinto >= DURACION_ACTIVACION)) {
    digitalWrite(SOLENOIDE_TINTO, LOW);
    solenoideTintoActivo = false;
  }

  if (solenoideVerdeActivo && (tiempoActual - tiempoInicioVerde >= DURACION_ACTIVACION)) {
    digitalWrite(SOLENOIDE_VERDE, LOW);
    solenoideVerdeActivo = false;
  }
}

