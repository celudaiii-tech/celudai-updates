import json
import subprocess
from datetime import datetime
from tkinter import *
from tkinter import filedialog, simpledialog, messagebox
from androguard.core.apk import APK

REPO = r"C:\CeludaiBUILD"
JSON_FILE = REPO + "\\update.json"

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

    apk = APK(path)

    package = apk.get_package()
    version = int(apk.get_androidversion_code())
    name = path.split("/")[-1].replace(".apk","")

    return name,package,version

# ---------------- AGREGAR APP ----------------

def add_app():

    info = read_apk()
    if not info:
        return

    name,package,version = info

    url = simpledialog.askstring(
        "Link APK",
        "Pegá el link del APK (Mediafire / servidor / CDN)"
    )

    if not url:
        return

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

# ---------------- GUARDAR ----------------

def save():

    data["activation_password"] = password_entry.get()

    with open(JSON_FILE,"w",encoding="utf8") as f:
        json.dump(data,f,indent=4)

    subprocess.call(["git","-C",REPO,"add","."])
    subprocess.call(["git","-C",REPO,"commit","-m","Actualización apps Celudai"])
    subprocess.call(["git","-C",REPO,"push"])

    messagebox.showinfo("OK","Update.json actualizado y subido")

# ---------------- ELIMINAR APP ----------------

def delete_app():

    sel = listbox.curselection()

    if not sel:
        return

    data["apps"].pop(sel[0])

    refresh()

# ---------------- REFRESH LISTA ----------------

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
root.geometry("620x520")

Label(root,text="Contraseña de activación").pack()

password_entry = Entry(root,width=40)
password_entry.pack()
password_entry.insert(0,data["activation_password"])

Button(root,text="Agregar APK",command=add_app).pack(pady=10)

Button(root,text="Eliminar App",command=delete_app).pack()

Button(root,text="Guardar y Subir",command=save).pack(pady=10)

listbox = Listbox(root,width=85)
listbox.pack(fill="both",expand=True,pady=10)

refresh()

root.mainloop()