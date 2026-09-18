FROM python:3.13-slim

WORKDIR /opt/inloopid/backend

# Security: Vytvoření neprivilegovaného uživatele pro běh služby
RUN useradd -m -s /bin/bash inloopid_service

# Instalace Python závislostí
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt waitress

# Kopírování aplikační logiky
COPY . .
RUN chown -R inloopid_service:inloopid_service /opt/inloopid

USER inloopid_service
EXPOSE 5000

CMD ["python3", "start_prod.py"]
