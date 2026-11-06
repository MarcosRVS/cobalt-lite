import os
import sys
import glob
import time
import shutil
import uuid
import json
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, after_this_request

app = Flask(__name__)

# Directorios base
BASE_DIR = Path(__file__).resolve().parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DOWNLOAD_DIR.mkdir(exist_ok=True)

CONFIG_FILE = BASE_DIR / "config.json"
COOKIES_FILE = BASE_DIR / "cookies.txt"

def load_config():
    default_config = {
        "access_key": "",          # Si está vacío no pide clave. Si tiene texto, se requiere para descargar.
        "cleanup_minutes": 20      # Elimina automáticamente archivos temporales con más de 20 min
    }
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_config.update(data)
        except Exception:
            pass
    else:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(default_config, f, indent=4)
    return default_config

def check_env_cookies():
    env_cookies = os.environ.get("YOUTUBE_COOKIES", "").strip()
    if env_cookies and len(env_cookies) > 20:
        try:
            with open(COOKIES_FILE, "w", encoding="utf-8") as f:
                f.write(env_cookies)
        except Exception:
            pass

def has_valid_cookies():
    check_env_cookies()
    if not COOKIES_FILE.exists():
        return False
    try:
        if COOKIES_FILE.stat().st_size < 30:
            return False
        with open(COOKIES_FILE, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read(2048)
            # Solo consideramos cookies si tienen formato Netscape o dominios de YouTube tabulados
            return ("Netscape HTTP Cookie File" in content or "\tyoutube.com\t" in content or "\t.youtube.com\t" in content)
    except Exception:
        return False

def find_ffmpeg():
    # 1. System PATH
    system_ffmpeg = shutil.which("ffmpeg")
    if system_ffmpeg:
        return system_ffmpeg
    
    # 2. Rutas locales o de usuario
    candidates = [
        BASE_DIR / "ffmpeg",
        BASE_DIR / "ffmpeg.exe",
        BASE_DIR / "bin" / "ffmpeg",
        Path.home() / "bin" / "ffmpeg",
        Path.home() / ".local" / "bin" / "ffmpeg",
        Path("/usr/local/bin/ffmpeg"),
        Path("/usr/bin/ffmpeg")
    ]
    for candidate in candidates:
        if candidate.exists() and (os.access(candidate, os.X_OK) or sys.platform.startswith("win")):
            return str(candidate)
    return None

def cleanup_old_files():
    config = load_config()
    max_age_seconds = config.get("cleanup_minutes", 20) * 60
    now = time.time()
    for item in DOWNLOAD_DIR.iterdir():
        if item.is_file():
            try:
                if now - item.stat().st_mtime > max_age_seconds:
                    item.unlink(missing_ok=True)
            except Exception:
                pass

def verify_auth(req):
    config = load_config()
    required_key = config.get("access_key", "").strip()
    if not required_key:
        return True
    
    provided_key = req.headers.get("X-Access-Key")
    if not provided_key and req.is_json:
        provided_key = req.json.get("key")
    if not provided_key:
        provided_key = req.args.get("key")
        
    return provided_key == required_key

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/status", methods=["GET"])
def server_status():
    ffmpeg_path = find_ffmpeg()
    has_cookies = has_valid_cookies()
    config = load_config()
    requires_auth = bool(config.get("access_key", "").strip())

    import yt_dlp
    return jsonify({
        "status": "ok",
        "has_ffmpeg": bool(ffmpeg_path),
        "ffmpeg_path": ffmpeg_path if ffmpeg_path else "No detectado (descargas limitadas a formatos nativos)",
        "has_cookies": has_cookies,
        "requires_auth": requires_auth,
        "yt_dlp_version": yt_dlp.version.__version__
    })

@app.route("/api/info", methods=["POST"])
def get_info():
    cleanup_old_files()
    if not verify_auth(request):
        return jsonify({"error": "Clave de acceso no válida o ausente."}), 401
    
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Debes proporcionar una URL válida."}), 400

    import yt_dlp

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "extract_flat": False,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "mweb", "web"]
            }
        },
    }

    if has_valid_cookies():
        ydl_opts["cookiefile"] = str(COOKIES_FILE)

    ffmpeg_path = find_ffmpeg()
    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = str(Path(ffmpeg_path).parent)

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
            duration_sec = info.get("duration", 0) or 0
            if duration_sec >= 3600:
                hours = duration_sec // 3600
                mins = (duration_sec % 3600) // 60
                secs = duration_sec % 60
                duration_str = f"{hours}:{mins:02d}:{secs:02d}"
            else:
                mins = duration_sec // 60
                secs = duration_sec % 60
                duration_str = f"{mins}:{secs:02d}"

            return jsonify({
                "title": info.get("title", "Video"),
                "uploader": info.get("uploader", "Desconocido"),
                "thumbnail": info.get("thumbnail", ""),
                "duration": duration_str,
                "duration_raw": duration_sec,
                "url": url
            })
    except Exception as e:
        err_msg = str(e)
        if "Sign in to confirm you're not a bot" in err_msg:
            return jsonify({
                "error": "YouTube bloqueó la IP ('Sign in to confirm you\\'re not a bot'). Añade un archivo 'cookies.txt' válido para resolverlo."
            }), 403
        return jsonify({"error": f"Error al procesar el enlace: {err_msg}"}), 400

