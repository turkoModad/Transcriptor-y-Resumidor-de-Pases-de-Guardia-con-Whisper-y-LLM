import os
from funciones_procesamiento.procesador import crear_carpetas, procesar_audio


CARPETA_MODELO_WHISPER = "/home/turko/proyectos_subidos/youtube_transcribe_video/modelo_whisper"
RUTA_MODELO_GGUF = "/home/turko/proyectos_subidos/no_subidos/proyecto_ia/modelos/microsoft_Phi-4-mini-instruct-Q8_0.gguf"

CARPETA_AUDIOS = "audios_reuniones"
CARPETA_TRANSCRIPCIONES = "transcripciones"
CARPETA_REPORTES = "reportes_json"


def main():
    crear_carpetas([CARPETA_AUDIOS, CARPETA_TRANSCRIPCIONES, CARPETA_REPORTES])

    print("Transcriptor de reuniones cambio de turno (Whisper + PHI-4)")

    archivos_disponibles = [f for f in os.listdir(CARPETA_AUDIOS) if f.endswith(".mp3")]
    archivos_disponibles.sort()

    if not archivos_disponibles:
        print(f"\nNo se encontraron archivos .mp3 en la carpeta '{CARPETA_AUDIOS}'.")
        print("Ejecuta primero 'crear_audios_sinteticos.py' para generar las muestras.")
        return

    print("\nArchivos de audio disponibles:")
    for i, archivo in enumerate(archivos_disponibles, start=1):
        print(f"  [{i}] {archivo}")
    print(f"  [{len(archivos_disponibles) + 1}] Procesar todos los audios")

    eleccion = input("\nSeleccione una opción (Enter para procesar el primero): ").strip()

    if not eleccion or eleccion == "1":
        archivo_sel = archivos_disponibles[0]
        ruta = os.path.join(CARPETA_AUDIOS, archivo_sel)
        procesar_audio(ruta, CARPETA_MODELO_WHISPER, RUTA_MODELO_GGUF, CARPETA_TRANSCRIPCIONES, CARPETA_REPORTES)

    elif eleccion == str(len(archivos_disponibles) + 1):
        for archivo in archivos_disponibles:
            ruta = os.path.join(CARPETA_AUDIOS, archivo)
            procesar_audio(ruta, CARPETA_MODELO_WHISPER, RUTA_MODELO_GGUF, CARPETA_TRANSCRIPCIONES, CARPETA_REPORTES)

    else:
        try:
            indice = int(eleccion) - 1
            if 0 <= indice < len(archivos_disponibles):
                ruta = os.path.join(CARPETA_AUDIOS, archivos_disponibles[indice])
                procesar_audio(ruta, CARPETA_MODELO_WHISPER, RUTA_MODELO_GGUF, CARPETA_TRANSCRIPCIONES, CARPETA_REPORTES)
            else:
                print("Opción inválida.")
        except ValueError:
            print("Entrada no reconocida.")


if __name__ == "__main__":
    main()