from flask import Flask
from zk_routes import zk_bp

app = Flask(__name__)
app.register_blueprint(zk_bp)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=False)
