# Speech-to-Text CLI

Esta es una herramienta de línea de comandos (CLI) para transcribir archivos de audio a texto, y luego limpiar y estructurar la transcripción en un documento coherente.

## Requisitos

- Python 3.8 o superior.
- `ffmpeg` para la manipulación de audio.
- Una cuenta de Google Cloud con la API "Speech-to-Text" habilitada.
- Una clave (API Key) de Google Gemini para el post-procesamiento del texto.

## 1. Instalación

1.  **Clonar el repositorio:**
    ```bash
    git clone <URL-del-repositorio>
    cd speech2text
    ```

2.  **Instalar ffmpeg:**
    Asegúrate de que `ffmpeg` esté instalado y disponible en el PATH de tu sistema. Puedes descargarlo desde [ffmpeg.org](https://ffmpeg.org/download.html).

3.  **Autenticación con Google Cloud:**
    Debes autenticar tu entorno para usar los servicios de Google Cloud. La forma recomendada es usar la CLI de `gcloud`:
    ```bash
    gcloud auth application-default login
    ```

4.  **Crear un entorno virtual e instalar dependencias:**
    ```bash
    python -m venv .venv
    # Activar el entorno virtual
    # En Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1
    # En macOS/Linux
    # source .venv/bin/activate
    pip install -r requirements.txt
    ```

## 2. Configuración

Este proyecto necesita un archivo de configuración para funcionar.

1.  Crea un archivo llamado `.env` en la raíz del proyecto.
2.  Abre el archivo y pega las siguientes líneas. **Debes reemplazar los valores de ejemplo** con el nombre de tu "bucket" de Google Cloud Storage y tu clave de API de Gemini.

    ```
    GCS_BUCKET_NAME="tu-bucket-de-gcs-aqui"
    GEMINI_API_KEY="tu-api-key-de-gemini-aqui"
    ```

## 3. Uso

El flujo de trabajo principal es:
1.  Dividir un archivo de audio grande en partes más pequeñas.
2.  Transcribir cada parte a texto crudo.
3.  Unir, corregir y dar formato a todo el texto en un documento final.

---

### **Paso 1: Dividir un archivo de audio (Opcional)**

Si tienes un archivo de audio muy largo, usa el script `split_audio.ps1` para dividirlo en segmentos. Los archivos resultantes se guardarán en el mismo directorio que el archivo original.

**Ejemplo:**
Para dividir un archivo llamado `mi_audio_largo.mp3` en partes de 5 minutos:
```powershell
./split_audio.ps1 -InputFile .\data\raw\mi_audio_largo.mp3 -SplitTime 00:05:00
```
Esto generará archivos como `mi_audio_largo_part_001.wav`, `mi_audio_largo_part_002.wav`, etc.

---

### **Paso 2: Transcribir los archivos de audio**

Coloca todos los archivos `.wav` que desees procesar en un solo directorio (por ejemplo, `data/processed`).

Luego, ejecuta el script `process_audio.ps1`. Este buscará todos los archivos `.wav` y ejecutará el proceso de transcripción para cada uno.

```powershell
./process_audio.ps1
```

El resultado de cada transcripción se guardará como un archivo `.json` dentro de la carpeta `jobs`.

---

### **Paso 3: Generar el documento final (Post-procesamiento)**

Este es el paso final. Una vez que todas las partes del audio han sido transcritas, puedes usar el siguiente comando para unir todos los textos en un único documento Markdown (`.md`).

**Ejemplo:**
Si los archivos de tu transcripción están en la carpeta `jobs/mesa_1/`, ejecuta:
```bash
python -m speech2text post-process "jobs/mesa_1/"
```

Esto leerá todos los archivos `.json` de esa carpeta, los procesará con el modelo de lenguaje y creará un documento final llamado `mesa_1.md` en la raíz del proyecto.