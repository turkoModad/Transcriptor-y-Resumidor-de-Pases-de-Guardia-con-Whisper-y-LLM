import os
from generador_audio.generador import generar_audio_desde_texto


CARPETA_TEXTOS = "textos_reuniones"
CARPETA_AUDIOS = "audios_reuniones"


def main():
    print(" Generador de audios sintéticos")

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
            print(f"No se encontró el archivo {ruta_txt}")

    print("Los audios fueron generados exitosamente.")


if __name__ == "__main__":
    main()