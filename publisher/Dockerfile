# Użycie lekkiego obrazu z Pythonem
FROM python:3.11-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Kopiowanie plików do kontenera
COPY requirements.txt .
COPY publisher.py .

# Instalowanie zależności
RUN pip install --no-cache-dir -r requirements.txt

#Wylaczenie buforowania pythonowego
ENV PYTHONUNBUFFERED=1

# Uruchomienie publishera
ENTRYPOINT ["python", "publisher.py"]