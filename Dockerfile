# Imagen base Python 3.11 slim
FROM python:3.11-slim

# Instala LibreOffice headless para conversión Word→PDF\RUN apt-get update && apt-get install -y \
    libreoffice-writer libreoffice-core libreoffice-common libreoffice-python3 \
    && rm -rf /var/lib/apt/lists/*

# Directorio de trabajo dentro del contenedor
WORKDIR /app

# Copia e instala dependencias Python\COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia el resto del proyecto (app.py, templates/)
COPY . .

# Puerto por defecto (Render inyecta $PORT automáticamente)
EXPOSE 10000

# Arranque con Gunicorn usando la variable PORT, fallback a 10000\CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]