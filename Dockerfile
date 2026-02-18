# Usamos una imagen base ligera de Python
FROM python:3.8.16

# Evita que Python genere archivos .pyc y fuerza salida inmediata a consola
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Directorio de trabajo dentro del contenedor
WORKDIR /app

RUN apt-get update && \
    apt-get install -y git && \
    rm -rf /var/lib/apt/lists/*
    
# Instalar dependencias

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
# Copiar el código
COPY app.py .
# (Opcional: copiar historial si ya tienes uno base)
# COPY historial.txt . 

# Crear directorio para montaje
RUN mkdir -p /data/images

# Comando de ejecución
CMD ["python", "app.py"]