from flask import Flask
from waitress import serve
from .routes import BLUEPRINTS

class Server:
    def __init__(self):
        self.flask = Flask(__name__)

        # register every collected blueprint
        for bp in BLUEPRINTS:
            self.flask.register_blueprint(bp)

    def serve(self, host="0.0.0.0", port=5000):
        serve(self.flask, host=host, port=port)