import os
import json
import subprocess
import requests
from datetime import datetime
from tkinter import *
from tkinter import filedialog, messagebox
from androguard.core.apk import APK

# ---------------- CONFIG ----------------

REPO_LOCAL = r"C:\CeludaiBUILD"
JSON_FILE = os.path.join(REPO_LOCAL, "update.json")
TOKEN_FILE = os.path.join(REPO_LOCAL, "github_token.txt")

GITHUB_REPO = "celudaiii-tech/celudai-updates"
RELEASE_TAG = "celudai-store"

# ---------------- TOKEN ----------------

def get_token():
    return open(TOKEN_FILE).read().strip()

TOKEN = get_token()

HEADERS = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github+json"
}

# ---------------- JSON ----------------

def load_json():

    if os.path.exists(JSON_FILE):
        return json.load(open(JSON_FILE,"r",encoding="utf8"))

    return {
        "activation_password":"Celudai#2026!",
        "apps":[]
    }

data = load_json()

# ---------------- APK INFO ----------------

def read_apk(path):

    apk = APK(path)

    package = apk.get_package()
    version = int(apk.get_androidversion_code())

    return package,version

# ---------------- RELEASE ----------------

def get_release():

    r = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/releases/tags/{RELEASE_TAG}",
        headers=HEADERS
    )

    if r.status_code == 200:
        return r.json()

    r = requests.post(
        f"https://api.github.com/repos/{GITHUB_REPO}/releases",
        headers=HEADERS,
        json={
            "tag_name": RELEASE_TAG,
            "name": "Celudai Store",
            "body": "APK repository",
            "draft": False,
            "prerelease": False
        }
    )

    if r.status_code not in [200,201]:
        raise Exception("Error creando release:\n"+str(r.json()))

    return r.json()

# ---------------- DELETE ASSET ----------------

def delete_asset(asset_id):

    requests.delete(
        f"https://api.github.com/repos/{GITHUB_REPO}/releases/assets/{asset_id}",
        headers=HEADERS
    )

# ---------------- UPLOAD APK ----------------

def upload_apk(path):

    release = get_release()

    upload_url = release["upload_url"].split("{")[0]
    assets = release["assets"]

    filename = os.path.basename(path)

    for asset in assets:
        if asset["name"] == filename:
            delete_asset(asset["id"])

    with open(path,"rb") as f:

        r = requests.post(
            f"{upload_url}?name={filename}",
            headers={
                "Authorization": f"token {TOKEN}",
                "Content-Type": "application/octet-stream"
            },
            data=f
        )

    if r.status_code not in [200,201]:
        raise Exception("Error subiendo APK:\n"+str(r.json()))

    res = r.json()

    if "browser_download_url" not in res:
        raise Exception("GitHub no devolvió URL:\n"+str(res))

    return res["browser_download_url"]

# ---------------- GIT ----------------

def git_sync():

    subprocess.call([
        "git","-C",REPO_LOCAL,
        "pull","origin","main","--rebase"
    ])

def git_push():

    subprocess.call(["git","-C",REPO_LOCAL,"add","."])
    subprocess.call(["git","-C",REPO_LOCAL,"commit","-m","Actualización automática Celudai"])
    subprocess.call(["git","-C",REPO_LOCAL,"push","origin","main"])

# ---------------- SAVE JSON ----------------

def save_json():

    data["activation_password"] = password_entry.get()

    with open(JSON_FILE,"w",encoding="utf8") as f:
        json.dump(data,f,indent=4)

    git_sync()
    git_push()

    messagebox.showinfo("OK","JSON actualizado y subido")

# ---------------- ADD APK ----------------

def add_apk():

    path = filedialog.askopenfilename(filetypes=[("APK","*.apk")])

    if not path:
        return

    try:

        package,version = read_apk(path)

        url = upload_apk(path)

        name = os.path.basename(path).replace(".apk","")

        existing = next((a for a in data["apps"] if a["package"] == package),None)

        if existing:

            existing["version"] = version
            existing["url"] = url

        else:

            data["apps"].append({
                "name": name,
                "package": package,
                "version": version,
                "url": url,
                "added": datetime.now().strftime("%Y-%m-%d %H:%M")
            })

        refresh()

        messagebox.showinfo("OK","APK subida correctamente")

    except Exception as e:

        messagebox.showerror("Error",str(e))

# ---------------- DELETE APP ----------------

def delete_app():

    sel = listbox.curselection()

    if not sel:
        return

    data["apps"].pop(sel[0])

    refresh()

# ---------------- LIST ----------------

def refresh():

    listbox.delete(0,END)

    for app in data["apps"]:
        listbox.insert(
            END,
            f"{app['name']} | {app['package']} | v{app['version']}"
        )

# ---------------- UI ----------------

root = Tk()
root.title("Celudai Store Admin")
root.geometry("550x520")

Label(root,text="Password activación").pack()

password_entry = Entry(root,width=40)
password_entry.pack()
password_entry.insert(0,data["activation_password"])

Button(root,text="Agregar APK",command=add_apk).pack(pady=10)

Button(root,text="Eliminar app",command=delete_app).pack()

Button(root,text="Guardar / Subir",command=save_json).pack(pady=10)

listbox = Listbox(root,width=70)
listbox.pack(fill="both",expand=True,pady=10)

refresh()

root.mainloop()