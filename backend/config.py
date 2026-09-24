import os
import sqlite3
from datetime import timedelta
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

default_db_path = os.path.join(basedir, 'inloopid_blind_notary.db')
database_url = os.environ.get('DATABASE_URL', f'sqlite:///{default_db_path}')

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.urandom(32).hex()
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or os.urandom(32).hex()
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=2)

    SQLALCHEMY_DATABASE_URI = database_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Zcela obejdeme výchozí poolovací mechanismus SQLAlchemy a vynutíme přímý sqlite3 ovladač
    SQLALCHEMY_ENGINE_OPTIONS = {
        "creator": lambda: sqlite3.connect(default_db_path)
    }

    MOJEID_CLIENT_ID = os.environ.get('MOJEID_CLIENT_ID')
    MOJEID_CLIENT_SECRET = os.environ.get('MOJEID_CLIENT_SECRET')
