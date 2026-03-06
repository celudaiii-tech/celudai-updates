import json
import os
import requests
from androguard.core.bytecodes.apk import APK

GITHUB_TOKEN = "TU_TOKEN"
REPO = "TU_USUARIO/TU_REPO"
FILE_PATH = "apps.json"
BRANCH = "main"

API_URL = f"https://api.github.com/repos/{REPO}/contents/{FILE_PATH}"

def leer_json():
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    r = requests.get(API_URL, headers=headers)

    if r.status_code == 200:
        data = r.json()
        contenido = json.loads(
            requests.utils.unquote(data["content"]).encode().decode("base64")
        )
        return contenido, data["sha"]
    else:
        return {"apps": [], "password": "1234"}, None


def guardar_json(contenido, sha):
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}

    payload = {
        "message": "Actualización desde panel admin",
        "content": contenido.encode().decode("base64"),
        "branch": BRANCH
    }

    if sha:
        payload["sha"] = sha

    r = requests.put(API_URL, json=payload, headers=headers)

    print("Respuesta GitHub:", r.status_code)
    print(r.text)


def leer_apk(ruta):
    try:
        apk = APK(ruta)

        nombre = apk.get_app_name()
        paquete = apk.get_package()

        return {
            "nombre": nombre,
            "paquete": paquete,
            "archivo": os.path.basename(ruta)
        }

    except Exception as e:
        print("No se pudo leer el APK:", e)
        return None


def agregar_apk(ruta):
    data, sha = leer_json()

    info = leer_apk(ruta)

    if info:
        data["apps"].append(info)

        nuevo_json = json.dumps(data, indent=4)

        guardar_json(nuevo_json, sha)

        print("APK agregado correctamente")


def cambiar_password(nueva):
    data, sha = leer_json()

    data["password"] = nueva

    nuevo_json = json.dumps(data, indent=4)

    guardar_json(nuevo_json, sha)

    print("Contraseña actualizada")


if __name__ == "__main__":

    while True:

        print("\n--- PANEL ADMIN ---")
        print("1 - Agregar APK")
        print("2 - Cambiar contraseña")
        print("3 - Salir")

        op = input("Opción: ")

        if op == "1":
            ruta = input("Ruta del APK: ")
            agregar_apk(ruta)

        elif op == "2":
            nueva = input("Nueva contraseña: ")
            cambiar_password(nueva)

        elif op == "3":
            break
