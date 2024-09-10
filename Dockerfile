# Python imajını temel al
FROM python:3.12-slim

# Çalışma dizinini oluştur
WORKDIR /app

# Gereksinimler dosyasını kopyala ve kur
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Flask sunucusunu dışa aç
EXPOSE 5000

# Uygulamayı başlat - Gunicorn ile
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

