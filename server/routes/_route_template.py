import json
from flask import (Blueprint,
                   request,
                   jsonify)
from ._loader import register_route

ROUTE_NAME = 'my_route_name'
ROUTE_PREFIX = '/my_route_url_prefix'

# @register_route
def build():
    bp = Blueprint(ROUTE_NAME, __name__, url_prefix=ROUTE_PREFIX)

    @bp.route("/", methods=["GET", "POST"])
    def route_builder():
        with open('configuration.json', 'r') as f:
            config = json.load(f)

        # merge query-string args and JSON body (if any)
        data = dict(request.args)           # ?a=1&b=2 → {"a":"1","b":"2"}
        if request.is_json:
            data.update(request.get_json(silent=True) or {})
        return jsonify(['I received your call, here are the parameters that you have sent:', data])

    return bp