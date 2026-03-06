from flask import Flask, send_from_directory, jsonify
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
APPS_DIR = os.path.join(BASE_DIR, "apps")

@app.route("/")
def index():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(BASE_DIR, path)

@app.route("/api/apps")
def list_apps():
    apps = []

    if not os.path.exists(APPS_DIR):
        return jsonify(apps)

    for folder in os.listdir(APPS_DIR):
        app_path = os.path.join(APPS_DIR, folder)

        if os.path.isdir(app_path):
            info_file = os.path.join(app_path, "app.json")

            if os.path.exists(info_file):
                with open(info_file, "r", encoding="utf-8") as f:
                    import json
                    data = json.load(f)
                    apps.append(data)

    return jsonify(apps)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
