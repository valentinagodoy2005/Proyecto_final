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
            password="",            # La contraseña que configuraste
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

# Función para realizar un backup sin usar mysqldump
def perform_backup():
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    db_host = config['DATABASE']['host']
    db_user = config['DATABASE']['user']
    db_password = config['DATABASE']['password']
    db_name = config['DATABASE']['database']
    
    backup_file = f"{db_name}_backup.sql"
    backup_file_path = os.path.join(os.getcwd(), backup_file)

    try:
        conn = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        cursor = conn.cursor()

        # Extraer todas las tablas de la base de datos
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        with open(backup_file_path, 'w') as f:
            for table in tables:
                table_name = table[0]

                # Crear el esquema de la tabla
                cursor.execute(f"SHOW CREATE TABLE {table_name}")
                create_table_query = cursor.fetchone()[1]
                f.write(f"{create_table_query};\n\n")

                # Extraer los datos de la tabla
                cursor.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()

                # Escribir los datos en formato INSERT INTO
                if rows:
                    f.write(f"INSERT INTO {table_name} VALUES\n")
                    for row in rows:
                        f.write(f"{str(row)};\n")
                    f.write("\n\n")

        cursor.close()
        conn.close()

        messagebox.showinfo("Backup", f"Backup realizado y guardado en: {backup_file_path}")

    except mysql.connector.Error as err:
        messagebox.showerror("Error", f"Error al realizar el backup: {err}")

# Función para programar backups según la frecuencia seleccionada
def schedule_backup():
    backup_frequency = backup_var.get()
    if backup_frequency == "24 horas":
        interval = 86400  # 24 horas en segundos
    elif backup_frequency == "7 días":
        interval = 604800  # 7 días en segundos
    elif backup_frequency == "30 días":
        interval = 2592000  # 30 días en segundos
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

# Botón para generar el backup ahora
tk.Button(root, text="Generar Backup Ahora", command=perform_backup).grid(row=6, column=0, columnspan=10, pady=20)

# Iniciar el bucle principal de la aplicación
root.mainloop()
