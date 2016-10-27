from flask import Blueprint, render_template, request
import simple_search

blueprint = Blueprint("search_engine", __name__, url_prefix="/search_engine")

@blueprint.route("/")
def home():
    return render_template("search_engine/simple_search.html", response=None)

@blueprint.route("/", methods=["POST"])
def home_post():
    query = request.form["query"]
    return render_template("search_engine/simple_search.html", query=query, response=simple_search.simple_search(query))