import os
from datetime import timedelta
from dotenv import load_dotenv

# Načtení proměnných z .env souboru
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
    # Bezpečnostní klíče
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(32).hex()
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)
    
    # Databáze Slepého notáře
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'inloopid_blind_notary.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # MojeID OIDC Konfigurace
    MOJEID_CLIENT_ID = os.environ.get('MOJEID_CLIENT_ID')
    MOJEID_CLIENT_SECRET = os.environ.get('MOJEID_CLIENT_SECRET')
