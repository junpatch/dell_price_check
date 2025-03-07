import os

from flask import Blueprint, render_template

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html")

@bp.route("/test")
def test():
    os.getcwd()
    return os.getcwd()