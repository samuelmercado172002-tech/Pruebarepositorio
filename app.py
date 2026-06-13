
# ASISTENTE INTELIGENTE - VERSION 2
# Autor: Hilder Olivas
# Mejoras: Documentación completa y organizador expandido
#
# Funciones:
# - Reconocimiento de voz
# - Voz natural con Edge-TTS
# - Registro de nombre
# - Conversación básica
# - Historial en pantalla
# - Organizador de archivos avanzado

from flask import Flask, render_template, request

# las importaciones de bibliotecas usadas 
# reconocedor de voz - speech recognition as sr 
# su funcion es convertir el audio a tecto
import speech_recognition as sr

# Hilos los hilos permite ejecutar varias tareas constantemente
import threading

# estas se encargan de la voz natural  
import asyncio
import edge_tts
# esta se encarga de reproducir el audio del archivo mp3
import pygame
# esta es accede al sistema operativo y es la que 
# maneja las rutas y archivos
import os

# inventigando esta es la que maneja archivos y 
#tambiem mueve archvos
import shutil

# esta es la que hace el manejo de las rutas 
from pathlib import Path

# las nuevas importaciones 
# Librería OpenCV
# Se utiliza para acceder a la cámara web,
# procesar imágenes y detectar rostros.
import cv2
# Librería para redimensionar imágenes y video
# Facilita ajustar el tamaño de los fotogramas
# capturados por la cámara.
import imutils

# =====================================================
# creacion de la aplicacion Flask
# =====================================================

app = Flask(__name__)

# =====================================================
# VARIABLES GLOBALES
# =====================================================

# almacena el nombre del usuario registrado
nombre_usuario = ""

# esta es la lista que almacena el historial de conversaciones
# Formato: [{"usuario": "texto", "respuesta": "texto"}, ...]
conversacion = []

# la nueva variable para capturar el rostro
capturando_rostros = False

# =====================================================
# FUNCION DE VOZ NATURAL
# =====================================================
# Esta función genera un archivo de audio MP3 temporal con una voz natural
# Utiliza edge_tts servicio de texto a voz de Microsoft

async def generar_voz(texto):
   
 
    archivo = "voz.mp3"

    # Crear comunicación de texto a voz
    comunicacion = edge_tts.Communicate(
        texto,
       voice="es-MX-JorgeNeural" # esta es la voz que se reproducera el audio 
       # se puede cambiar 
    )

    #aca esta guardar el audio como archivo MP3
    await comunicacion.save(archivo)

    # esta se encarga de inicializar el mixer de
    # # pygame para reproducción de audio
    pygame.mixer.init()

    # Cargar el archivo MP3
    pygame.mixer.music.load(archivo)

    # reproducir el audio
    pygame.mixer.music.play()

    # essperar hasta que termine la reproducción
    while pygame.mixer.music.get_busy():
        continue

    # cerrar el mixer
    pygame.mixer.quit()

    #y aca elimina el archivo temporal 
    if os.path.exists(archivo):
        os.remove(archivo)

# =====================================================
# funcion de hablar sincronica
# =====================================================
# sta función ejecuta la generación de voz de forma síncrona es decir que 
# espera a que termine antes de continuar

def hablar(texto):
    
    asyncio.run(generar_voz(texto))

# =====================================================
# funcion de hablar en segundo plano 
# =====================================================
# esta función ejecuta la generación de voz en un hilo separado
# para que no bloquee el resto de la app

def hablar_async(texto):
    """
    ejecuta la generación de voz en un hilo separado (background).
    permite que el programa continúe ejecutándose mientras se reproduce el audio.
    """
    # aca de crear un nuevo hilo
    hilo = threading.Thread(
        target=hablar,      # función a ejecutar
        args=(texto,)       # los argumentos de la funcion
    )

    # iniciar el hilo
    hilo.start()

# =====================================================
# FUNCION DE ESCUCHAR MICRÓFONO
# =====================================================
# esta función captura audio del micrófono y lo convierte a texto
# utiliza Google Speech Recognition API

