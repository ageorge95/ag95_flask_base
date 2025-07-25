from flask import (Flask,
                   url_for)
from markupsafe import Markup
from waitress import serve
from .routes import BLUEPRINTS

class Server:
    def __init__(self):
        self.flask = Flask(__name__, static_folder=None)

        # register every collected blueprint
        for bp in BLUEPRINTS:
            self.flask.register_blueprint(bp)

        # root route (no blueprint)
        @self.flask.route("/")
        def root_index():
            links = []
            for rule in self.flask.url_map.iter_rules():
                # skip the rule we are generating right now
                if rule.endpoint == "root_index":
                    continue
                href = url_for(rule.endpoint,
                               **{p: f"<{p}>" for p in rule.arguments})
                text = f"{rule.rule}  ({rule.endpoint})"
                links.append(f'<li><a href="{href}">{text}</a></li>')
            html = "<h1>Registered routes</h1><ul>{}</ul>".format("".join(links))
            return Markup(html)

    def serve(self, host="0.0.0.0", port=5000):
        serve(self.flask, host=host, port=port)