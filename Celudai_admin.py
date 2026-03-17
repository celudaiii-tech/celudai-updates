import json
import subprocess
import requests
import os
import zipfile
import time
import threading
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

# ---------------- APK ----------------

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

# ---------------- GITHUB ----------------

def create_release(package,version):

    tag = f"app-{package}-{version}-{int(time.time())}"

    r = requests.post(
        f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases",
        headers=HEADERS,
        json={
            "tag_name": tag,
            "name": tag,
            "body": "Celudai Store APK",
            "draft": True
        },
        timeout=60
    )

    release = r.json()

    if "upload_url" not in release:
        raise Exception(str(release))

    return release

def upload_apk(apk_path, package, version):

    release = create_release(package,version)
    upload_url = release["upload_url"].split("{")[0]

    filename = package + ".apk"

    progress_var.set("Subiendo APK...")

    for intento in range(3):

        try:
            with open(apk_path, "rb") as f:

                def gen():
                    while True:
                        chunk = f.read(1024 * 1024)  # 1MB
                        if not chunk:
                            break
                        yield chunk

                r = requests.post(
                    upload_url + "?name=" + filename,
                    headers={
                        "Authorization": f"token {TOKEN}",
                        "Content-Type": "application/vnd.android.package-archive"
                    },
                    data=gen(),
                    timeout=300
                )

            if r.status_code in [200,201]:

                # publicar release
                requests.patch(
                    f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/{release['id']}",
                    headers=HEADERS,
                    json={"draft": False},
                    timeout=60
                )

                asset = r.json()

                if "browser_download_url" not in asset:
                    raise Exception("No se obtuvo URL de descarga")

                return asset["browser_download_url"]

            else:
                raise Exception(r.text)

        except Exception as e:
            progress_var.set(f"Reintentando... ({intento+1}/3)")
            time.sleep(3)

    raise Exception("Falló la subida después de 3 intentos")

# ---------------- APP ----------------

def add_app():

    info = read_apk()
    if not info:
        return

    apk_path,name,package,version,size = info

    try:
        url = upload_apk(apk_path,package,version)
    except Exception as e:
        messagebox.showerror("Error subida",str(e))
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
    messagebox.showinfo("OK","APK subido correctamente")

def add_app_thread():
    threading.Thread(target=add_app).start()

def delete_app():

    sel = listbox.curselection()
    if not sel:
        return

    data["apps"].pop(sel[0])
    refresh()

def save():

    data["activation_password"] = password_entry.get()

    with open(JSON_FILE,"w",encoding="utf8") as f:
        json.dump(data,f,indent=4)

    subprocess.call(["git","-C",REPO,"add","."])
    subprocess.call(["git","-C",REPO,"commit","-m","Update"])
    subprocess.call(["git","-C",REPO,"push"])

    messagebox.showinfo("OK","Update.json subido")

def refresh():

    listbox.delete(0,END)

    for app in data["apps"]:
        listbox.insert(
            END,
            f"{app['name']} | {app['package']} | v{app['version']}"
        )

# ---------------- UI ----------------

root = Tk()
root.title("Celudai Admin")
root.geometry("700x520")

Label(root,text="Password").pack()

password_entry = Entry(root,width=40)
password_entry.pack()
password_entry.insert(0,data["activation_password"])

Button(root,text="Agregar APK",command=add_app_thread).pack(pady=8)
Button(root,text="Eliminar",command=delete_app).pack()
Button(root,text="Guardar",command=save).pack(pady=10)

progress_var = StringVar()
Label(root,textvariable=progress_var).pack()

listbox = Listbox(root,width=100)
listbox.pack(fill="both",expand=True)

refresh()

root.mainloop()