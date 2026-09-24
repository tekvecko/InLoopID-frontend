import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
os.environ['AUTHLIB_INSECURE_TRANSPORT'] = '1'

from flask import Flask
from flask_cors import CORS
from models import db
from extensions import migrate
from config import Config

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {
        "origins": ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "http://127.0.0.1:3000"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"]
    }}, supports_credentials=True)

    app.config.from_object(Config)
    app.secret_key = os.environ.get('SECRET_KEY', 'vyvojovy_klic_pro_termux_inloopid_123')
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['SESSION_COOKIE_SECURE'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    from zk_routes import zk_bp
    from passkey_routes import passkey_bp
    from routes import api_bp
    from hr_routes import hr_bp
    from mojeid_routes import auth_bp
    from b2b_routes import b2b_bp
    from verifier_gateway_routes import verifier_bp
    from hr_compliance import hr_compliance_bp

    app.register_blueprint(zk_bp)
    app.register_blueprint(passkey_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(hr_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(b2b_bp)
    app.register_blueprint(verifier_bp)
    app.register_blueprint(hr_compliance_bp)

    with app.app_context():
        db.create_all()

    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        return response

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)