def escuchar():
    """
    Captura audio del micrófono y lo convierte a texto.
    Returns:
        str: El texto reconocido del usuario
    Raises:
        Exception: Si no se puede reconocer el audio o hay error de micrófono
    """
    
    # crear el reconocedor de voz
    reconocedor = sr.Recognizer()

    # usar el micrófono como fuente de audio
    with sr.Microphone() as source:

         # esto nos sirve para que sepamos que nos esta escuchando 
        print("Escuchando...")

        # se ajusta para el ruido ambiental se hace como una 
        #calibracion
        reconocedor.adjust_for_ambient_noise(
            source,
            duration=1  # esto significa que hay 1 segndo de calibracion 
        )

        # Capturar el audio
        audio = reconocedor.listen(
            source,
            timeout=5,              # este es el tiepo de espéra que son 5 segundos 
                                    # se puede modificar si queremos mas
            phrase_time_limit=9     # este es el maximo de segudos que se puede grabar 
        )

    # Convertir el audio a texto usando Google Speech Recognition
    texto = reconocedor.recognize_google(
        audio,
        language="es-ES"  # idioma: Español de España para que nos entienda
        # ya que si estw en otro idioma no nos entendera 
    )

    # esta muestra lo que el usuario dijo
    print("Usuario dijo:", texto)

    # retorna el texto 
    return texto.lower()

# =====================================================
# esta es la funcion de organizador de archivos que mejoraremos 
# =====================================================
# Esta función organiza archivos en carpetas según su tipo
# ahora las mejoras:ahora soporta word, excel, PowerPoint, ZIP, Python y TXT

