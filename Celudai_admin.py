import os
import sys
import json
import subprocess
import shutil
import requests
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox

# ---------------- CONFIG ----------------

REPO_LOCAL = r"C:\CeludaiBUILD"

APK_FOLDER = os.path.join(REPO_LOCAL, "apks")
JSON_FILE = os.path.join(REPO_LOCAL, "update.json")

GITHUB_USER = "celudaiii-tech"
GITHUB_REPO = "celudai-updates"
RELEASE_TAG = "apps"

TOKEN_FILE = os.path.join(REPO_LOCAL, "github_token.txt")

with open(TOKEN_FILE, "r") as f:
    GITHUB_TOKEN = f.read().strip()

if not os.path.exists(APK_FOLDER):
    os.makedirs(APK_FOLDER)

# ---------------- CARGAR JSON ----------------

def load_json():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except:
                return {"activation_password": "Celudai#2026!", "apps": []}
    return {"activation_password": "Celudai#2026!", "apps": []}

data = load_json()

# ---------------- LEER APK ----------------

try:
    from androguard.core.apk import APK
except ImportError:
    messagebox.showerror("Error", "Instala androguard: pip install androguard")
    sys.exit(1)

def read_apk(apk_path):
    apk = APK(apk_path)
    package = apk.get_package()
    version = apk.get_androidversion_code()

    if not package or not version:
        raise Exception("No se pudo leer package o version")

    return str(package), int(version)

# ---------------- GIT ----------------

def git_pull():
    subprocess.call(["git", "-C", REPO_LOCAL, "pull", "origin", "main"])

def git_push():
    subprocess.call(["git", "-C", REPO_LOCAL, "add", "."])
    subprocess.call(["git", "-C", REPO_LOCAL, "commit", "-m", "Actualización automática Celudai"])
    subprocess.call(["git", "-C", REPO_LOCAL, "push", "origin", "main"])

# ---------------- RELEASE ----------------

def get_release():

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json"
    }

    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}"

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        data = r.json()
        if "upload_url" in data:
            return data

    # crear release si no existe
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases"

    release_data = {
        "tag_name": RELEASE_TAG,
        "name": "Celudai Apps",
        "draft": False,
        "prerelease": False
    }

    r = requests.post(url, headers=headers, json=release_data)

    data = r.json()

    if "upload_url" not in data:
        raise Exception(f"Error creando release: {data}")

    return data

def upload_to_release(apk_path):

    release = get_release()

    upload_url = release["upload_url"].split("{")[0]

    filename = os.path.basename(apk_path)

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/vnd.android.package-archive"
    }

    with open(apk_path, "rb") as f:

        r = requests.post(
            f"{upload_url}?name={filename}",
            headers=headers,
            data=f
        )

    if r.status_code not in [200, 201]:
        raise Exception(f"Error subiendo APK: {r.text}")

# ---------------- AGREGAR APK ----------------

def add_apk():

    apk_path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])

    if not apk_path:
        return

    try:

        package, version = read_apk(apk_path)

        filename = os.path.basename(apk_path)

        destino = os.path.join(APK_FOLDER, filename)

        shutil.copy2(apk_path, destino)

        upload_to_release(destino)

        url = f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}/releases/download/{RELEASE_TAG}/{filename}"

        nombre = filename.replace(".apk", "")

        existing = next((a for a in data["apps"] if a["package"] == package), None)

        if existing:
            existing.update({
                "version": version,
                "url": url,
                "name": nombre
            })
        else:
            data["apps"].append({
                "name": nombre,
                "package": package,
                "version": version,
                "url": url,
                "added": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

        refresh_list()

        messagebox.showinfo("Celudai", "APK subida correctamente al Release")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# ---------------- ELIMINAR ----------------

def delete_app():

    seleccion = listbox.curselection()

    if not seleccion:
        return

    index = seleccion[0]

    data["apps"].pop(index)

    refresh_list()

# ---------------- GUARDAR ----------------

def save():

    data["activation_password"] = password_entry.get()

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    git_push()

    messagebox.showinfo("Sistema", "JSON actualizado y subido a GitHub")

# ---------------- ACTUALIZAR ----------------

def update():

    git_pull()

    global data

    data = load_json()

    password_entry.delete(0, END)

    password_entry.insert(0, data.get("activation_password", ""))

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

Button(root, text="Agregar APK", command=add_apk).pack(pady=10)

Button(root, text="Eliminar APP", command=delete_app).pack(pady=5)

Button(root, text="Guardar (push)", command=save).pack(pady=10)

Button(root, text="Actualizar desde GitHub", command=update).pack(pady=5)

Label(root, text="Apps cargadas").pack()

listbox = Listbox(root, width=75)
listbox.pack(pady=10, fill="both", expand=True)

refresh_list()

root.mainloop()