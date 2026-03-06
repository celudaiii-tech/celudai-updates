import os
import json
import shutil
import subprocess
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from apkutils2 import APK
import requests

# ---------------- CONFIG ----------------
REPO_LOCAL = r"C:\Users\Diego\Desktop\CeludaiADMIN"
APK_FOLDER = os.path.join(REPO_LOCAL, "apks")
JSON_FILE = os.path.join(REPO_LOCAL, "update.json")

REMOTE_JSON_URL = "https://raw.githubusercontent.com/celudaiii-tech/celudai-updates/main/update.json"

if not os.path.exists(APK_FOLDER):
    os.makedirs(APK_FOLDER)

# ---------------- CARGAR JSON ----------------
def cargar_json():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return {
            "activation_password": "Celudai#2026!",
            "apps": []
        }

data = cargar_json()

# ---------------- LEER APK ----------------
def leer_apk(apk_path):
    try:
        apk = APK.from_file(apk_path)

        package = apk.manifest.package_name
        version = apk.manifest.version_code

        if not package or not version:
            raise Exception("No se pudo detectar package o version")

        return str(package), int(version)

    except Exception as e:
        raise Exception(f"No se pudo leer el APK\n{str(e)}")

# ---------------- GIT ----------------
def git_commit_push(message):
    try:
        subprocess.check_call(["git", "-C", REPO_LOCAL, "add", "."])
        subprocess.check_call(["git", "-C", REPO_LOCAL, "commit", "-m", message])
        subprocess.check_call(["git", "-C", REPO_LOCAL, "push"])
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error Git", str(e))

# ---------------- GUARDAR ----------------
def guardar():
    try:
        data["activation_password"] = password_entry.get()

        with open(JSON_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        git_commit_push("Actualización Celudai")

        messagebox.showinfo("Sistema", "Guardado y subido a GitHub")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- ACTUALIZAR ----------------
def actualizar():
    try:
        r = requests.get(REMOTE_JSON_URL)

        if r.status_code != 200:
            raise Exception("No se pudo descargar update.json")

        global data
        data = r.json()

        password_entry.delete(0, END)
        password_entry.insert(0, data.get("activation_password", ""))

        refresh_list()

        messagebox.showinfo("Sistema", "Datos actualizados desde GitHub")

    except Exception as e:
        messagebox.showerror("Error", f"No se pudo actualizar:\n{str(e)}")

# ---------------- AGREGAR APK ----------------
def agregar():
    apk_path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])

    if not apk_path:
        return

    try:
        package, version = leer_apk(apk_path)

    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    nombre_admin = os.path.basename(apk_path).replace(".apk", "")
    destino = os.path.join(APK_FOLDER, f"{nombre_admin}.apk")

    shutil.copy(apk_path, destino)

    url_apk = f"apks/{nombre_admin}.apk"

    existing = next((a for a in data["apps"] if a["package"] == package), None)

    if existing:
        existing["version"] = version
        existing["url"] = url_apk
        existing["name"] = nombre_admin
    else:
        data["apps"].append({
            "name": nombre_admin,
            "package": package,
            "version": version,
            "url": url_apk,
            "added": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    refresh_list()

# ---------------- ELIMINAR ----------------
def eliminar():
    seleccion = listbox.curselection()

    if not seleccion:
        messagebox.showwarning("Atención", "Selecciona una APP")
        return

    index = seleccion[0]
    app = data["apps"][index]
    nombre = app["name"]

    confirmar = messagebox.askyesno("Confirmar", f"¿Eliminar {nombre}?")

    if not confirmar:
        return

    apk_path = os.path.join(APK_FOLDER, f"{nombre}.apk")

    if os.path.exists(apk_path):
        os.remove(apk_path)

    data["apps"].pop(index)

    refresh_list()

# ---------------- LISTA ----------------
def refresh_list():
    listbox.delete(0, END)

    for app in data["apps"]:
        listbox.insert(END, f"{app['name']} | {app['package']} | v{app['version']}")

# ---------------- GUI ----------------
root = Tk()
root.title("Celudai Admin")
root.geometry("540x520")

Label(root, text="Contraseña de activación").pack(pady=5)

password_entry = Entry(root, width=50)
password_entry.pack()

password_entry.insert(0, data.get("activation_password", ""))

Button(root, text="Agregar / Actualizar APK", command=agregar).pack(pady=10)
Button(root, text="Eliminar APP", command=eliminar).pack(pady=5)
Button(root, text="Guardar (subir a Git)", command=guardar).pack(pady=10)
Button(root, text="Actualizar desde nube", command=actualizar).pack(pady=5)

Label(root, text="Apps cargadas").pack()

listbox = Listbox(root, width=75)
listbox.pack(pady=10, fill="both", expand=True)

refresh_list()

root.mainloop()
