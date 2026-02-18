import os
import re
import shutil
import time
import schedule
import logging
from datetime import datetime   
from jrodb import Api

# --- CONFIGURACIÓN DE LOGS ---
# Para ver qué pasa dentro del contenedor
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- CONFIG VARIABLES ---
# NOTA: En Docker usaremos rutas relativas internas
FOLDER_ORIGEN = '/data/images'    # Ruta mapeada desde el Docker Volume
FOLDER_STAGING = '/app/staging'
ARCHIVO_HISTORIAL = '/app/historial.txt'

URL = os.getenv('JRO_API_URL', 'https://www.igp.gob.pe/observatorios/radio-observatorio-jicamarca/database')
API_KEY = os.getenv('JRO_API_KEY')  
DATASET_ID = os.getenv('JRO_DATASET_ID', '51570760-5452-4492-a895-ed42e3449774')

if not API_KEY:
    raise ValueError("❌ ERROR: No encontré la variable JRO_API_KEY")

MAPA_MESES = {
    '01': 'january', '02': 'february', '03': 'march', '04': 'april',
    '05': 'may', '06': 'june', '07': 'july', '08': 'august',
    '09': 'september', '10': 'october', '11': 'november', '12': 'december'
}

def proceso_subida():
    logging.info("⏰ INICIANDO RUTINA PROGRAMADA DE SUBIDA...")

    # 1. Cargar Historial
    historial = set()
    if os.path.exists(ARCHIVO_HISTORIAL):
        with open(ARCHIVO_HISTORIAL, 'r') as f:
            historial = set(line.strip() for line in f.readlines())
    
    # 2. Preparar Staging
    if os.path.exists(FOLDER_STAGING):
        shutil.rmtree(FOLDER_STAGING)
    os.makedirs(FOLDER_STAGING)

    # 3. Detectar Nuevos
    if not os.path.exists(FOLDER_ORIGEN):
        logging.error(f"❌ No encuentro la carpeta de origen: {FOLDER_ORIGEN}")
        return

    todos_archivos = sorted([f for f in os.listdir(FOLDER_ORIGEN) if f.endswith('.png')])
    archivos_nuevos = []

    for filename in todos_archivos:
        if filename not in historial:
            src = os.path.join(FOLDER_ORIGEN, filename)
            dst = os.path.join(FOLDER_STAGING, filename)
            shutil.copy2(src, dst)
            archivos_nuevos.append(filename)
    
    cantidad = len(archivos_nuevos)
    if cantidad == 0:
        logging.info("💤 Nada nuevo que subir. Volviendo a dormir.")
        shutil.rmtree(FOLDER_STAGING)
        return

    logging.info(f"📦 Detectados {cantidad} archivos nuevos. Iniciando carga...")

    # 4. Preparar Metadatos y Subir
    lista_fechas = []
    lista_others = []

    for filename in archivos_nuevos:
        match_fecha = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
        if match_fecha:
            y, m, d = match_fecha.groups()
            fecha_iso = f"{y}-{m}-{d}"
            mes = MAPA_MESES.get(m, 'unknown')
        else:
            now = datetime.now()
            fecha_iso = now.strftime('%Y-%m-%d')
            mes = 'unknown'
        
        lista_fechas.append(fecha_iso)
        lista_others.append(f"month:{mes}")
        tupla_lista=tuple(lista_others)
    try:
        # FASE 1: BULK UPLOAD
        with Api(URL, Authorization=API_KEY) as access_api:
            access_api.create(
                type_option='resource',
                package_id=DATASET_ID,
                upload=FOLDER_STAGING,
                file_date=lista_fechas,
                others=tupla_lista,
                file_type='Image',
                format='PNG',
                mimetype='image/png',
                description="Processing metadata...",
                max_count=cantidad + 50
            )
        logging.info("✅ Subida física completada.")

        # Actualizar historial temporalmente (para no re-subir si falla el patch)
        with open(ARCHIVO_HISTORIAL, 'a') as f:
            for fname in archivos_nuevos:
                f.write(fname + '\n')

        # FASE 2: PATCH DE NOTAS
        logging.info("🔧 Aplicando descripciones detalladas (Patch)...")
        with Api(URL, Authorization=API_KEY) as access_read:
            info = access_read.show(type_option='dataset', id=DATASET_ID)
            recursos_server = info.get('resources', [])

        for res in recursos_server:
            if res.get('name') in archivos_nuevos:
                r_id = res['id']
                r_name = res['name']
                
                # Extraer fecha bonita
                match = re.search(r'(\d{4})(\d{2})(\d{2})', r_name)
                fecha_bonita = f"{match.group(3)}/{match.group(2)}/{match.group(1)}" if match else "Unknown Date"
                
                desc = (
                        f"Nighttime Range-Time-Intensity (RTI) plots of Equatorial Spread F (ESF) irregularities "
                        f"observed by the Jicamarca JULIA Medium Power (MP) Coherent Scatter Radar (CSR). "
                        f"The figure displays the signal-to-noise ratio (SNR) in dB for Channel 0 and Channel 1, "
                        f"highlighting plasma bubbles and F-region instability. "
                        f"Date: {fecha_bonita}."
                    )
                try:
                    with Api(URL, Authorization=API_KEY) as access_patch:
                        access_patch.patch(type_option='resource', id=r_id, package_id=DATASET_ID, description=desc)
                except Exception as e:
                    logging.warning(f"⚠️ Falló patch nota {r_name}: {e}")

        # FASE 3: VISTAS
        with Api(URL, Authorization=API_KEY) as access_views:
            meta = access_views.show(type_option='dataset', id=DATASET_ID)
            access_views.create(type_option='views', select='dataset', package=meta)
        
        logging.info("👁️ Vistas actualizadas.")

    except Exception as e:
        logging.error(f"❌ Error crítico en el proceso: {e}")
    finally:
        if os.path.exists(FOLDER_STAGING):
            shutil.rmtree(FOLDER_STAGING)
        logging.info("🏁 Ciclo terminado. Esperando siguiente ejecución.")

# --- PLANIFICADOR ---
if __name__ == "__main__":
    print("--- 🚀 SERVIDOR DE SUBIDA AUTOMÁTICA INICIADO ---")
    
    
    proceso_subida()
    
    # schedule.every(3).days.at("02:00").do(proceso_subida) # Ejemplo: 2 AM cada 3 dias
    
    # PARA TU PRUEBA RÁPIDA (CADA 1 MINUTO):
    schedule.every(6).minutes.do(proceso_subida)
    
    # schedule.every(3).days.do(proceso_subida)

    while True:
        schedule.run_pending()
        time.sleep(60) # Revisar el reloj cada minuto
        