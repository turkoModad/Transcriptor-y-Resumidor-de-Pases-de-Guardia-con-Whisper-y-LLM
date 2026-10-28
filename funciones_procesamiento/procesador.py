import os
import gc
import json
import torch
import whisper
from llama_cpp import Llama


def crear_carpetas(carpetas):
    """Crea las carpetas necesarias si no existen."""
    for carpeta in carpetas:
        if not os.path.exists(carpeta):
            os.makedirs(carpeta)


def transcribir_con_whisper(ruta_audio, carpeta_modelo_whisper):
    """
    Carga el modelo Whisper localmente, transcribe el audio y libera la memoria.
    """
    dispositivo = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n[1/4] Cargando Whisper ('medium') en modo: {dispositivo.upper()}...")

    modelo = whisper.load_model(
        "medium",
        download_root=carpeta_modelo_whisper
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


def extraer_json_con_llm(texto_reunion, ruta_modelo_gguf):
    """
    Envía la transcripción al LLM local (Phi-4) con un System Prompt estructurado
    para obtener las categorías en formato JSON.
    """
    if not os.path.exists(ruta_modelo_gguf):
        raise FileNotFoundError(f"No se encontró el modelo GGUF en: {ruta_modelo_gguf}")

    print("\n[3/4] Cargando modelo LLM local (Phi-4 Instruct)...")
    llm = Llama(
        model_path=ruta_modelo_gguf,
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
        return {
            "Tareas_Pendientes": [],
            "Riesgos_Reportados": [],
            "Maquinaria_Afectada": [],
            "raw_output": texto_salida
        }


def procesar_audio(ruta_audio, carpeta_modelo_whisper, ruta_modelo_gguf, carpeta_transcripciones, carpeta_reportes):
    """
    Proceso completo para un solo audio: Transcripción -> Guardado -> LLM -> JSON.
    """
    nombre_base = os.path.splitext(os.path.basename(ruta_audio))[0]
    print(f" PROCESANDO: {nombre_base}")

    # 1. Transcribir con Whisper
    texto = transcribir_con_whisper(ruta_audio, carpeta_modelo_whisper)

    ruta_txt = os.path.join(carpeta_transcripciones, f"{nombre_base}.txt")
    with open(ruta_txt, "w", encoding="utf-8") as f:
        f.write(texto)
    print(f"-> Transcripción guardada en: {ruta_txt}")

    # 2. Extraer información del LLM
    salida_llm = extraer_json_con_llm(texto, ruta_modelo_gguf)
    datos_estructurados = parsear_y_limpiar_json(salida_llm)

    ruta_json = os.path.join(carpeta_reportes, f"{nombre_base}.json")
    with open(ruta_json, "w", encoding="utf-8") as f:
        json.dump(datos_estructurados, f, indent=4, ensure_ascii=False)
    print(f"-> Reporte JSON guardado en: {ruta_json}")

    print(" RESUMEN EXTRAÍDO:")
    print(json.dumps(datos_estructurados, indent=2, ensure_ascii=False))

    return datos_estructurados