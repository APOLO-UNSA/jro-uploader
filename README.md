# 📡 JRO Data Uploader Suite

Este repositorio contiene las herramientas oficiales para la gestión de datos en el **Radio Observatorio de Jicamarca (JRO)**. Incluye un servicio automatizado (Docker) y una aplicación de escritorio (GUI) para la carga manual y mantenimiento de recursos en el portal CKAN.

---

## 📡 Instalación
Para instalar el Uploader Suite, ejecute los siguientes comandos:

```bash
git clone https://github.com/APOLO-UNSA/jro-uploader.git
cd jro-uploader
```

## 🖥️ JRO Uploader Desktop (GUI)

La aplicación de escritorio permite a los investigadores gestionar los datos de forma visual e interactiva.

### ✨ Funcionalidades
*   **Selección Manual:** Elige archivos específicos (uno o varios) para subir al dataset.
*   **Descripción Personalizada:** Al subir archivos, puedes escribir una nota técnica que se combinará automáticamente con la fecha del archivo.
*   **Limpieza de Datos:**
    *   **Eliminar Seleccionados:** Busca y borra permanentemente archivos del servidor basándose en la lista local.
    *   **Vaciar Dataset:** Elimina todos los recursos de un dataset de forma masiva (con confirmación de seguridad).
*   **Log en tiempo real:** Consola integrada para monitorear el éxito o error de cada fase (Subida, Patch de Notas, Vistas).

### ⚙️ Instalación Local (Linux)
Para ejecutar la aplicación de escritorio fuera de Docker, configura un entorno virtual:

```bash
# Crear entorno virtual
python3 -m venv .venv_gui
source .venv_gui/bin/activate

# Instalar dependencias (Requiere conexión a la Intranet del IGP)
pip install -r requirements_GUI.txt
```

### 🚀 Ejecución
```bash
# Activar y ejecutar
./.venv_gui/bin/python3 install_gui.py
./.venv_gui/bin/python3 gui_app.py
```

*Nota: Puedes usar el  `JRO_Uploader.desktop` para crear un acceso directo en tu escritorio de Ubuntu.*

---

## 🐋 JRO Uploader Service (Docker)

Servicio diseñado para correr en servidores de forma ininterrumpida, monitoreando carpetas en busca de nuevas imágenes RTI.

### 📋 Requisitos Previos
1.  **Docker** instalado.
2.  **Acceso a la Intranet del IGP** (Necesario para descargar la librería `jrodb`).

### ⚙️ Configuración (Variables de Entorno)
| Variable | Descripción |
| :--- | :--- |
| `JRO_API_KEY` | Clave de acceso secreta de CKAN. |
| `JRO_API_URL` | URL del repositorio (IGP Database). |
| `JRO_DATASET_ID` | ID único del dataset (UUID). |

### 🚀 Despliegue Rápido
```bash
docker run -d \
  --name uploader-servicio \
  --restart unless-stopped \
  -e TZ=America/Lima \
  -e JRO_API_KEY="TU_CLAVE" \
  -e JRO_DATASET_ID="ID_DEL_DATASET" \
  -v /ruta/imagenes:/data/images \
  jro-uploader:v1
```

---

## 📂 Estructura del Proyecto
*   `app.py`: Lógica del servicio automático (background).
*   `gui_app.py`: Lógica de la aplicación interactiva (desktop).
*   `Dockerfile`: Configuración para despliegue en contenedores.
*   `requirements.txt`: Dependencias del sistema y librerías internas del IGP.

---
© 2026 Radio Observatorio de Jicamarca - Instituto Geofísico del Perú.
