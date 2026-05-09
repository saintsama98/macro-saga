import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from minimacro import api  # noqa: E402

SAMPLES_DIR = ROOT / "samples"

app = Flask(__name__, static_folder="static", template_folder="templates")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/api/process")
def process():
    payload = request.get_json(silent=True) or {}
    source = payload.get("source", "")
    return jsonify(api.process(source))


@app.get("/api/sample/<name>")
def sample(name: str):
    file_map = {"sample": "sample.mac", "errors": "sample_errors.mac"}
    if name not in file_map:
        return jsonify({"error": "unknown sample"}), 404
    path = SAMPLES_DIR / file_map[name]
    if not path.exists():
        return jsonify({"error": "sample file missing"}), 404
    return jsonify({"source": path.read_text()})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
