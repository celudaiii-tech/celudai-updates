import os
import json
import shutil
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, filedialog, Listbox, END, messagebox
from apkutils import APK
import subprocess

# ---------------- Configuración ----------------
APK_FOLDER = "apks"
JSON_FILE = "update.json"
<<<<<<< HEAD
CONFIG_FILE = "config.json"
=======
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1

if not os.path.exists(APK_FOLDER):
    os.makedirs(APK_FOLDER)

<<<<<<< HEAD
# ---------------- Leer configuración ----------------
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        config = json.load(f)
        GITHUB_TOKEN = config["github_token"]
        REPO = config["repo"]
else:
    messagebox.showerror("Error", "No se encontró config.json")
    exit()

# ---------------- Cargar JSON ----------------
=======
# Cargar JSON existente o crear estructura inicial
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {
        "activation_password": "Celudai#2026!",
        "apps": []
    }

<<<<<<< HEAD
=======
# Si el JSON viejo no tenía contraseña, la agregamos
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
if "activation_password" not in data:
    data["activation_password"] = "Celudai#2026!"

# ---------------- Funciones principales ----------------
def save_json(push_to_github=False):
<<<<<<< HEAD

=======
    # Guardar contraseña actual desde la interfaz
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
    data["activation_password"] = password_entry.get()

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    refresh_listbox()

    if push_to_github:
        push_to_github_repo()

def add_app():
<<<<<<< HEAD

=======
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
    apk_path = filedialog.askopenfilename(filetypes=[("APK Files", "*.apk")])
    if not apk_path:
        return

    title = entry_title.get().strip()
<<<<<<< HEAD

=======
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
    if not title:
        messagebox.showerror("Error", "Ingresa un título administrativo")
        return

    try:
        apk_obj = APK(apk_path)
        package_name = apk_obj.manifest.package_name
        version = int(apk_obj.manifest.version_code)
<<<<<<< HEAD

=======
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer APK:\n{e}")
        return

    existing = next((app for app in data["apps"] if app["name"] == title), None)

    shutil.copy(apk_path, os.path.join(APK_FOLDER, f"{title}.apk"))

    if existing:
<<<<<<< HEAD

        existing["package"] = package_name
        existing["version"] = version
        existing["url"] = f"{APK_FOLDER}/{title}.apk"

    else:

=======
        existing["package"] = package_name
        existing["version"] = version
        existing["url"] = f"{APK_FOLDER}/{title}.apk"
    else:
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
        data["apps"].append({
            "name": title,
            "package": package_name,
            "version": version,
            "url": f"{APK_FOLDER}/{title}.apk",
            "added": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    save_json(push_to_github=True)

def delete_app():
<<<<<<< HEAD

    selection = listbox.curselection()

=======
    selection = listbox.curselection()
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
    if not selection:
        return

    index = selection[0]
    title = data["apps"][index]["name"]

    if messagebox.askyesno("Confirmar", f"Eliminar {title}?"):
<<<<<<< HEAD

        apk_file = os.path.join(APK_FOLDER, f"{title}.apk")

=======
        apk_file = os.path.join(APK_FOLDER, f"{title}.apk")
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
        if os.path.exists(apk_file):
            os.remove(apk_file)

        data["apps"].pop(index)
<<<<<<< HEAD

        save_json(push_to_github=True)

def refresh_listbox():

    listbox.delete(0, END)

=======
        save_json(push_to_github=True)

def refresh_listbox():
    listbox.delete(0, END)
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
    for app in data["apps"]:
        listbox.insert(END, f"{app['name']} (v{app['version']})")

# ---------------- PUSH AUTOMÁTICO ----------------
def push_to_github_repo():
<<<<<<< HEAD

    try:

        repo_url = f"https://{GITHUB_TOKEN}@github.com/{REPO}.git"

        subprocess.run(["git", "init"], check=True)

        subprocess.run(["git", "remote", "remove", "origin"], stderr=subprocess.DEVNULL)

        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)

=======
    try:
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
        subprocess.run(["git", "config", "user.name", "CeludaiUpdater"], check=True)
        subprocess.run(["git", "config", "user.email", "celudai@example.com"], check=True)

        subprocess.run(["git", "add", "."], check=True)

        diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
<<<<<<< HEAD

        if diff.returncode != 0:

            subprocess.run(["git", "commit", "-m", "Actualización automática"], check=True)
            subprocess.run(["git", "branch", "-M", "main"], check=True)
            subprocess.run(["git", "push", "-u", "origin", "main"], check=True)

            messagebox.showinfo("Sistema", "Cambios subidos a GitHub")

        else:

            messagebox.showinfo("Sistema", "No hay cambios")

    except subprocess.CalledProcessError as e:

        messagebox.showerror("Error", f"No se pudo subir:\n{e}")
=======
        if diff.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Actualización automática"], check=True)
            subprocess.run(["git", "push", "origin", "main"], check=True)
            messagebox.showinfo("Sistema", "Cambios guardados correctamente")
        else:
            messagebox.showinfo("Sistema", "No hay cambios para guardar")

    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"No se pudo guardar:\n{e}")
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1

# ---------------- GUI ----------------
root = Tk()
root.title("Celudai Updater Admin")
root.geometry("520x520")

<<<<<<< HEAD
=======
# 🔐 CONTRASEÑA DE ACTIVACIÓN
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
Label(root, text="Contraseña de activación:").pack(pady=(10, 0))

password_entry = Entry(root, width=50)
password_entry.pack(pady=5)
password_entry.insert(0, data["activation_password"])

Label(root, text="Título administrativo:").pack(pady=5)

entry_title = Entry(root, width=50)
entry_title.pack(pady=5)

Button(root, text="Agregar / Actualizar APK", command=add_app).pack(pady=5)
Button(root, text="Eliminar app", command=delete_app).pack(pady=5)
Button(root, text="Guardar", command=lambda: save_json(push_to_github=True)).pack(pady=5)

Label(root, text="Apps cargadas:").pack(pady=5)

listbox = Listbox(root, width=70)
listbox.pack(pady=5, fill="both", expand=True)

refresh_listbox()
<<<<<<< HEAD

=======
>>>>>>> ca9a48ecb955d3926ee3cd51b00e4d0af9e06fd1
root.mainloop()