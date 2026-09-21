#!/usr/bin/env bash
set -e

# Aktivace virtuálního prostředí
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "Chyba: Adresář venv nenalezen!"
    exit 1
fi

echo "=== 1. Cílené ukončování starých procesů Celery a Flask ==="
pkill -9 -f "celery worker" || true
pkill -9 -f "python app.py" || true

echo "=== 2. Úprava celery_app.py (Izolovaná konfigurace Redisu + solo pool) ==="
if [ -f celery_app.py ]; then
    cp celery_app.py celery_app.py.bak
fi

cat << 'INNER_EOF' > celery_app.py
import os
from celery import Celery

broker_url = os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0')
result_backend = os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')

celery = Celery(
    'inloopid_tasks',
    broker=broker_url,
    backend=result_backend,
    include=['tasks']
)

celery.conf.update(
    broker_connection_retry_on_startup=True,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    worker_pool='solo'
)

if __name__ == '__main__':
    celery.start()
INNER_EOF

echo "=== 3. Úprava app.py (Import Celery bez cirkulární závislosti) ==="
if [ -f app.py ]; then
    cp app.py app.py.bak
fi

cat << 'INNER_EOF' > app.py
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask
from flask_cors import CORS
from models import db
from extensions import migrate
from authlib.integrations.flask_client import OAuth

# Importujeme konfigurovaný celery objekt z celery_app
from celery_app import celery

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}}, supports_credentials=True)

    # Načtení centrální konfigurace
    from config import Config
    app.config.from_object(Config)

    app.secret_key = os.environ.get('SECRET_KEY', 'vyvojovy_klic_pro_termux_inloopid_123')
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False

    oauth = OAuth(app)
    oauth.register(
        name='mojeid',
        client_id=os.environ.get('MOJEID_CLIENT_ID'),
        client_secret=os.environ.get('MOJEID_CLIENT_SECRET'),
        server_metadata_url='https://mojeid.regtest.nic.cz/.well-known/openid-configuration',
        client_kwargs={'scope': 'openid profile email'}
    )
    app.config['OAUTH_REGISTRY'] = oauth

    db.init_app(app)
    migrate.init_app(app, db)

    # Lokální importy pro zamezení cirkulárních závislostí
    from routes import api_bp
    from hr_routes import hr_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(hr_bp)

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self' http://localhost:*; script-src 'self'; style-src 'self'; connect-src 'self' http://localhost:* ws://localhost:*;"
        return response

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
INNER_EOF

echo "=== Patch úspěšně aplikován! ==="
