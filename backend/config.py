import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

# Základní absolutní adresář pro backend
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

# Zajištění absolutní cesty k SQLite databázi
default_db_path = os.path.join(basedir, 'inloopid_blind_notary.db')
database_url = os.environ.get('DATABASE_URL')

if not database_url:
    database_url = f'sqlite:///{default_db_path}'

class Config:
    # Bezpečnostní klíče
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(32).hex()
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    # Databáze Slepého notáře (vždy absolutní cesta)
    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # MojeID OIDC Konfigurace
    MOJEID_CLIENT_ID = os.environ.get('MOJEID_CLIENT_ID')
    MOJEID_CLIENT_SECRET = os.environ.get('MOJEID_CLIENT_SECRET')
