FROM python:3.11-slim

# Instalar ffmpeg, nodejs (motor JS para descifrado de YouTube) y dependencias
RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg curl ca-certificates nodejs && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar requerimientos e instalar gunicorn y dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar el resto del código
COPY . .

# Crear carpeta de descargas con permisos
RUN mkdir -p downloads

ENV PORT=5000
EXPOSE 5000

# Ejecutar con gunicorn en producción
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "300", "app:app"]
