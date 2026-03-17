import json
import subprocess
import requests
import os
import zipfile
import time
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox

REPO = r"C:\CeludaiBUILD"
JSON_FILE = REPO + "\\update.json"

GITHUB_USER = "celudaiii-tech"
GITHUB_REPO = "celudai-updates"

# ---------------- TOKEN ----------------

def get_token():
    with open(REPO + "\\github_token.txt","r") as f:
        return f.read().strip()

TOKEN = get_token()

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ---------------- JSON ----------------

def load_json():
    try:
        with open(JSON_FILE,"r",encoding="utf8") as f:
            return json.load(f)
    except:
        return {
            "activation_password":"Celudai#2026!",
            "apps":[]
        }

data = load_json()

# ---------------- LEER APK ----------------

def read_apk():

    path = filedialog.askopenfilename(filetypes=[("APK","*.apk")])
    if not path:
        return None

    size = round(os.path.getsize(path)/1024/1024,2)

    package = "unknown.package"
    version = 1

    try:
        with zipfile.ZipFile(path,'r') as z:
            manifest = z.read("AndroidManifest.xml")

        manifest_str = manifest.decode(errors="ignore")

        if 'package="' in manifest_str:
            package = manifest_str.split('package="')[1].split('"')[0]

        if 'versionCode="' in manifest_str:
            version = int(manifest_str.split('versionCode="')[1].split('"')[0])

    except:
        pass

    name = os.path.basename(path).replace(".apk","")

    return path,name,package,version,size

# ---------------- CREAR RELEASE (DRAFT) ----------------

def create_release(package,version):

    timestamp = int(time.time())

    tag = f"app-{package}-{version}-{timestamp}"

    release_data = {
        "tag_name": tag,
        "name": tag,
        "body": "Celudai Store APK",
        "draft": True,   # 🔥 clave
        "prerelease": False
    }

    r = requests.post(
        f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases",
        headers=HEADERS,
        json=release_data
    )

    release = r.json()

    if "upload_url" not in release:
        raise Exception(str(release))

    return release

# ---------------- SUBIR APK ----------------

def upload_apk(apk_path, package, version):

    release = create_release(package,version)

    upload_url = release["upload_url"].split("{")[0]

    filename = package + ".apk"

    filesize = os.path.getsize(apk_path)

    headers = {
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/vnd.android.package-archive",
        "Content-Length": str(filesize)
    }

    progress_var.set("Subiendo APK...")

    with open(apk_path,"rb") as f:

        r = requests.post(
            upload_url + "?name=" + filename,
            headers=headers,
            data=f,
            timeout=None
        )

    if r.status_code not in [200,201]:
        raise Exception(r.text)

    # 🔥 PUBLICAR RELEASE (necesario para evitar immutable)
    requests.patch(
        f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/{release['id']}",
        headers=HEADERS,
        json={"draft": False}
    )

    asset = r.json()

    progress_var.set("Subida finalizada")

    return asset["browser_download_url"]

# ---------------- AGREGAR APP ----------------

def add_app():

    info = read_apk()
    if not info:
        return

    apk_path,name,package,version,size = info

    try:
        url = upload_apk(apk_path,package,version)
    except Exception as e:
        messagebox.showerror("Error",str(e))
        return

    existing = next((a for a in data["apps"] if a["package"] == package),None)

    if existing:
        existing["version"] = version
        existing["url"] = url
        existing["size"] = size
    else:
        data["apps"].append({
            "name": name,
            "package": package,
            "version": version,
            "size": size,
            "url": url,
            "added": datetime.now().strftime("%Y-%m-%d %H:%M")
        })

    refresh()

# ---------------- ELIMINAR APP ----------------

def delete_app():

    sel = listbox.curselection()

    if not sel:
        return

    data["apps"].pop(sel[0])

    refresh()

# ---------------- GUARDAR ----------------

def save():

    data["activation_password"] = password_entry.get()

    with open(JSON_FILE,"w",encoding="utf8") as f:
        json.dump(data,f,indent=4)

    subprocess.call(["git","-C",REPO,"add","."])
    subprocess.call(["git","-C",REPO,"commit","-m","Update Celudai apps"])
    subprocess.call(["git","-C",REPO,"push"])

    messagebox.showinfo("OK","Update.json subido")

# ---------------- REFRESH ----------------

def refresh():

    listbox.delete(0,END)

    for app in data["apps"]:
        listbox.insert(
            END,
            f"{app['name']} | {app['package']} | v{app['version']} | {app.get('size','?')} MB"
        )

# ---------------- UI ----------------

root = Tk()
root.title("Celudai Store Admin")
root.geometry("720x540")

Label(root,text="Contraseña de activación").pack()

password_entry = Entry(root,width=40)
password_entry.pack()
password_entry.insert(0,data["activation_password"])

Button(root,text="Agregar APK",command=add_app).pack(pady=8)
Button(root,text="Eliminar App",command=delete_app).pack()
Button(root,text="Guardar y Subir",command=save).pack(pady=10)

progress_var = StringVar()
Label(root,textvariable=progress_var).pack()

listbox = Listbox(root,width=110)
listbox.pack(fill="both",expand=True,pady=10)

refresh()

root.mainloop()