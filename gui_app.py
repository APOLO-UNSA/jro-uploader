import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
import threading
import logging
import re
import shutil
from datetime import datetime
from jrodb import Api

# Mapa de meses para metadatos
MAPA_MESES = {
    '01': 'january', '02': 'february', '03': 'march', '04': 'april',
    '05': 'may', '06': 'june', '07': 'july', '08': 'august',
    '09': 'september', '10': 'october', '11': 'november', '12': 'december'
}

class JROUploaderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("JRO Data Uploader - Desktop Professional")
        self.root.geometry("850x850")
        
        # Variables de configuración
        self.api_url = tk.StringVar(value=os.getenv('JRO_API_URL', 'https://www.igp.gob.pe/observatorios/radio-observatorio-jicamarca/database'))
        self.api_key = tk.StringVar(value=os.getenv('JRO_API_KEY', ''))
        self.dataset_id = tk.StringVar(value=os.getenv('JRO_DATASET_ID', '51570760-5452-4492-a895-ed42e3449774'))
        self.folder_path = tk.StringVar(value=os.getcwd())
        
        self.setup_ui()
        self.setup_logging()
        
        self.logger.info("🚀 Aplicación iniciada y lista.")

    def setup_ui(self):
        style = ttk.Style()
        style.configure("TButton", padding=5)
        style.configure("Danger.TButton", foreground="red")
        
        # --- CONFIGURACIÓN ---
        config_frame = ttk.LabelFrame(self.root, text=" ⚙️ Configuración de Conexión ", padding=15)
        config_frame.pack(fill="x", padx=15, pady=10)

        ttk.Label(config_frame, text="URL del Repositorio:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(config_frame, textvariable=self.api_url, width=65).grid(row=0, column=1, padx=10, pady=2)

        ttk.Label(config_frame, text="API Key Secreta:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(config_frame, textvariable=self.api_key, width=65, show="*").grid(row=1, column=1, padx=10, pady=2)

        ttk.Label(config_frame, text="ID del Dataset:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(config_frame, textvariable=self.dataset_id, width=65).grid(row=2, column=1, padx=10, pady=2)

        # --- GESTIÓN DE ARCHIVOS (SUBIDA) ---
        files_frame = ttk.LabelFrame(self.root, text=" 📂 Gestión de Archivos y Subida ", padding=15)
        files_frame.pack(fill="both", expand=True, padx=15, pady=5)

        folder_subframe = ttk.Frame(files_frame)
        folder_subframe.pack(fill="x", pady=5)
        ttk.Label(folder_subframe, text="Carpeta de Origen:").pack(side="left")
        ttk.Entry(folder_subframe, textvariable=self.folder_path, width=50).pack(side="left", padx=10)
        ttk.Button(folder_subframe, text="Cambiar Carpeta", command=self.browse_folder).pack(side="left")

        list_frame = ttk.Frame(files_frame)
        list_frame.pack(fill="both", expand=True, pady=10)
        self.file_listbox = tk.Listbox(list_frame, selectmode="extended", font=("Consolas", 10))
        self.file_listbox.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.config(yscrollcommand=scrollbar.set)

        btn_frame = ttk.Frame(files_frame)
        btn_frame.pack(fill="x")
        ttk.Button(btn_frame, text="🔄 Actualizar Lista Local", command=self.refresh_file_list).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="🚀 SUBIR SELECCIONADOS", command=self.start_manual_upload).pack(side="left", padx=5)
        
        # --- OPERACIONES DE LIMPIEZA ---
        cleanup_frame = ttk.LabelFrame(self.root, text=" 🗑️ Operaciones de Limpieza (Permanente) ", padding=15)
        cleanup_frame.pack(fill="x", padx=15, pady=10)
        
        ttk.Button(cleanup_frame, text="❌ Eliminar SELECCIONADOS del Servidor", 
                   command=self.start_delete_selected).pack(side="left", padx=5)
        
        ttk.Button(cleanup_frame, text="🔥 VACIAR TODO EL DATASET", 
                   style="Danger.TButton", command=self.start_delete_all).pack(side="right", padx=5)

        # --- CONSOLA ---
        log_frame = ttk.LabelFrame(self.root, text=" 📝 Log de Actividad ", padding=5)
        log_frame.pack(fill="x", padx=15, pady=10)
        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, state='disabled', 
                                                 background="#1e1e1e", foreground="#00ff00",
                                                 font=("Consolas", 10))
        self.log_area.pack(fill="x")

    def setup_logging(self):
        # Limpiar cualquier configuración de logging previa
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        class TextHandler(logging.Handler):
            def __init__(self, text_widget):
                super().__init__()
                self.text_widget = text_widget

            def emit(self, record):
                msg = self.format(record)
                def append():
                    self.text_widget.configure(state='normal')
                    self.text_widget.insert('end', msg + '\n')
                    self.text_widget.configure(state='disabled')
                    self.text_widget.see('end')
                # Usar after para asegurar que la UI se actualice correctamente desde cualquier hilo
                self.text_widget.after(0, append)

        # Configuramos el logger principal de la clase
        self.logger = logging.getLogger("JRO_GUI")
        self.logger.setLevel(logging.INFO)
        
        # Handler para la interfaz
        gui_handler = TextHandler(self.log_area)
        gui_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s', datefmt='%H:%M:%S'))
        self.logger.addHandler(gui_handler)
        
        # También mandamos a la consola real por si acaso
        console_handler = logging.StreamHandler()
        self.logger.addHandler(console_handler)

    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_path.set(folder)
            self.refresh_file_list()

    def refresh_file_list(self):
        self.file_listbox.delete(0, 'end')
        path = self.folder_path.get()
        if os.path.exists(path):
            files = [f for f in os.listdir(path) if f.endswith('.png')]
            for f in sorted(files):
                self.file_listbox.insert('end', f)
            self.logger.info(f"Carpeta actualizada. {len(files)} archivos PNG encontrados.")

    def delete_logic(self, filenames_to_delete=None, delete_all=False):
        url = self.api_url.get()
        key = self.api_key.get()
        ds_id = self.dataset_id.get()
        
        ids_para_eliminar = []
        try:
            self.logger.info("🔍 Conectando para buscar recursos...")
            with Api(url, Authorization=key) as access_read:
                dataset_info = access_read.show(type_option='dataset', id=ds_id)
                resources = dataset_info.get('resources', [])
                
                for res in resources:
                    res_name = res.get('name')
                    res_id = res.get('id')
                    if delete_all or (filenames_to_delete and res_name in filenames_to_delete):
                        ids_para_eliminar.append(res_id)
                        self.logger.info(f"   📍 Identificado: {res_name}")

            if not ids_para_eliminar:
                self.logger.warning("⚠️ No se encontraron archivos para eliminar.")
                return

            self.logger.info(f"🗑️ Ejecutando eliminación de {len(ids_para_eliminar)} archivos...")
            with Api(url, Authorization=key) as access_delete:
                access_delete.delete(type_option='resource', select='purge', package_id=ds_id, id=ids_para_eliminar)
            
            self.logger.info(f"✅ ÉXITO: {len(ids_para_eliminar)} archivos eliminados del servidor.")
            messagebox.showinfo("Éxito", "Eliminación completada.")

        except Exception as e:
            self.logger.error(f"❌ ERROR en borrado: {str(e)}")

    def start_delete_selected(self):
        selected = self.file_listbox.curselection()
        if not selected: return
        filenames = [self.file_listbox.get(i) for i in selected]
        if messagebox.askyesno("Confirmar", f"¿Eliminar {len(filenames)} archivos del servidor?"):
            threading.Thread(target=self.delete_logic, kwargs={'filenames_to_delete': filenames}, daemon=True).start()

    def start_delete_all(self):
        if simpledialog.askstring("PELIGRO", "Escribe ELIMINAR para borrar TODO el dataset:") == "ELIMINAR":
            threading.Thread(target=self.delete_logic, kwargs={'delete_all': True}, daemon=True).start()

    def upload_logic(self, archivos_nuevos, user_description):
        url = self.api_url.get()
        key = self.api_key.get()
        ds_id = self.dataset_id.get()
        origen = self.folder_path.get()
        staging = os.path.join(origen, 'gui_staging_tmp')

        try:
            if os.path.exists(staging): shutil.rmtree(staging)
            os.makedirs(staging)

            lista_fechas, lista_others = [], []
            self.logger.info(f"📦 Fase 1: Preparando {len(archivos_nuevos)} archivos...")
            
            for filename in archivos_nuevos:
                shutil.copy2(os.path.join(origen, filename), os.path.join(staging, filename))
                match = re.search(r'(\d{4})(\d{2})(\d{2})', filename)
                y, m, d = match.groups() if match else (datetime.now().strftime('%Y'), datetime.now().strftime('%m'), datetime.now().strftime('%d'))
                lista_fechas.append(f"{y}-{m}-{d}")
                lista_others.append(f"month:{MAPA_MESES.get(m, 'unknown')}")

            with Api(url, Authorization=key) as access_api:
                access_api.create(
                    type_option='resource', package_id=ds_id, upload=staging,
                    file_date=lista_fechas, others=tuple(lista_others),
                    file_type='Image', format='PNG', mimetype='image/png',
                    description="Manual Upload", max_count=len(archivos_nuevos) + 50
                )
            self.logger.info("✅ Fase 1 completada (Subida física).")

            self.logger.info("🔧 Fase 2: Actualizando descripciones (Patch)...")
            with Api(url, Authorization=key) as access_read:
                info = access_read.show(type_option='dataset', id=ds_id)
                recursos_server = info.get('resources', [])

            for res in recursos_server:
                if res.get('name') in archivos_nuevos:
                    r_id, r_name = res['id'], res['name']
                    match = re.search(r'(\d{4})(\d{2})(\d{2})', r_name)
                    fecha_bonita = f"{match.group(3)}/{match.group(2)}/{match.group(1)}" if match else "Desconocida"
                    final_desc = f"{user_description}. Date: {fecha_bonita}."
                    
                    with Api(url, Authorization=key) as access_patch:
                        access_patch.patch(type_option='resource', id=r_id, package_id=ds_id, description=final_desc)
                    self.logger.info(f"   📝 Patch aplicado: {r_name}")

            self.logger.info("👁️ Fase 3: Refrescando vistas del portal...")
            with Api(url, Authorization=key) as access_views:
                meta = access_views.show(type_option='dataset', id=ds_id)
                access_views.create(type_option='views', select='dataset', package=meta)
            
            self.logger.info("🏁 PROCESO FINALIZADO EXITOSAMENTE.")
            messagebox.showinfo("Éxito", "Todo se ha subido y configurado.")

        except Exception as e:
            self.logger.error(f"❌ ERROR CRÍTICO: {str(e)}")
        finally:
            if os.path.exists(staging): shutil.rmtree(staging)

    def start_manual_upload(self):
        selected = self.file_listbox.curselection()
        if not selected: return
        filenames = [self.file_listbox.get(i) for i in selected]
        desc = simpledialog.askstring("Descripción", "Escribe la descripción general para estos datos:", parent=self.root)
        if desc is not None:
            threading.Thread(target=self.upload_logic, args=(filenames, desc or "Sin descripción"), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = JROUploaderGUI(root)
    app.refresh_file_list()
    root.mainloop()
