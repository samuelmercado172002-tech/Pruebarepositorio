# Asistente Virtual en Python

## Funcionalidades actuales

### Versión 1
- Reconocimiento de voz
- Conversión de voz a texto
- Voz natural con Edge-TTS
- Registro del nombre del usuario
- Historial de conversación
### Versión 2
- Se extendio las extenciones de guardado como archivos de excel powerpoint, word, txt, .py, comprimidos

### versión 3
-Se integró un módulo de reconocimiento facial utilizando OpenCV. Se desarrolló una función para activar la cámara web, detectar rostros mediante Haar Cascade, crear automáticamente un dataset por persona y almacenar las imágenes capturadas. Además, se añadió un comando de voz al asistente para iniciar el proceso de captura de rostros de manera automática.
para futuras etapas de entrenamiento y reconocimiento.

- se agrego el archivo xml de openCV porque la carpeta del proyecto estaba teniendo problemas para leerlo desde su instalación debido al nombre de usuario de Windows que contiene un caracter que no reconoce por eso se agrego de esta manera faceClassif = cv2.CascadeClassifier(
    "haarcascade_frontalface_default.xml"
)