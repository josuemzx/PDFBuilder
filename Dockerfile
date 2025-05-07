FROM python:3.11-slim

# Instala LibreOffice headless y dependencias
RUN apt-get update && apt-get install -y \
    libreoffice-writer libreoffice-core libreoffice-common libreoffice-python3 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 10000
CMD ["gunicorn", "--bind", "0.0.0.0:10000", "app:app"]
