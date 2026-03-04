import os
import json
import shutil
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, filedialog, Listbox, END, messagebox
from apkutils import APK  # pip install apkutils-patch
import subprocess

# ---------------- Configuración ----------------
APK_FOLDER = "apks"
JSON_FILE = "update.json"
TOKEN_FILE = "github_token.txt"  # aquí el cliente debe poner su token personal

if not os.path.exists(APK_FOLDER):
    os.makedirs(APK_FOLDER)

# Cargar JSON existente o crear vacío
if os.path.exists(JSON_FILE):
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {"apps": []}

# ---------------- Funciones principales ----------------
def save_json(push_to_github=False):
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    refresh_listbox()
    if push_to_github:
        push_json_to_github()

def add_app():
    apk_path = filedialog.askopenfilename(filetypes=[("APK Files", "*.apk")])
    if not apk_path:
        return

    title = entry_title.get().strip()
    if not title:
        messagebox.showerror("Error", "Ingresa un título administrativo")
        return

    try:
        apk_obj = APK(apk_path)
        package_name = apk_obj.manifest.package_name
        version = int(apk_obj.manifest.version_code)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo leer APK:\n{e}")
        return

    existing = next((app for app in data["apps"] if app["name"] == title), None)
    if existing:
        existing["package"] = package_name
        existing["version"] = version
        shutil.copy(apk_path, os.path.join(APK_FOLDER, f"{title}.apk"))
    else:
        shutil.copy(apk_path, os.path.join(APK_FOLDER, f"{title}.apk"))
        data["apps"].append({
            "name": title,
            "package": package_name,
            "version": version,
            "url": f"{APK_FOLDER}/{title}.apk",
            "added": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    save_json()

def delete_app():
    selection = listbox.curselection()
    if not selection:
        return
    index = selection[0]
    title = data["apps"][index]["name"]

    if messagebox.askyesno("Confirmar", f"Eliminar {title}?"):
        apk_file = os.path.join(APK_FOLDER, f"{title}.apk")
        if os.path.exists(apk_file):
            os.remove(apk_file)
        data["apps"].pop(index)
        save_json()

def refresh_listbox():
    listbox.delete(0, END)
    for app in data["apps"]:
        listbox.insert(END, f"{app['name']} (v{app['version']})")

def push_json_to_github():
    if not os.path.exists(TOKEN_FILE):
        messagebox.showwarning("GitHub", f"No se encontró {TOKEN_FILE}. No se hará push.")
        return
    with open(TOKEN_FILE, "r", encoding="utf-8") as f:
        token = f.read().strip()

    try:
        subprocess.run(["git", "config", "user.name", "CeludaiUpdater"], check=True)
        subprocess.run(["git", "config", "user.email", "celudai@example.com"], check=True)
        subprocess.run(["git", "add", JSON_FILE], check=True)

        diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
        if diff.returncode != 0:
            subprocess.run(["git", "commit", "-m", "Actualización automática de apps"], check=True)
            repo_url = get_remote_url()
            if repo_url:
                secure_url = repo_url.replace("https://", f"https://{token}@")
                subprocess.run(["git", "push", secure_url, "main"], check=True)
                messagebox.showinfo("GitHub", "JSON actualizado en GitHub correctamente")
            else:
                messagebox.showwarning("GitHub", "No se encontró URL remota para push")
    except subprocess.CalledProcessError as e:
        messagebox.showerror("GitHub", f"Error al hacer push: {e}")

def get_remote_url():
    try:
        result = subprocess.run(["git", "remote", "get-url", "origin"], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

# ---------------- GUI ----------------
root = Tk()
root.title("Celudai Updater Admin")
root.geometry("500x450")

Label(root, text="Título administrativo:").pack(pady=5)
entry_title = Entry(root, width=50)
entry_title.pack(pady=5)

Button(root, text="Agregar / Actualizar APK", command=add_app).pack(pady=5)
Button(root, text="Eliminar app", command=delete_app).pack(pady=5)
Button(root, text="Guardar JSON y push a GitHub", command=lambda: save_json(push_to_github=True)).pack(pady=5)

Label(root, text="Apps cargadas:").pack(pady=5)
listbox = Listbox(root, width=70)
listbox.pack(pady=5, fill="both", expand=True)

refresh_listbox()
root.mainloop()