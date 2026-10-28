import os
from evaluacion.metricas import evaluar_par_de_archivos


CARPETA_ORIGINALES = "textos_reuniones"
CARPETA_TRANSCRIPCIONES = "transcripciones"
CARPETA_RESULTADOS = "resultados_evaluacion"


def main():
    print(" Evaluación de presición de Whisper (Texto sintético vs Transcripción)")

    if not os.path.exists(CARPETA_TRANSCRIPCIONES) or not os.path.exists(CARPETA_ORIGINALES):
        print("Error: Asegúrate de que existan las carpetas de textos y transcripciones.")
        return

    archivos_transcritos = [f for f in os.listdir(CARPETA_TRANSCRIPCIONES) if f.endswith(".txt")]
    archivos_transcritos.sort()

    if not archivos_transcritos:
        print(f"No hay transcripciones en la carpeta '{CARPETA_TRANSCRIPCIONES}'.")
        print("Ejecuta primero 'procesar_reuniones.py' para generar al menos una transcripción.")
        return

    resultados = []

    for archivo in archivos_transcritos:
        ruta_orig = os.path.join(CARPETA_ORIGINALES, archivo)
        ruta_trans = os.path.join(CARPETA_TRANSCRIPCIONES, archivo)

        if os.path.exists(ruta_orig):
            resultado = evaluar_par_de_archivos(ruta_orig, ruta_trans)
            resultados.append(resultado)

            print(f"\nArchivo evaluado: {archivo}")
            print(f"  - Palabras originales: {resultado['total_palabras_originales']}")
            print(f"  - Diferencias detectadas: {resultado['palabras_con_diferencias']}")
            print(f"  - Tasa de error (WER): {resultado['wer_error_porcentaje']}%")
            print(f"  - Precisión alcanzada: {resultado['precision_porcentaje']}%")
        else:
            print(f"\nAviso: No se encontró el texto original para '{archivo}'.")

    if resultados:
        # Promedio general
        promedio_precision = sum(r["precision_porcentaje"] for r in resultados) / len(resultados)
        promedio_wer = sum(r["wer_error_porcentaje"] for r in resultados) / len(resultados)

        print(f"\nResumen general de calidad")
        print(f"Total de archivos evaluados: {len(resultados)}")
        print(f"Tasa de error promedio (WER): {promedio_wer:.2f}%")
        print(f"Precisión promedio de Whisper: {promedio_precision:.2f}%")

        # Guardar los resultados en la carpeta de resultados
        if not os.path.exists(CARPETA_RESULTADOS):
            os.makedirs(CARPETA_RESULTADOS)

        lineas = []
        lineas.append("Evaluación de la precisión de Whisper")
        lineas.append("Detalle por archivo:\n")
        for r in resultados:
            lineas.append(f"Archivo: {r['archivo_referencia']}")
            lineas.append(f"  - Palabras originales:     {r['total_palabras_originales']}")
            lineas.append(f"  - Diferencias detectadas:  {r['palabras_con_diferencias']}")
            lineas.append(f"  - Tasa de error (WER):     {r['wer_error_porcentaje']}%")
            lineas.append(f"  - Precisión alcanzada:     {r['precision_porcentaje']}%")
            lineas.append("#" * 30)

        lineas.append("\nResumen general de calidad:")
        lineas.append(f"Total de archivos evaluados:     {len(resultados)}")
        lineas.append(f"Tasa de error promedio (WER):    {promedio_wer:.2f}%")
        lineas.append(f"Precisión promedio de Whisper:   {promedio_precision:.2f}%")

        contenido_reporte = "\n".join(lineas)
        ruta_guardado = os.path.join(CARPETA_RESULTADOS, "reporte_evaluacion.txt")
        with open(ruta_guardado, "w", encoding="utf-8") as f:
            f.write(contenido_reporte)

        print(f"\nResultados guardados exitosamente en: {ruta_guardado}")


if __name__ == "__main__":
    main()