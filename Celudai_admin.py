import os
import sys
import json
import subprocess
import requests
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox

# -------- CONFIG --------
REPO_LOCAL = r"C:\CeludaiBUILD"
APK_FOLDER = os.path.join(REPO_LOCAL, "apks")
JSON_FILE = os.path.join(REPO_LOCAL, "update.json")

# GitHub
GITHUB_TOKEN = "PON_AQUI_TU_TOKEN"
REPO_OWNER = "celudaiii-tech"
REPO_NAME = "celudai-updates"
RELEASE_TAG = "apps"

if not os.path.exists(APK_FOLDER):
    os.makedirs(APK_FOLDER)

# -------- GITHUB RELEASE --------
def get_or_create_release():
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/tags/{RELEASE_TAG}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    r = requests.get(url, headers=headers)

    if r.status_code == 200:
        return r.json()

    data = {
        "tag_name": RELEASE_TAG,
        "name": "Celudai Apps",
        "draft": False,
        "prerelease": False
    }

    r = requests.post(
        f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases",
        headers=headers,
        json=data
    )

    return r.json()

# -------- SUBIR APK A RELEASE --------
def subir_a_github(apk_path):

    release = get_or_create_release()
    release_id = release["id"]

    name = os.path.basename(apk_path)

    url = f"https://uploads.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases/{release_id}/assets?name={name}"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Content-Type": "application/vnd.android.package-archive"
    }

    with open(apk_path, "rb") as f:
        r = requests.post(url, headers=headers, data=f)

    if r.status_code not in (200, 201):
        raise Exception("Error subiendo APK a GitHub")

    return r.json()["browser_download_url"]

# -------- CARGAR JSON --------
def cargar_json():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"activation_password": "Celudai#2026!", "apps": []}

data = cargar_json()

# -------- LEER APK --------
try:
    from androguard.core.apk import APK
except ImportError:
    messagebox.showerror("Error", "Androguard no está instalado.\nEjecuta: pip install androguard")
    sys.exit(1)

def leer_apk(apk_path):

    apk = APK(apk_path)

    package = apk.get_package()
    version = apk.get_androidversion_code()

    if not package or not version:
        raise Exception("No se pudo detectar package o version")

    return str(package), int(version)

# -------- GIT --------
def git_pull():
    subprocess.call(["git", "-C", REPO_LOCAL, "pull", "origin", "main"])

def git_push():

    subprocess.call(["git", "-C", REPO_LOCAL, "add", "update.json"])

    subprocess.call([
        "git",
        "-C",
        REPO_LOCAL,
        "commit",
        "-m",
        "Actualización Celudai JSON"
    ])

    subprocess.call(["git", "-C", REPO_LOCAL, "push", "origin", "main"])

# -------- GUARDAR --------
def guardar():

    data["activation_password"] = password_entry.get()

    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    git_push()

    messagebox.showinfo("Sistema", "JSON actualizado y subido a GitHub")

# -------- ACTUALIZAR --------
def actualizar():

    git_pull()

    global data
    data = cargar_json()

    password_entry.delete(0, END)
    password_entry.insert(0, data.get("activation_password", ""))

    refresh_list()

# -------- AGREGAR APK --------
def agregar():

    apk_path = filedialog.askopenfilename(filetypes=[("APK", "*.apk")])

    if not apk_path:
        return

    try:
        package, version = leer_apk(apk_path)
    except Exception as e:
        messagebox.showerror("Error", str(e))
        return

    try:
        url = subir_a_github(apk_path)
    except Exception as e:
        messagebox.showerror("GitHub", str(e))
        return

    nombre = os.path.basename(apk_path).replace(".apk", "")

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

# -------- ELIMINAR --------
def eliminar():

    seleccion = listbox.curselection()

    if not seleccion:
        messagebox.showwarning("Atención", "Selecciona una APP")
        return

    index = seleccion[0]

    data["apps"].pop(index)

    refresh_list()

# -------- LISTA --------
def refresh_list():

    listbox.delete(0, END)

    for app in data["apps"]:
        listbox.insert(END, f"{app['name']} | {app['package']} | v{app['version']}")

# -------- GUI --------
root = Tk()
root.title("Celudai Admin")
root.geometry("540x520")

Label(root, text="Contraseña de activación").pack(pady=5)

password_entry = Entry(root, width=50)
password_entry.pack()

password_entry.insert(0, data.get("activation_password", ""))

Button(root, text="Agregar / Actualizar APK", command=agregar).pack(pady=10)
Button(root, text="Eliminar APP", command=eliminar).pack(pady=5)
Button(root, text="Guardar (push)", command=guardar).pack(pady=10)
Button(root, text="Actualizar desde GitHub", command=actualizar).pack(pady=5)

Label(root, text="Apps cargadas").pack()

listbox = Listbox(root, width=75)
listbox.pack(pady=10, fill="both", expand=True)

refresh_list()

root.mainloop()