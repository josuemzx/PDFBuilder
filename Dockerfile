# Imagen base Python 3.11 slim
FROM python:3.11-slim

# Instalamos LibreOffice headless y Java para LibreOffice
RUN apt-get update && \
    apt-get install -y \
        libreoffice-writer \
        libreoffice-core \
        libreoffice-common \
        default-jre-headless && \
    rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiamos dependencias e instalamos
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos la aplicación y templates
COPY . ./

# Exponemos puerto (Render inyecta $PORT automáticamente)
EXPOSE 10000

# Arrancamos con Gunicorn, timeout 600s
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --timeout 600 app:app"]