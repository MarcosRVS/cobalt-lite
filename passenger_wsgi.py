import sys
import os
import traceback

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

# Detectar e incluir automáticamente los site-packages del entorno virtual de cPanel
HOME_DIR = os.path.expanduser("~")
VENV_DIR = os.path.join(HOME_DIR, "virtualenv")
if os.path.exists(VENV_DIR):
    for root, dirs, _ in os.walk(VENV_DIR):
        if "site-packages" in dirs:
            site_packages_path = os.path.join(root, "site-packages")
            if site_packages_path not in sys.path:
                sys.path.insert(0, site_packages_path)

try:
    from app import app
    application = app
except Exception:
    error_info = traceback.format_exc()
    sys_paths = "\n".join(sys.path)

    def application(environ, start_response):
        status = '500 Internal Server Error'
        html = f"""<!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Diagnóstico - Cobalt Lite</title>
            <style>
                body {{ background: #0c0d11; color: #f87171; font-family: monospace; padding: 2rem; }}
                .box {{ background: #171922; border: 1px solid #374151; border-radius: 8px; padding: 1rem; color: #f3f4f6; overflow-x: auto; margin-bottom: 1.5rem; }}
                h2 {{ color: #ef4444; }}
            </style>
        </head>
        <body>
            <h2>Error al iniciar la aplicación (Traceback)</h2>
            <div class="box"><pre>{error_info}</pre></div>
            <h3>sys.path:</h3>
            <div class="box"><pre>{sys_paths}</pre></div>
        </body>
        </html>
        """
        output = html.encode('utf-8')
        response_headers = [
            ('Content-Type', 'text/html; charset=utf-8'),
            ('Content-Length', str(len(output)))
        ]
        start_response(status, response_headers)
        return [output]
