# Partimos de la imagen base de Python
FROM python:3.11-slim

# Instalamos LibreOffice headless para conversión Word→PDF\ n# (comentario separado de la instrucción RUN)
RUN apt-get update && \
    apt-get install -y libreoffice-writer libreoffice-core libreoffice-common libreoffice-python3 && \
    rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiamos dependencias e instalamos
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos la aplicación y plantillas
COPY . ./

# Exponemos un puerto genérico (Render inyecta $PORT)
EXPOSE 10000

# Arrancamos con Gunicorn, usando $PORT o fallback a 10000
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]