def organizar_archivos(carpeta):
    """
    Organiza automáticamente archivos en carpetas por tipo.
    
    el proceso que hace para logararlo se compone se 5 puntos 
    1. Obtener la ruta de la carpeta especificada
    2. Crear carpetas destino para cada tipo de archivo
    3. Recorrer todos los archivos en la carpeta
    4. Clasificar cada archivo según su extensión
    5. Mover el archivo a su carpeta correspondiente
    """
    
    try:
        # ------------------------------------------
        # obtener ruta segun carpeta la carpeta espeficica
        # ------------------------------------------
    
        usuario = os.getlogin()
        
        if carpeta == "Descargas":
            # Ruta a la carpeta de Descargas
            ruta = os.path.join(
                "C:\\Users",
                usuario,
                "Downloads"
            )

        elif carpeta == "Escritorio":
            # Ruta a la carpeta de Escritorio
            ruta = os.path.join(
                "C:\\Users",
                usuario,
                "Desktop"
            )
          
        elif carpeta == "Archivos":
            # esta es la ruta peronalizada 
            ruta = os.path.join(
                "C:\\Users",
                usuario,
                "Desktop",
                "Archivos"
            )

        else:
              return "No encontré la carpeta."
        # ------------------------------------------
        # CREAR CARPETAS DESTINO
        # ------------------------------------------
        # Se crean carpetas para cada tipo de archivo

        pdf_dir = os.path.join(ruta, "PDF")
        imagenes_dir = os.path.join(ruta, "Imagenes")
        videos_dir = os.path.join(ruta, "Videos")
        word_dir = os.path.join(ruta, "WORD")
        excel_dir = os.path.join(ruta, "EXCEL")
        powerpoint_dir = os.path.join(ruta, "POWERPOINT")
        comprimidos_dir = os.path.join(ruta, "COMPRIMIDOS")
        python_dir = os.path.join(ruta, "PYTHON")
        texto_dir = os.path.join(ruta, "TEXTOS")
        otros_dir = os.path.join(ruta, "Otros")

        # Crear las carpetas si no existen
        os.makedirs(pdf_dir, exist_ok=True)
        os.makedirs(imagenes_dir, exist_ok=True)
        os.makedirs(videos_dir, exist_ok=True)
        os.makedirs(word_dir, exist_ok=True)
        os.makedirs(excel_dir, exist_ok=True)
        os.makedirs(powerpoint_dir, exist_ok=True)
        os.makedirs(comprimidos_dir, exist_ok=True)
        os.makedirs(python_dir, exist_ok=True)
        os.makedirs(texto_dir, exist_ok=True)
        os.makedirs(otros_dir, exist_ok=True)

        # Contador de archivos organizados
        contador = 0

        # ------------------------------------------
        # aca recorre todos los archivos y 
        # ------------------------------------------

        for archivo in os.listdir(ruta):

            # Ruta completa del archivo
            archivo_completo = os.path.join(ruta, archivo)

            # Ignorar carpetas (solo procesar archivos)
            if os.path.isdir(archivo_completo):
                continue

            # Obtener la extensión del archivo
            extension = Path(archivo).suffix.lower()

            # ------------------------------------------
            # se clasifican y se mueven por tipos
            # ------------------------------------------

            # PDF
            if extension == ".pdf":
                destino = os.path.join(pdf_dir, archivo)

            # IMÁGENES
            elif extension in [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"]:
                destino = os.path.join(imagenes_dir, archivo)

            # VIDEOS
            elif extension in [".mp4", ".avi", ".mov", ".mkv"]:
                destino = os.path.join(videos_dir, archivo)

            # los docuemtos word (nuevo)
            elif extension == ".docx":
                destino = os.path.join(word_dir, archivo)

            # Excel (lo nuevoo)
            elif extension == ".xlsx":
                destino = os.path.join(excel_dir, archivo)

            # Powerpoint (nuevoi)
            elif extension == ".pptx":
                destino = os.path.join(powerpoint_dir, archivo)

            # los comprimidos (nuevo)
            elif extension in [".zip", ".rar"]:
                destino = os.path.join(comprimidos_dir, archivo)

            # Python (nuevo)
            elif extension == ".py":
                destino = os.path.join(python_dir, archivo)

            # Texto (nuevo)
            elif extension == ".txt":
                destino = os.path.join(texto_dir, archivo)

            # otros
            else:
                destino = os.path.join(otros_dir, archivo)

            # se mueve el archivo a su carpeta destino
            shutil.move(archivo_completo, destino)

            # Incrementar contador de archivos organizados
            contador += 1

        # Retornar mensaje de éxito
        return (
            f"Se organizaron correctamente "
            f"{contador} archivos."
        )

  # nueva funcion para el capturador de rostro 
    except Exception as e:
     return (
        f"Ocurrió un error: {str(e)}"
    )
# ==========================================
# CAPTURA DE ROSTROS la nueva fucnion
# ==========================================
def capturar_rostros(nombre_persona):
      
      #aca solo llame la funcion hablar para que me de un aviso de que se 
      # esta capturando el rostro 
    hablar(f"Capturando rostros de {nombre_persona}")
     #se crea la capeta automaticamente del dataset
    carpeta_datos = "dataset"
    # se crea la subcarpeta en la dataset con el nombre de la persona
    carpeta_persona = os.path.join(
        carpeta_datos,
        nombre_persona
    )

    Path(carpeta_persona).mkdir(
        parents=True,
        exist_ok=True
    )

    faceClassif = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)
 # esto lo habia puesto porque el xml no me estaba funcionando 
 #era para ver si el era el erro y si era 
   # print("Ruta Haar:", cv2.data.haarcascades)
    #print("Cascade vacío:", faceClassif.empty())

    if faceClassif.empty():
        return "Error: No se cargó el clasificador Haar Cascade"
#el activador de la camara
    cap = cv2.VideoCapture(0)
# comienza el contador en 0
    count = 0

    while True:

        ret, frame = cap.read()
# verifica que la camara este funcionando correcatmente 
        if not ret:
            print("Error al abrir cámara")
            break

        frame = imutils.resize(
            frame,
            width=800
        )

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        auxFrame = frame.copy()
#detecta la cantidad de rostrso en la imagen 
        faces = faceClassif.detectMultiScale(
            gray,
            1.3,
            5
        )
# recorre cada rostro detectado 
        for (x, y, w, h) in faces:
#dibuja un rectangulo verde en cada rostro detectado
            cv2.rectangle(
                frame,
                (x, y),
                (x + w, y + h),
                (0, 255, 0),
                2
            )

            rostro = auxFrame[
                y:y+h,
                x:x+w
            ]
#ajusta el tamaño del rostro
            rostro = cv2.resize(
                rostro,
                (150, 150)
            )
