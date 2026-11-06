# 🚀 Cobalt Lite — Descargador Privado de Medios

<div align="center">
  <p>Una alternativa ligera, privada y sin publicidad inspirada en el diseño minimalista de <strong>cobalt.tools</strong>.</p>
  <p>Descarga video y audio de YouTube de forma directa a tu dispositivo sin pasar por servicios de terceros ni rastreadores.</p>
</div>

---

## ✨ Características

- 🎯 **Interfaz fiel a Cobalt**: Diseño minimalista, modo oscuro nativo, tarjetas de vista previa (título, canal, duración y miniatura) y soporte para pegar con un clic o presionar <kbd>Enter</kbd>.
- 🎵 **Extracción de Audio**:
  - **MP3** (192 kbps de alta fidelidad, con FFmpeg).
  - **M4A / AAC** (audio original sin pérdida por recodificación).
  - **Opus**.
- 🎬 **Descarga de Video**:
  - **1080p (Full HD)** con unión de pistas de alta calidad vía FFmpeg.
  - **720p (HD)** y **480p**.
- 🔒 **100% Privado y Seguro**:
  - Soporte de **clave de acceso privada** configurable en `config.json` para evitar que personas no autorizadas usen tu servidor.
  - **Limpieza automática** de archivos temporales en el servidor tras cada descarga o por temporizador de caducidad (20 min).
- 🍪 **Bypass anti-bot**: Soporte integrado para `cookies.txt` en caso de despliegues en centros de datos con IPs bloqueadas por YouTube.
- ⚡ **Multiplataforma**: Funciona tanto en **local en Windows/Linux/Mac**, como en la nube (**Docker, Render.com, Railway**) y en **cPanel con Python WSGI**.

---

## 🛠️ Tecnologías

- **Backend**: Python 3.10+, [Flask](https://flask.palletsprojects.com/), [yt-dlp](https://github.com/yt-dlp/yt-dlp), Gunicorn.
- **Procesamiento Multimedia**: [FFmpeg](https://ffmpeg.org/).
- **Frontend**: HTML5, [Tailwind CSS](https://tailwindcss.com/) (CDN), [Lucide Icons](https://lucide.dev/).
- **Despliegue**: Docker, Passenger WSGI (cPanel), o servidor de desarrollo local.

---

## 💻 Uso en Local (Tu PC)

Correr la app en tu propia computadora es la mejor opción: tu conexión residencial de internet evita cualquier bloqueo de YouTube y FFmpeg procesa las descargas a máxima velocidad.

### En Windows (con lanzador rápido):
Haz doble clic en:
```text
iniciar_cobalt.bat
```
Se abrirá automáticamente tu navegador en `http://localhost:5000`.

### Desde la terminal:
```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar servidor
python app.py
```
Abre en tu navegador: `http://localhost:5000`

---

## ☁️ Despliegue en la Nube (Render.com / Docker)

El repositorio incluye un `Dockerfile` listo para producción que instala automáticamente `ffmpeg` y `gunicorn`.

1. Haz un fork o sube este repositorio a tu cuenta de **GitHub**.
2. Entra a [Render.com](https://render.com) e inicia sesión con GitHub.
3. Haz clic en **New +** > **Web Service**.
4. Conecta este repositorio (`cobalt-lite`).
5. Render detectará automáticamente el entorno **Docker**.
6. Selecciona el plan **Free** y pulsa **Create Web Service**.
7. En un par de minutos tendrás tu propia URL pública con certificado SSL HTTPS gratis.

---

## ⚙️ Configuración (`config.json`)

En la raíz del proyecto puedes personalizar el archivo `config.json`:

```json
{
    "access_key": "MiClaveSecreta123",
    "cleanup_minutes": 20
}
```

- **`access_key`**: Si está vacía (`""`), cualquier persona que entre a la web puede descargar. Si pones una clave, los usuarios deberán ingresar esa clave en el botón de la llave 🔑 de la interfaz para poder procesar descargas.
- **`cleanup_minutes`**: Minutos que se conservan los archivos temporales descargados en el servidor antes de ser eliminados automáticamente.

---

## 🍪 Solución a bloqueos anti-bot en la nube (`cookies.txt`)

Si despliegas en un servidor en la nube y YouTube responde con:
> *"Sign in to confirm you're not a bot"*

1. En tu navegador habitual instala la extensión de código abierto **Get cookies.txt LOCALLY**.
2. Abre YouTube con tu cuenta activa.
3. Exporta las cookies y guarda el archivo en la raíz del proyecto como `cookies.txt`.
4. La app detectará el archivo automáticamente y autenticará las peticiones de descarga.

---

## 📄 Licencia y Descargo de Responsabilidad

Este software es para uso estrictamente personal, privado y educativo. Respeta siempre los términos de servicio de las plataformas de contenido y los derechos de autor de los creadores.
