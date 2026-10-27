import os
from gtts import gTTS


CARPETA_TEXTOS = "textos_reuniones"
CARPETA_AUDIOS = "audios_reuniones"

def generar_audio_desde_texto(ruta_texto, ruta_audio_salida):
    """
    Lee un archivo de texto y lo convierte a audio MP3 utilizando gTTS.
    """
    print(f"\nLeyendo archivo: {ruta_texto}")
    with open(ruta_texto, "r", encoding="utf-8") as f:
        contenido = f.read()

    print(f"Generando audio sintético con voz en español...")
    # Configuracion en español
    tts = gTTS(text=contenido, lang="es", tld="com.ar")
    
    tts.save(ruta_audio_salida)
    print(f"-> Audio guardado exitosamente en: {ruta_audio_salida}")

def main():
    print(" GENERADOR DE AUDIOS SINTÉTICOS DE REUNIONES DE TURNO (PUNA DE SALTA)")

    if not os.path.exists(CARPETA_AUDIOS):
        os.makedirs(CARPETA_AUDIOS)

    # Lista de archivos a procesar
    archivos_reuniones = [
        ("turno_1_mina_lindero.txt", "turno_1_mina_lindero.mp3"),
        ("turno_2_salar_rincon.txt", "turno_2_salar_rincon.mp3"),
        ("turno_3_planta_arizaro.txt", "turno_3_planta_arizaro.mp3")
    ]

    for archivo_txt, archivo_mp3 in archivos_reuniones:
        ruta_txt = os.path.join(CARPETA_TEXTOS, archivo_txt)
        ruta_mp3 = os.path.join(CARPETA_AUDIOS, archivo_mp3)

        if os.path.exists(ruta_txt):
            generar_audio_desde_texto(ruta_txt, ruta_mp3)
        else:
            print(f"Aviso: No se encontró el archivo {ruta_txt}")

    print("Los 3 audios fueron generados.")

if __name__ == "__main__":
    main()

