import os
import re
import gc
import json
import torch
import whisper
from llama_cpp import Llama


CARPETA_MODELO_WHISPER = "/home/turko/proyectos_subidos/youtube_transcribe_video/modelo_whisper"
RUTA_MODELO_GGUF = "/home/turko/proyectos_subidos/no_subidos/proyecto_ia/modelos/microsoft_Phi-4-mini-instruct-Q8_0.gguf"


CARPETA_AUDIOS = "audios_reuniones"
CARPETA_TRANSCRIPCIONES = "transcripciones"
CARPETA_REPORTES = "reportes_json"


def crear_carpetas():
    """Crea las carpetas necesarias si no existen."""
    for carpeta in [CARPETA_AUDIOS, CARPETA_TRANSCRIPCIONES, CARPETA_REPORTES]:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)


def transcribir_con_whisper(ruta_audio):
    """
    Carga el modelo Whisper localmente, transcribe el audio y libera la memoria.
    """
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n[1/4] Cargando Whisper ('medium') en modo: {dispositivo.upper()}...")


    modelo = whisper.load_model(
        "medium",
        download_root=CARPETA_MODELO_WHISPER
    )

    if dispositivo == "cuda":
        modelo = modelo.to(dispositivo)

    print(f"[2/4] Transcribiendo el audio: {os.path.basename(ruta_audio)}...")
    resultado = modelo.transcribe(
        ruta_audio,
        language="es",
        fp16=(dispositivo == "cuda"),
        verbose=False
    )

    texto_transcrito = resultado["text"].strip()

    # Liberar la memoria de la GPU/RAM
    del modelo
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return texto_transcrito



def extraer_json_con_llm(texto_reunion):
    """
    Envía la transcripción al LLM local (Phi-4) con un System Prompt estructurado
    para obtener las categorías en formato JSON.
    """
    if not os.path.exists(RUTA_MODELO_GGUF):
        raise FileNotFoundError(f"No se encontró el modelo GGUF en: {RUTA_MODELO_GGUF}")

    print("\n[3/4] Cargando modelo LLM local (Phi-4 Instruct)...")
    llm = Llama(
        model_path=RUTA_MODELO_GGUF,
        n_ctx=4096,
        n_threads=6,
        verbose=False
    )

    prompt_sistema = (
        "Eres un analista experto en seguridad y operaciones mineras en la Puna de Salta.\n"
        "Tu tarea es analizar la transcripción de una reunión de pase de guardia o turno "
        "y extraer la información clave de forma estructurada.\n\n"
        "Debes responder ÚNICAMENTE con un JSON válido, sin preámbulos, sin saludos ni explicaciones.\n"
        "La estructura obligatoria del JSON es exactamente la siguiente:\n"
        "{\n"
        '  "Tareas_Pendientes": ["tarea 1", "tarea 2", ...],\n'
        '  "Riesgos_Reportados": ["riesgo 1", "riesgo 2", ...],\n'
        '  "Maquinaria_Afectada": ["maquinaria 1 y su estado", ...]\n'
        "}\n"
    )

    prompt_final = (
        f"<|system|>\n{prompt_sistema}<|end|>\n"
        f"<|user|>\nTranscripción de la reunión:\n\"\"\"\n{texto_reunion}\n\"\"\"<|end|>\n"
        f"<|assistant|>\n"
    )

    print("[4/4] Analizando transcripción y extrayendo puntos críticos...")
    respuesta = llm(
        prompt_final,
        max_tokens=1024,
        temperature=0.1,
        stop=["<|end|>", "<|user|>", "<|system|>"]
    )

    texto_salida = respuesta["choices"][0]["text"].strip()

    # Liberar memoria del LLM
    del llm
    gc.collect()

    return texto_salida


def parsear_y_limpiar_json(texto_salida):
    """
    Limpia etiquetas de markdown como ```json ... ``` y convierte el texto a diccionario Python.
    """
    texto_limpio = texto_salida.strip()

    # Si el LLM devolvió bloques de código en markdown, los removemos
    if "```json" in texto_limpio:
        texto_limpio = texto_limpio.split("```json")[1].split("```")[0].strip()
    elif "```" in texto_limpio:
        texto_limpio = texto_limpio.split("```")[1].split("```")[0].strip()

    inicio = texto_limpio.find("{")
    fin = texto_limpio.rfind("}")
    if inicio != -1 and fin != -1:
        texto_limpio = texto_limpio[inicio:fin + 1]

    try:
        datos_json = json.loads(texto_limpio)
        return datos_json
    except json.JSONDecodeError:
        print("\nAviso: No se pudo convertir automáticamente a JSON estricto.")
        # Retornar un diccionario con el texto bruto si falla el parser
        return {
            "Tareas_Pendientes": [],
            "Riesgos_Reportados": [],
            "Maquinaria_Afectada": [],
            "raw_output": texto_salida
        }


def procesar_audio(ruta_audio):
    """
    Proceso completo para un solo audio: Transcripción -> Guardado -> LLM -> JSON.
    """
    nombre_base = os.path.splitext(os.path.basename(ruta_audio))[0]
    print(f" PROCESANDO: {nombre_base}")

    # 1. Transcribir con Whisper
    texto = transcribir_con_whisper(ruta_audio)

    # Guardar transcripcion en archivo de texto
    ruta_txt = os.path.join(CARPETA_TRANSCRIPCIONES, f"{nombre_base}.txt")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"-> Transcripción guardada en: {ruta_txt}")

    # 2. Extraer informacion del LLM
    salida_llm = extraer_json_con_llm(texto)
    datos_estructurados = parsear_y_limpiar_json(salida_llm)

    # Guardar reporte en formato JSON
    ruta_json = os.path.join(CARPETA_REPORTES, f"{nombre_base}.json")
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos_estructurados, f, indent=4, ensure_ascii=False)
    print(f"-> Reporte JSON guardado en: {ruta_json}")

    print(" RESUMEN EXTRAÍDO:")
    print(json.dumps(datos_estructurados, indent=2, ensure_ascii=False))

    return datos_estructurados


def main():
    crear_carpetas()
    print(" Transcriptor de reuniones cambio de turno (Whisper + PHI-4)")

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
        procesar_audio(os.path.join(CARPETA_AUDIOS, archivo_sel))
    elif eleccion == str(len(archivos_disponibles) + 1):
        for archivo in archivos_disponibles:
            procesar_audio(os.path.join(CARPETA_AUDIOS, archivo))
    else:
        try:
            indice = int(eleccion) - 1
            if 0 <= indice < len(archivos_disponibles):
                procesar_audio(os.path.join(CARPETA_AUDIOS, archivos_disponibles[indice]))
            else:
                print("Opción inválida.")
        except ValueError:
            print("Entrada no reconocida.")


if __name__ == "__main__":
    main()

