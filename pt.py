import asyncio
import edge_tts
import pygame
import os


async def hablar(texto):

    archivo = "voz.mp3"

    comunicacion = edge_tts.Communicate(
        texto,
        voice="es-NI-FedericoNeural"
    )

    await comunicacion.save(archivo)

    pygame.mixer.init()
    pygame.mixer.music.load(archivo)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pass

    pygame.mixer.quit()

    os.remove(archivo)

asyncio.run(
    hablar(
        "Hola Hilder, esta voz es mucho más natural."
    )
)

