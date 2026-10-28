import os
import re
import json
from evaluacion.juez_llm import cargar_juez_llm, auditar_reporte_con_llm, liberar_juez_llm


RUTA_MODELO_GGUF = "/home/turko/proyectos_subidos/no_subidos/proyecto_ia/modelos/microsoft_Phi-4-mini-instruct-Q8_0.gguf"
CARPETA_ESPERADOS = "reportes_esperados"
CARPETA_EXTRAIDOS = "reportes_json"
CARPETA_RESULTADOS = "resultados_evaluacion"


def extraer_calificacion(texto_dictamen):
    """
    Busca la calificación numérica en el texto devuelto por el LLM (ej. 10/10 o 7/10).
    """
    coincidencia = re.search(r'CALIFICACI[ÓO]N FINAL.*?:\s*(\d+(?:\.\d+)?)', texto_dictamen, re.IGNORECASE)
    if coincidencia:
        try:
            return float(coincidencia.group(1))
        except ValueError:
            return None
    return None


def main():
    print("Auditoría de reportes con LLM (Phi-4)")

    if not os.path.exists(CARPETA_ESPERADOS) or not os.path.exists(CARPETA_EXTRAIDOS):
        print("Error: Asegúrate de que existan las carpetas de reportes esperados y extraídos.")
        return

    archivos_esperados = [f for f in os.listdir(CARPETA_ESPERADOS) if f.endswith(".json")]
    archivos_esperados.sort()

    if not archivos_esperados:
        print(f"No hay archivos en la carpeta '{CARPETA_ESPERADOS}'.")
        return

    # Cargar el LLM
    llm = cargar_juez_llm(RUTA_MODELO_GGUF)

    lineas_reporte = []
    lineas_reporte.append("Auditoría de reportes con LLM (Phi-4)")
    lineas_reporte.append("Detalle por archivo:\n")

    calificaciones = []

    for archivo in archivos_esperados:
        ruta_esp = os.path.join(CARPETA_ESPERADOS, archivo)
        ruta_ext = os.path.join(CARPETA_EXTRAIDOS, archivo)

        if not os.path.exists(ruta_ext):
            print(f"\nAviso: No se encontró el reporte extraído para '{archivo}'. Omitiendo...")
            continue

        print(f"\nAuditando: {archivo}...")

        with open(ruta_esp, "r", encoding="utf-8") as f:
            datos_esp = json.load(f)

        with open(ruta_ext, "r", encoding="utf-8") as f:
            datos_ext = json.load(f)

        dictamen = auditar_reporte_con_llm(llm, datos_esp, datos_ext, archivo)

        nota = extraer_calificacion(dictamen)
        if nota is not None:
            calificaciones.append(nota)

        print(f"\nArchivo: {archivo}")
        print(dictamen)
        print("#" * 30)

        lineas_reporte.append(f"Archivo: {archivo}")
        lineas_reporte.append(dictamen)
        lineas_reporte.append("#" * 30)

    # Liberar memoria del LLM
    liberar_juez_llm(llm)

    if calificaciones:
        promedio = sum(calificaciones) / len(calificaciones)

        print("\nResumen general de calidad:")
        print(f"Total de archivos evaluados:     {len(calificaciones)}")
        print(f"Calificación promedio de Phi-4:  {promedio:.2f} / 10")

        lineas_reporte.append("\nResumen general de calidad:")
        lineas_reporte.append(f"Total de archivos evaluados:     {len(calificaciones)}")
        lineas_reporte.append(f"Calificación promedio de Phi-4:  {promedio:.2f} / 10")

    if not os.path.exists(CARPETA_RESULTADOS):
        os.makedirs(CARPETA_RESULTADOS)

    ruta_salida = os.path.join(CARPETA_RESULTADOS, "auditoria_reportes_llm.txt")
    with open(ruta_salida, "w", encoding="utf-8") as f:
        f.write("\n".join(lineas_reporte))

    print(f"\nResultados guardados en: {ruta_salida}")


if __name__ == "__main__":
    main()