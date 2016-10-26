from flask import Blueprint, render_template

blueprint = Blueprint("home", __name__)

@blueprint.route("/", methods=["GET", "POST"])
def home():
    return render_template("home/home.html")