#guarda la imagen en la carpeta correspondiente
            cv2.imwrite(
                os.path.join(
                    carpeta_persona,
                    f"rostro_{count}.jpg"
                ),
                rostro
            )
            #aumenta el contador de las fotos
            count += 1
          #contador para ver cuantas fotos van del usuario 
            cv2.putText(
              frame,
              f"Persona: {nombre_persona}",
              (10, 70),
                 cv2.FONT_HERSHEY_SIMPLEX,
             1,
               (255, 0, 0),
             2
        )

        cv2.imshow(
            f"Capturando {nombre_persona}",
            frame
        )

        tecla = cv2.waitKey(1)
#finaliza la capatura
        if tecla == 27 or count >= 50:
            break

    cap.release()
    cv2.destroyAllWindows()

    return (
    f"Captura finalizada. "
    f"Se guardaron {count} imágenes de {nombre_persona} "
    f"en el dataset."
)

# Esta función procesa los comandos que el usuario dice
# y retorna una respuesta apropiada

def procesar_comando(comando):

    global nombre_usuario
    global capturando_rostros

    if capturando_rostros:

        capturando_rostros = False

        return capturar_rostros(comando.title())

    if nombre_usuario == "":

        nombre_usuario = comando.title()

        return (
            f"Mucho gusto {nombre_usuario}. "
            f"Estoy listo para ayudarte.\n"
            f"Puedes decir:\n"
            f"Organizar archivos,\n"
            f"Dictar texto,\n"
            f"Capturar rostro,\n"
            f"O salir."
        )

    if "dictar" in comando:
        return "Has seleccionado el modo dictado."

    elif "capturar rostro" in comando:

        capturando_rostros = True

        return "Dime el nombre de la persona"

    # -------------------------------------------------
    # OPCION: ORGANIZAR ARCHIVOS
    # -------------------------------------------------
    # Usuario quiere organizar archivos automáticamente

    elif "organizar" in comando:
        respuesta = organizar_archivos("Archivos") 
        return respuesta    

    # -------------------------------------------------
    # OPCION: SALIR
    # -------------------------------------------------
    # Usuario quiere cerrar la aplicación

    elif "salir" in comando:
        return (
            f"Hasta luego {nombre_usuario} que tenga buen dia juven"
        )

    # -------------------------------------------------
    # COMANDO DESCONOCIDO
    # -------------------------------------------------
    # Si no coincide con ningún comando

    else:
        return (
            "No entendí el comando."
        )

# =====================================================
# RUTA PRINCIPAL - PÁGINA DE INICIO
# =====================================================
# Esta ruta maneja las peticiones GET (cargar página html )
# y POST enviar información

@app.route("/", methods=["GET", "POST"])
def inicio():
    """
    Maneja la página principal del asistente.
    
    """
    
    global conversacion

    # Variable para almacenar mensajes de error
    mensaje_error = ""

    # Si la petición es POST (usuario envió un comando)
    if request.method == "POST":

        try:
            # Capturar lo que el usuario dice
            texto_usuario = escuchar()

            # se procesa elk comnando y se optiene una respuesta 
            respuesta_asistente = procesar_comando(texto_usuario)

            # parav guardar el historial 
            conversacion.append({
                "usuario": texto_usuario,
                "respuesta": respuesta_asistente
            })

            # Reproducir la respuesta en voz (en segundo plano)
            hablar_async(respuesta_asistente)

        except Exception as e:
            # si ocurre un error capturarlo
            mensaje_error = str(e)
            print(e)

    # Renderizar la plantilla HTML con los datos
    return render_template(
        "index.html",
        nombre=nombre_usuario,
        conversacion=conversacion,
        error=mensaje_error
    )

# =====================================================
# INICIO DEL PROGRAMA
# =====================================================
# Este código se ejecuta cuando se inicia la aplicación

if __name__ == "__main__":

    # Mostrar mensaje en consola
    print("ASISTENTE INICIADO")

    # Saludar al usuario
    hablar_async(
        "Hola. Soy tu asistente virtual. "
        "Por favor dime tu nombre."
    )

    # Iniciar el servidor Flask
    app.run(
        debug=False  # No mostrar errores detallados en la web
    )