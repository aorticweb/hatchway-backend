from flask import Flask, request

from app import config
from app.helpers import get_posts, param_validation

app = Flask(__name__)


@app.route("/api/ping/")
def ping():
    return {"success": True}, 200

@app.route("/api/posts")
def posts():
    tags = request.args.get("tags", "")
    sort_by = request.args.get("sortBy", config.DEFAULT_SORT)
    direction = request.args.get("direction", config.DEFAULT_DIRECTION)
    has_err, err = param_validation(tags, sort_by, direction)
    if has_err:
        return {"error": err}, 400
    posts = get_posts(tags, sort_by, direction)
    return {"posts": posts}, 200
