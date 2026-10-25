import os
from flask import (Flask,
                   url_for)
from markupsafe import (Markup,
                        escape)
from waitress import serve
from ag95 import export_html_templates
from .routes import (load_all_blueprints,
                     BLUEPRINTS)

class Server:
    def __init__(self):
        self.flask = Flask(__name__, static_folder=None)

        # export ag95 templates
        export_html_templates(os.path.join(os.path.dirname(__file__), 'templates'))

        # collect and load blueprints
        load_all_blueprints()

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

                text = escape(f"{rule.rule}  ({rule.endpoint})")
                if rule.arguments:
                    # url_for() validates the route converters. A literal
                    # placeholder is invalid for <int:...>, <float:...>, etc.,
                    # so show parameterized routes as text instead of links.
                    links.append(f"<li><code>{text}</code></li>")
                else:
                    href = escape(url_for(rule.endpoint))
                    links.append(f'<li><a href="{href}">{text}</a></li>')
            html = "<h1>Registered routes</h1><ul>{}</ul>".format("".join(links))
            return Markup(html)

    def serve(self, host="0.0.0.0", port=5000):
        serve(self.flask, host=host, port=port,
              threads=8)