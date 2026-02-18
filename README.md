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
git clone git@github.com:APOLO-UNSA/jro-uploader.git
cd jro-uploader
