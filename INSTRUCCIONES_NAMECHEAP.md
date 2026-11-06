# Guía de Instalación en Namecheap cPanel (Hosting Stellar)

Esta webapp está diseñada para ejecutarse como aplicación **Python WSGI (Phusion Passenger)** directamente en cPanel sin requerir Docker ni permisos de root.

---

## Paso 1: Crear la Aplicación Python en cPanel

1. Inicia sesión en tu **cPanel de Namecheap**.
2. En la sección **Software**, haz clic en **"Setup Python App"**.
3. Haz clic en el botón azul **"Create Application"**.
4. Llena los campos:
   * **Python version**: Selecciona `3.10` o `3.11`.
   * **Application root**: `cobalt-lite`
   * **Application URL**: Tu subdominio o dominio (ej. `cobalt.tudominio.com`).
   * **Application startup file**: `passenger_wsgi.py`
   * **Application Entry point**: `application`
5. Haz clic en **"Create"**.

---

## Paso 2: Subir los Archivos

1. En cPanel, abre el **"File Manager"** (Administrador de Archivos).
2. Entra a la carpeta de la app (`cobalt-lite/`).
3. Sube y extrae el archivo `cobalt-lite.zip`.

---

## Paso 3: Instalar Dependencias

Abre la **Terminal** de cPanel:
1. Copia el comando que cPanel muestra arriba de "Setup Python App" (que empieza por `source /home/.../activate`) y ejecútalo en la terminal.
2. Ejecuta:
   ```bash
   pip install Flask yt-dlp requests
   ```
3. Vuelve a "Setup Python App" y pulsa **Restart**.