@app.route("/api/download", methods=["POST"])
def download_media():
    cleanup_old_files()
    if not verify_auth(request):
        return jsonify({"error": "Clave de acceso no válida."}), 401

    data = request.get_json() or {}
    url = data.get("url", "").strip()
    mode = data.get("mode", "video") # "video" o "audio"
    audio_format = data.get("audio_format", "mp3") # mp3, m4a, opus
    video_quality = data.get("video_quality", "auto") # auto, 1080, 720, 480

    if not url:
        return jsonify({"error": "URL requerida."}), 400

    import yt_dlp

    download_id = str(uuid.uuid4())[:8]
    output_template = str(DOWNLOAD_DIR / f"{download_id}_%(title).100s.%(ext)s")

    ffmpeg_path = find_ffmpeg()
    ydl_opts = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "restrictfilenames": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android", "ios", "mweb", "web"]
            }
        },
    }

    if has_valid_cookies():
        ydl_opts["cookiefile"] = str(COOKIES_FILE)

    if ffmpeg_path:
        ydl_opts["ffmpeg_location"] = str(Path(ffmpeg_path).parent)

    if mode == "audio":
        if ffmpeg_path and audio_format == "mp3":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        elif ffmpeg_path and audio_format == "opus":
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "opus",
            }]
        else:
            # m4a nativo sin recodificación
            ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
    else:
        # Modo video
        if ffmpeg_path:
            if video_quality == "1080":
                ydl_opts["format"] = "bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]"
            elif video_quality == "720":
                ydl_opts["format"] = "bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=720]+bestaudio/best[height<=720]"
            elif video_quality == "480":
                ydl_opts["format"] = "bestvideo[height<=480]+bestaudio/best[height<=480]"
            else:
                ydl_opts["format"] = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"
            ydl_opts["merge_output_format"] = "mp4"
        else:
            # Flujos progresivos
            if video_quality == "720":
                ydl_opts["format"] = "best[height<=720][ext=mp4]/best[ext=mp4]/best"
            elif video_quality == "480":
                ydl_opts["format"] = "best[height<=480][ext=mp4]/best[ext=mp4]/best"
            else:
                ydl_opts["format"] = "best[ext=mp4]/best"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        matching_files = list(DOWNLOAD_DIR.glob(f"{download_id}_*"))
        if not matching_files:
            return jsonify({"error": "No se pudo generar el archivo descargado."}), 500

        target_file = matching_files[0]
        original_name = target_file.name.replace(f"{download_id}_", "")

        return jsonify({
            "status": "ready",
            "file_id": target_file.name,
            "filename": original_name,
            "size_bytes": target_file.stat().st_size
        })

    except Exception as e:
        err_msg = str(e)
        if "Sign in to confirm you're not a bot" in err_msg:
            return jsonify({
                "error": "Bloqueo anti-bot de YouTube. Si estás en hosting, añade cookies.txt válidas."
            }), 403
        return jsonify({"error": f"Error durante la descarga: {err_msg}"}), 500

@app.route("/api/fetch/<filename>", methods=["GET"])
def fetch_file(filename):
    safe_name = os.path.basename(filename)
    file_path = DOWNLOAD_DIR / safe_name
    
    if not file_path.exists() or not file_path.is_file():
        return "Archivo no encontrado o expirado.", 404

    @after_this_request
    def remove_file(response):
        try:
            file_path.unlink(missing_ok=True)
        except Exception:
            pass
        return response

    clean_display = safe_name
    parts = safe_name.split("_", 1)
    if len(parts) > 1 and len(parts[0]) == 8:
        clean_display = parts[1]

    return send_file(
        file_path,
        as_attachment=True,
        download_name=clean_display
    )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
