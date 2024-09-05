import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
import configparser
from threading import Timer
import os

# Función para conectarse a la base de datos y obtener las bases de datos disponibles
def get_databases():
    try:
        conn = mysql.connector.connect(
            host="localhost",       # Si la base de datos está en tu computadora
            user="root",            # Usuario por defecto si no creaste otro
            password="",  # La contraseña que configuraste
        )
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        databases = [db[0] for db in cursor.fetchall()]
        cursor.close()
        conn.close()
        return databases
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al conectar con la base de datos: {err}")
        return []

# Función para mostrar las bases de datos en el combobox
def show_databases():
    databases = get_databases()
    if databases:
        db_combo['values'] = databases
        db_combo.current(0)
    else:
        db_combo.set("No hay bases de datos disponibles")

# Función para guardar la configuración
def save_config():
    config = configparser.ConfigParser()
    config['DATABASE'] = {
        'host': host_var.get(),
        'user': user_var.get(),
        'password': password_var.get(),
        'database': db_combo.get(),
        'backup_frequency': backup_var.get()
    }
    with open('config.ini', 'w') as configfile:
        config.write(configfile)
    messagebox.showinfo("Guardar configuración", "Configuración guardada correctamente")

# Función para realizar un backup (esta es una versión simplificada)
def perform_backup():
    config = configparser.ConfigParser()
    config.read('config.ini')
    db = config['DATABASE']['database']
    backup_file = f"{db}_backup.sql"
    
    # Aquí se realiza el backup utilizando mysqldump
    try:
        conn = mysql.connector.connect(
            host=config['DATABASE']['host'],
            user=config['DATABASE']['user'],
            password=config['DATABASE']['password'],
            database=db
        )
        cursor = conn.cursor()
        with open(backup_file, 'w') as f:
            for line in conn.cmd_query_iter(f"BACKUP DATABASE {db} TO '{backup_file}'"):
                f.write(line)
        messagebox.showinfo("Backup", f"Backup de la base de datos '{db}' realizado correctamente")
        cursor.close()
        conn.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al realizar el backup: {err}")

# Función para programar backups según la frecuencia seleccionada
def schedule_backup():
    backup_frequency = backup_var.get()
    if backup_frequency == "24 horas":
        interval = 86400
    elif backup_frequency == "7 días":
        interval = 604800
    elif backup_frequency == "30 días":
        interval = 2592000
    else:
        return
    
    perform_backup()
    Timer(interval, schedule_backup).start()

# Crear la ventana principal
root = tk.Tk()
root.title("Programador de Backups")

# Variables
host_var = tk.StringVar()
user_var = tk.StringVar()
password_var = tk.StringVar()
backup_var = tk.StringVar(value="24 horas")

# Campos de entrada
tk.Label(root, text="Host:").grid(row=0, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=host_var).grid(row=0, column=1, padx=10, pady=5)

tk.Label(root, text="Usuario:").grid(row=1, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=user_var).grid(row=1, column=1, padx=10, pady=5)

tk.Label(root, text="Contraseña:").grid(row=2, column=0, padx=10, pady=5)
tk.Entry(root, textvariable=password_var, show="*").grid(row=2, column=1, padx=10, pady=5)

# Botón para guardar la configuración
tk.Button(root, text="Guardar Configuración", command=save_config).grid(row=3, column=0, columnspan=2, pady=10)

# Botón para mostrar las bases de datos
tk.Button(root, text="Mostrar Bases de Datos", command=show_databases).grid(row=3, column=2, columnspan=2, pady=10)

# Combobox para seleccionar la base de datos
tk.Label(root, text="Base de Datos:").grid(row=4, column=0, padx=10, pady=5)
db_combo = ttk.Combobox(root)
db_combo.grid(row=4, column=1, padx=10, pady=5)

# Opciones de frecuencia de backups
tk.Label(root, text="Frecuencia de Backup:").grid(row=5, column=0, padx=10, pady=5)
backup_options = ["24 horas", "7 días", "30 días", "Nunca"]
backup_menu = ttk.OptionMenu(root, backup_var, backup_options[0], *backup_options)
backup_menu.grid(row=5, column=1, padx=10, pady=5)

# Botón para guardar la configuración
tk.Button(root, text="Generar Backup Ahora", command=perform_backup).grid(row=6, column=0, columnspan=10, pady=20)

def perform_backup():
    config = configparser.ConfigParser()
    config.read('config.ini')
    db = config['DATABASE']['database']
    backup_file = f"{db}_backup.sql"
    
    # Ruta completa del archivo de backup
    backup_file_path = os.path.join(os.getcwd(), backup_file)
    
    try:
        # Ejecutar el comando mysqldump para realizar el backup
        os.system(f"mysqldump -h {config['DATABASE']['host']} -u {config['DATABASE']['user']} -p{config['DATABASE']['password']} {db} > {backup_file_path}")
        print(f"Backup realizado y guardado en: {backup_file_path}")
    except Exception as e:
        print(f"Error al realizar el backup: {e}")

# Llamada a la función
perform_backup()

# Iniciar el bucle principal de la aplicación
root.mainloop()
