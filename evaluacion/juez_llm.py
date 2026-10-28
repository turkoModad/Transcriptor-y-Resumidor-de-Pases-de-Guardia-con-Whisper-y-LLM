import os
import gc
import json
from llama_cpp import Llama


def cargar_juez_llm(ruta_modelo_gguf):
    """
    Carga el modelo local Phi-4 en memoria para actuar como auditor/juez.
    """
    if not os.path.exists(ruta_modelo_gguf):
        raise FileNotFoundError(f"No se encontró el modelo GGUF en: {ruta_modelo_gguf}")

    print("Cargando modelo LLM local (Phi-4) como Juez Auditor...")
    llm = Llama(
        model_path=ruta_modelo_gguf,
        n_ctx=4096,
        n_threads=6,
        verbose=False
    )
    return llm


def auditar_reporte_con_llm(llm, datos_esperados, datos_extraidos, nombre_archivo):
    """
    Compara semánticamente el reporte esperado contra el reporte extraído por la IA.
    Evalúa completitud, omisiones, alucinaciones y asigna una calificación.
    """
    esperado_str = json.dumps(datos_esperados, indent=2, ensure_ascii=False)
    extraido_str = json.dumps(datos_extraidos, indent=2, ensure_ascii=False)

    prompt_sistema = (
        "Eres un auditor experto en control de calidad de datos y operaciones mineras.\n"
        "Tu tarea es evaluar objetivamente la precisión de un sistema de IA comparando "
        "el 'REPORTE ESPERADO' (la verdad operativa del turno) contra el 'REPORTE EXTRAÍDO' por la IA.\n\n"
        "Debes juzgar por el significado o semántica (no por coincidencia exacta de palabras).\n\n"
        "Estructura tu respuesta exactamente con este formato:\n"
        "1. TAREAS PENDIENTES:\n"
        "   - Puntos capturados correctamente:\n"
        "   - Puntos omitidos (si los hay):\n"
        "   - Alucinaciones o invenciones (si las hay):\n\n"
        "2. RIESGOS REPORTADOS:\n"
        "   - Puntos capturados correctamente:\n"
        "   - Puntos omitidos (si los hay):\n"
        "   - Alucinaciones o invenciones (si las hay):\n\n"
        "3. MAQUINARIA AFECTADA:\n"
        "   - Puntos capturados correctamente:\n"
        "   - Puntos omitidos (si los hay):\n"
        "   - Alucinaciones o invenciones (si las hay):\n\n"
        "CALIFICACIÓN FINAL (1 al 10): [Nota]\n"
        "VEREDICTO: [Breve resumen de 2 líneas sobre la fidelidad de la extracción]"
    )

    prompt_usuario = (
        f"Archivo evaluado: {nombre_archivo}\n\n"
        f"--- REPORTE ESPERADO (VERDAD) ---\n{esperado_str}\n\n"
        f"--- REPORTE EXTRAÍDO POR LA IA ---\n{extraido_str}\n"
    )

    prompt_final = (
        f"<|system|>\n{prompt_sistema}<|end|>\n"
        f"<|user|>\n{prompt_usuario}<|end|>\n"
        f"<|assistant|>\n"
    )

    respuesta = llm(
        prompt_final,
        max_tokens=1024,
        temperature=0.1,
        stop=["<|end|>", "<|user|>", "<|system|>"]
    )

    evaluacion_texto = respuesta["choices"][0]["text"].strip()
    return evaluacion_texto


def liberar_juez_llm(llm):
    """
    Libera la memoria RAM/VRAM del LLM.
    """
    del llm
    gc.collect()