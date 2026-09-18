#!/data/data/com.termux/files/usr/bin/python3
import sys
# Pojistka: ruční přidání systémové cesty pro jistotu
sys.path.append('/data/data/com.termux/files/usr/lib/python3.13/site-packages')

from waitress import serve
from app import app
import logging

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    logging.info("Startuji v globálním systému (bez venv)...")
    serve(app, host='0.0.0.0', port=5000, threads=6)
