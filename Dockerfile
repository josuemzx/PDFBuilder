# Imagen base Python 3.11 slim
FROM python:3.11-slim

# Instalamos LibreOffice headless para conversión Word→PDF y Java para LibreOffice
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

# Puerto genérico, Render inyecta $PORT
EXPOSE 10000

# Arrancamos con Gunicorn, timeout extendido a 600s, usando $PORT o 10000 por defecto
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} --timeout 600 app:app"]
```dockerfile
# Imagen base Python 3.11 slim
FROM python:3.11-slim

# Instalamos LibreOffice headless para conversión Word→PDF
RUN apt-get update && \
    apt-get install -y \
        libreoffice-writer \
        libreoffice-core \
        libreoffice-common && \
    rm -rf /var/lib/apt/lists/*

# Directorio de trabajo
WORKDIR /app

# Copiamos dependencias e instalamos
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos la aplicación y templates
COPY . ./

# Puerto genérico, Render inyecta $PORT
EXPOSE 10000

# Arrancamos con Gunicorn, usando $PORT o 10000 por defecto
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-10000} app:app"]