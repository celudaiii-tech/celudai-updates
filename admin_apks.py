import os
import json
import subprocess

REPO_URL = "https://github.com/celudaiii-tech/celudai-updates"
USER = "celudaiii-tech"
REPO = "celudai-updates"

APKS_DIR = "apks"

apps = []

for archivo in os.listdir(APKS_DIR):

    if archivo.endswith(".apk"):

        nombre = archivo.replace(".apk","")

        url = f"https://raw.githubusercontent.com/{USER}/{REPO}/main/apks/{archivo}"

        apps.append({
            "name": nombre,
            "package": nombre,
            "version": "1.0",
            "url": url
        })

data = {"apps": apps}

with open("update.json","w") as f:
    json.dump(data,f,indent=4)

print("update.json generado")

subprocess.run(["git","add","."])
subprocess.run(["git","commit","-m","update apps"])
subprocess.run(["git","push"])

print("APKs subidas correctamente")
