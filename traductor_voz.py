import speech_recognition as sr
import pyttsx3
from datetime import datetime


voz = pyttsx3.init()

def hablar(texto):
    voz.say(texto)
    voz.runAndWait()

def guardar_texto(texto):
    
    fecha = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nombre_archivo = f"voz_{fecha}.txt"
    
    with open(nombre_archivo, "w", encoding="utf-8") as archivo:
        archivo.write(texto)
    
    return nombre_archivo

def escuchar_y_guardar():
    
    reconocedor = sr.Recognizer()

    with sr.Microphone() as origen:
        
        print("Ajustando ruido de fondo...")
        hablar("Ajustando ruido de fondo")
        
        reconocedor.adjust_for_ambient_noise(origen, duration=1)

        print("Habla ahora...")
        hablar("Habla ahora")

        audio = reconocedor.listen(origen)

        print("Procesando...")
        hablar("Procesando tu voz")

    try:
        
        texto = reconocedor.recognize_google(audio, language="es-ES")

        print("\nTexto detectado:")
        print(texto)

        
        hablar("Dijiste")
        hablar(texto)

        
        archivo = guardar_texto(texto)

        mensaje = f"Texto guardado en {archivo}"
        print(mensaje)
        hablar("Texto guardado correctamente")

    except sr.UnknownValueError:
        print("No pude entender el audio")
        hablar("No pude entender el audio")

    except sr.RequestError as e:
        print(f"Error con el servicio: {e}")
        hablar("Error con el servicio de reconocimiento")

if __name__ == "__main__":
    escuchar_y_guardar()   
    
 