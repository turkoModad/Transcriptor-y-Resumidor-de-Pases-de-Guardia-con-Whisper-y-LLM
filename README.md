# Transcriptor de Reuniones de Pases de guardia con Whisper + LLM Local

Este proyecto permite automatizar el procesamiento de audios de pases de turno y reuniones operativas en la industria minera (ambientado en operaciones de la Puna de Salta, como Mina Lindero, Salar del Rincón y Salar de Arizaro).

El sistema toma un audio en español (grabado o sintético), lo transcribe utilizando el modelo local **Whisper** y luego procesa el texto mediante el modelo de lenguaje local **Phi-4 (formato GGUF)** para extraer de manera estructurada y en formato **JSON** los puntos más importantes para el turno entrante:
- **Tareas Pendientes**
- **Riesgos Reportados**
- **Maquinaria Afectada**

---

## ¿Cómo funciona el proyecto?

El flujo de trabajo se divide en dos fases sencillas:

1. **Generación de datos de prueba (`crear_audios_sinteticos.py`)**:
   A partir de 3 guiones de más de 500 palabras con situaciones reales de minería (viento blanco, fallas hidráulicas, congelamiento, derrames contenidos, etc.), el script utiliza `gTTS` para generar los archivos de audio `.mp3` simulando el pase de guardia.

2. **Transcripción y Extracción Inteligente (`procesar_reuniones.py`)**:
   - **Paso 1:** Carga Whisper (`medium`) y convierte el archivo `.mp3` a texto limpio. Guarda la transcripción en la carpeta `transcripciones/`.
   - **Paso 2:** Libera la memoria RAM/VRAM utilizada por Whisper para no sobrecargar el equipo.
   - **Paso 3:** Carga el modelo LLM local (`microsoft_Phi-4-mini-instruct-Q8_0.gguf`) a través de `llama-cpp-python`.
   - **Paso 4:** Envía la transcripción con un prompt estructurado al LLM para que extraiga exactamente las tres categorías requeridas y guarda el resultado en `reportes_json/`.

---

## Estructura de Carpetas

```text
resumen-reuniones/
│
├── entorno-reuniones/            # Entorno virtual con todas las dependencias
├── textos_reuniones/             # Guiones base sobre minería en Salta
│   ├── turno_1_mina_lindero.txt
│   ├── turno_2_salar_rincon.txt
│   └── turno_3_planta_arizaro.txt
│
├── audios_reuniones/             # Audios generados o grabados en formato .mp3
│   ├── turno_1_mina_lindero.mp3
│   ├── turno_2_salar_rincon.mp3
│   └── turno_3_planta_arizaro.mp3
│
│── modelo_whisper
│
│── modelos/
│    └── microsoft_Phi-4-mini-instruct-Q8_0.gguf
│       
├── transcripciones/              # Texto extraído en Whisper
│   ├── turno_1_mina_lindero.txt
│   └── ...
│
├── reportes_json/                # Archivos JSON estructurados con los reportes
│   ├── turno_1_mina_lindero.json
│   └── ...
│
├── crear_audios_sinteticos.py    # Generador de audios sintéticos con gTTS
├── procesar_reuniones.py         # Script principal
├── requirements.txt              
└── README.md                     
```

---

## Modelos Utilizados

Para ahorrar espacio en disco y evitar duplicar archivos pesados, el proyecto reutiliza directamente los modelos ya existentes en tu máquina:

- **Whisper (modelo medium):**
  Ubicado en: `/modelo_whisper`
- **Phi-4 Mini Instruct (GGUF Q8_0):**
  Ubicado en: `/modelos/microsoft_Phi-4-mini-instruct-Q8_0.gguf`


---

## Guía de Uso Paso a Paso

### 1. Activar el Entorno Virtual
Abre una terminal en la carpeta del proyecto y activa el entorno:

```bash
cd /proyectos_subidos/resumen-reuniones
source entorno-reuniones/bin/activate
```

### 2. (Opcional) Generar nuevos audios sintéticos
Si deseas volver a generar o actualizar los audios a partir de los textos de la carpeta `textos_reuniones/`, ejecuta:

```bash
python crear_audios_sinteticos.py
```

### 3. Procesar los audios de pase de guardia
Para transcribir y extraer el resumen estructurado en JSON, ejecuta el script principal:

```bash
python procesar_reuniones.py
```

Al iniciar, verás un menú interactivo:
```text
Archivos de audio disponibles:
  [1] turno_1_mina_lindero.mp3
  [2] turno_2_salar_rincon.mp3
  [3] turno_3_planta_arizaro.mp3
  [4] Procesar TODOS los audios

Seleccione una opción:
```

Puedes ingresar el número del audio que deseas procesar (o `4` para procesar todos en lote).

---

## Ejemplo de Resultado Generado

Al finalizar el análisis, obtendrás en pantalla y guardado en `reportes_json/` un archivo como este:

```json
{
  "Tareas_Pendientes": [
    "Coordinar con el taller de mantenimiento el envío del camión lubricador y grúa para el camión 777 número 4.",
    "Purgar y cambiar el termostato y refrigerante de la pala hidráulica Komatsu PC2000.",
    "Entregar tres pallets de EPPs (barbijos, guantes térmicos, lentes antivaho) al sector perforación.",
    "Regar los caminos 2 y 3 con salmuera estabilizadora para mitigar el polvo.",
    "Verificar los tanques de oxígeno portátiles en los vehículos de la brigada de rescate."
  ],
  "Riesgos_Reportados": [
    "Pérdida de aceite hidráulico en eje trasero del camión Caterpillar 777 Nº 4.",
    "Alerta meteorológica por viento blanco con ráfagas superiores a 85 km/h a 4100 msnm.",
    "Desprendimiento de rocas en la cresta del talud sur del tajo abierto.",
    "Escarcha en escaleras metálicas de trituración primaria con riesgo de caídas."
  ],
  "Maquinaria_Afectada": [
    "Camión Caterpillar 777 Nº 4 (pérdida de aceite hidráulico en eje trasero).",
    "Pala hidráulica Komatsu PC2000 (recalentamiento del circuito de refrigeración por sedimentos).",
    "Motoniveladora 140K (neumático delantero con baja presión)."
  ]
}
```

---

## Notas para Futuras Mejoras
- Puedes agregar tus propios audios grabados con el celular o micrófono simplemente colocándolos dentro de `audios_reuniones/` en formato `.mp3`.
- Puedes agregar tu propio txt con la informacion transcripta y convertirla en audio al ejecutar `crear_audios_sinteticos.py`.
- Puedes procesar los archivos de audio con CPU o GPU, el script automáticamente reconocera si tienes una GPU y utilizara CUDA para acelerar el procesamiento. En CPU funciona de manera  estable.