# 📡 JRO Data Uploader Service

Este es un servicio automatizado dockerizado diseñado para el **Radio Observatorio de Jicamarca (JRO)**. Su función principal es monitorear un directorio local en busca de nuevas imágenes y subirlas automáticamente a la base de datos CKAN del instituto.

El servicio está construido en **Python 3.8.16** y utiliza una arquitectura de contenedor ligero p
---

## 📋 Requisitos Previos

Para construir y desplegar este servicio necesitas:

1.  **Docker** instalado en el servidor.
2.  **Acceso a la Intranet del IGP**: ⚠️ **CRÍTICO**.
    * El archivo `requirements.txt` descarga la librería `jrodb_lib` directamente desde el repositorio interno (`intranet.igp.gob.pe`).
    * Si intentas construir la imagen (`docker build`) desde una red externa (como tu casa) sin VPN, **fallará**.

---

## ⚙️ Instalación y Despliegue

### 1. Clonar el Repositorio
```bash
$ git clone git@github.com:APOLO-UNSA/jro-uploader.git
$ cd jro-uploader.
```
### ⚙️ 2. Variables de Entorno (Configuración)

El contenedor se configura mediante variables de entorno. Es indispensable definir la API KEY y la Zona Horaria para el correcto funcionamiento.
| Variable | Descripción | Valor por Defecto |
| :--- | :--- | :--- |
| `JRO_API_KEY` | **(Obligatorio)** Clave de acceso. | *Ninguno* (Tendrás que colocar el tuyo)|
| `TZ` | Zona horaria del contenedor. | `UTC` (cambiar al de lima, Perú)|
| `JRO_API_URL` | URL del jro database | url al repositorio |
| `JRO_DATASET_ID` | ID del dataset | ID del dataset 2025 esf (cambiar para el deseado)|

### 🚀 3. Ejecución del Contenedor

Para iniciar el servicio en segundo plano (-d) con reinicio automático (unless-stopped), utiliza el siguiente comando.

*Nota: Reemplaza /ruta/real/de/imagenes con la ruta absoluta donde se guardan las fotos en tu servidor.*

```bash

docker run -d \
  --name uploader-servicio \
  --restart unless-stopped \
  -e TZ=America/Lima \
  -e JRO_DATASET_ID="id_del_dataset" \
  -e JRO_API_KEY="TU_CLAVE_API_AQUI" \
  -v /ruta/real/de/imagenes:/data/images \
  jro-uploader:v1
```

### 📊 4. Comandos de Monitoreo y Mantenimiento

Comandos útiles para gestionar el ciclo de vida del servicio:
🔍 Ver estado del servicio

Verifica si el contenedor está Up (corriendo) o Restarting (en bucle de error).
```Bash
docker ps -a
```
## 📜 Consultar Logs en tiempo real

Muestra las últimas 50 líneas y se queda esperando nuevos eventos. Útil para ver qué archivos se están subiendo.
```Bash

docker logs -f --tail 50 uploader-servicio
```
(Presiona Ctrl + C para salir de la vista de logs)

## 📈 Verificar consumo de recursos

Revisa cuánta memoria RAM y CPU está consumiendo el proceso.
```Bash

docker stats uploader-servicio --no-stream
```
## 🔄 Reiniciar el servicio

Úsalo si cambiaste la configuración, la red se cayó, o el servicio se quedó pegado.
```Bash

docker restart uploader-servicio
```
## 🛑 Detener y Eliminar

Para apagar el servicio completamente. Esto borra el contenedor pero NO borra la imagen ni tus datos.
```Bash

docker stop uploader-servicio
docker rm uploader-servicio
```
## 📂 Estructura del Proyecto

```text
ckan
├── docker-entrypoint.d
│   └── setup_validation.sh
├── Dockerfile
└── Dockerfile.dev
