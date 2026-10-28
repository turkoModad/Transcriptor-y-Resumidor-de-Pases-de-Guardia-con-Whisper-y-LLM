import re
import os


def normalizar_texto(texto):
    """
    Prepara el texto para una comparación justa:
    - Convierte todo a minúsculas.
    - Elimina signos de puntuación (puntos, comas, guiones, comillas, etc.).
    - Elimina saltos de línea y espacios repetidos.
    """
    if not texto:
        return ""

    # Convertir a minúsculas
    texto_limpio = texto.lower()

    # Reemplazar cualquier signo de puntuación por un espacio
    texto_limpio = re.sub(r'[^\w\s]', ' ', texto_limpio)

    # Reducir múltiples espacios a uno solo
    texto_limpio = re.sub(r'\s+', ' ', texto_limpio).strip()

    return texto_limpio


def calcular_wer(texto_referencia, texto_hipotesis):
    """
    Calcula el Word Error Rate (WER) entre el texto original (referencia)
    y el texto transcripto por Whisper (hipótesis).

    Utiliza el algoritmo de distancia de Levenshtein a nivel de palabras.
    Devuelve:
    - wer_porcentaje: porcentaje de error (menor es mejor)
    - precision_porcentaje: porcentaje de acierto (mayor es mejor)
    - total_errores: cantidad de palabras sustituidas, eliminadas o insertadas
    - total_palabras: cantidad de palabras en el texto original
    """
    ref_palabras = normalizar_texto(texto_referencia).split()
    hip_palabras = normalizar_texto(texto_hipotesis).split()

    n = len(ref_palabras)
    m = len(hip_palabras)

    if n == 0:
        return 0.0, 100.0, 0, 0

    # Creamos la matriz para comparar palabra por palabra
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    # Algoritmo de distancia de edición (Levenshtein)
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref_palabras[i - 1] == hip_palabras[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                sustitucion = dp[i - 1][j - 1] + 1
                insercion = dp[i][j - 1] + 1
                eliminacion = dp[i - 1][j] + 1
                dp[i][j] = min(sustitucion, insercion, eliminacion)

    total_errores = dp[n][m]
    wer_porcentaje = round((total_errores / n) * 100, 2)
    precision_porcentaje = round(max(0.0, 100.0 - wer_porcentaje), 2)

    return wer_porcentaje, precision_porcentaje, total_errores, n


def evaluar_par_de_archivos(ruta_referencia, ruta_transcripcion):
    """
    Lee un archivo original (sintético) y su correspondiente transcripción,
    calcula la precisión y devuelve un resumen.
    """
    if not os.path.exists(ruta_referencia):
        raise FileNotFoundError(f"No existe el archivo de referencia: {ruta_referencia}")
    if not os.path.exists(ruta_transcripcion):
        raise FileNotFoundError(f"No existe el archivo de transcripción: {ruta_transcripcion}")

    with open(ruta_referencia, "r", encoding="utf-8") as f:
        texto_ref = f.read()

    with open(ruta_transcripcion, "r", encoding="utf-8") as f:
        texto_hip = f.read()

    wer, precision, errores, total = calcular_wer(texto_ref, texto_hip)

    return {
        "archivo_referencia": os.path.basename(ruta_referencia),
        "archivo_transcripcion": os.path.basename(ruta_transcripcion),
        "total_palabras_originales": total,
        "palabras_con_diferencias": errores,
        "wer_error_porcentaje": wer,
        "precision_porcentaje": precision
    }