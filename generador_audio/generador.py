import os
from gtts import gTTS


def generar_audio_desde_texto(ruta_texto, ruta_audio_salida):
    """
    Lee un archivo de texto y lo convierte a audio MP3 utilizando gTTS.
    
    """
    print(f"\nLeyendo archivo: {ruta_texto}")
    with open(ruta_texto, "r", encoding="utf-8") as f:
        contenido = f.read()

    print("Generando audio sintético con voz en español...")
    # Configuración en español
    tts = gTTS(text=contenido, lang="es", tld="com.ar")
    
    tts.save(ruta_audio_salida)
    print(f"Audio guardado exitosamente en: {ruta_audio_salida}")