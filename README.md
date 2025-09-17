# Speech-to-Text CLI

Esta es una herramienta de línea de comandos (CLI) para transcribir archivos de audio a texto.

## Requisitos

- Python 3.8 o superior
- `ffmpeg` para la manipulación de audio.

## Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL-del-repositorio>
    cd speech2text
    ```

2.  **Crear un entorno virtual e instalar dependencias:**
    ```bash
    python -m venv .venv
    # Activar el entorno virtual
    # En Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    # En macOS/Linux
    # source .venv/bin/activate
    pip install -r requirements.txt
    ```

3.  **Instalar ffmpeg:**
    Asegúrate de que `ffmpeg` esté instalado y disponible en el PATH de tu sistema. Puedes descargarlo desde [ffmpeg.org](https://ffmpeg.org/download.html).

## Uso

El flujo de trabajo principal es dividir un archivo de audio grande en partes más pequeñas y luego procesar cada parte para obtener la transcripción.

### 1. Dividir un archivo de audio

Usa el script `split_audio.ps1` para dividir un archivo de audio en segmentos de una duración específica. Los archivos resultantes se guardarán en el mismo directorio que el archivo de origen.

**Sintaxis:**
```powershell
./split_audio.ps1 -InputFile <ruta-al-archivo-de-audio> -SplitTime <HH:mm:ss>
```

**Ejemplo:**
Para dividir un archivo llamado `mi_audio_largo.mp3` en partes de 5 minutos:
```powershell
./split_audio.ps1 -InputFile .\data\audio1503657559_sample.wav -SplitTime 00:05:00
```
Esto generará archivos como `audio1503657559_sample_part_001.wav`, `audio1503657559_sample_part_002.wav`, etc.

### 2. Procesar los archivos de audio

Una vez que tengas los archivos de audio divididos (o cualquier archivo `.wav` que desees procesar), colócalos en el directorio `data`.

Luego, ejecuta el script `process_audio.ps1`:

```powershell
./process_audio.ps1
```

Este script buscará todos los archivos `.wav` en la carpeta `data` y ejecutará el proceso de transcripción para cada uno, utilizando el módulo `speech2text`.

### 3. Uso directo del módulo de Python

También puedes ejecutar el módulo de Python directamente para procesar un solo archivo.

```powershell
python -m speech2text transcribe ".\data\audio1503657559_sample.wav"
```
