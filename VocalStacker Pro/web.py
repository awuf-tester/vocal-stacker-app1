import os
import uuid
from flask import Flask, request, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename

UPLOAD_DIR = os.path.join(os.getcwd(), "temp", "uploads")
EXPORT_DIR = os.path.join(os.getcwd(), "exports")
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXPORT_DIR, exist_ok=True)

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/upload", methods=["POST"])
def upload():
    if "file" not in request.files:
        return jsonify({"error": "no file part"}), 400
    f = request.files["file"]
    if f.filename == "":
        return jsonify({"error": "no selected file"}), 400
    filename = secure_filename(f.filename)
    dest = os.path.join(UPLOAD_DIR, filename)
    f.save(dest)
    return jsonify({"filename": filename, "path": dest})


@app.route("/download/<path:filename>", methods=["GET"])
def download(filename):
    safe = secure_filename(filename)
    full = os.path.join(EXPORT_DIR, safe)
    if not os.path.exists(full):
        abort(404)
    return send_from_directory(EXPORT_DIR, safe, as_attachment=True)


@app.route("/stack/mix", methods=["POST"])
def stack_mix():
    data = request.get_json(force=True)
    files = data.get("files", [])
    fmt = data.get("format", "wav")
    preset = data.get("preset", "Studio Quality")
    if not files:
        return jsonify({"error": "no files provided"}), 400
    try:
        from audio.stack import VocalStackEngine
        from audio.exporter import Exporter

        engine = VocalStackEngine()
        for f in files:
            path = os.path.join(UPLOAD_DIR, secure_filename(f))
            engine.add_track(path)

        mix, sr = engine.mix()
        out_name = f"mix_{uuid.uuid4().hex}.{fmt}"
        out_path = os.path.join(EXPORT_DIR, out_name)
        exporter = Exporter()
        exporter.export(mix, sr, out_path, format=fmt, preset=preset)
        return jsonify({"output": out_name, "path": out_path})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/separate", methods=["POST"])
def separate():
    data = request.get_json(force=True)
    filename = data.get("file")
    stems = data.get("stems", ["vocals", "drums", "bass", "other"])
    if not filename:
        return jsonify({"error": "no file provided"}), 400
    path = os.path.join(UPLOAD_DIR, secure_filename(filename))
    outdir = os.path.join(EXPORT_DIR, f"separated_{uuid.uuid4().hex}")
    try:
        from ai.separator import DemucsSeparator

        sep = DemucsSeparator()
        result = sep.separate(path, outdir, stems=stems)
        return jsonify({"result_dir": os.path.basename(outdir), "files": result})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


@app.route("/pitch/correct", methods=["POST"])
def pitch_correct():
    data = request.get_json(force=True)
    filename = data.get("file")
    strength = float(data.get("strength", 0.6))
    scale = data.get("scale", "Major")
    if not filename:
        return jsonify({"error": "no file provided"}), 400
    path = os.path.join(UPLOAD_DIR, secure_filename(filename))
    try:
        import soundfile as sf
        from ai.pitch_corrector import PitchCorrector
        from audio.exporter import Exporter

        audio, sr = sf.read(path)
        pc = PitchCorrector()
        corrected = pc.correct(audio, sr, strength=strength, scale=scale)
        out_name = f"pitch_corrected_{uuid.uuid4().hex}.wav"
        out_path = os.path.join(EXPORT_DIR, out_name)
        exporter = Exporter()
        exporter.export(corrected, sr, out_path, format="wav")
        return jsonify({"output": out_name, "path": out_path})
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
