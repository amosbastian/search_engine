from flask import Blueprint, render_template, request
import advanced_search

blueprint = Blueprint("search_advanced", __name__,
                      url_prefix="/search_advanced")


@blueprint.route("/")
def home():
    return render_template("search_engine/advanced_search.html", response=None)


@blueprint.route("/", methods=["POST"])
def home_post():
    query = request.form["query"]
    resp = advanced_search.advanced_search(query)
    return render_template("search_engine/advanced_search.html", query=query, response=resp[0], barStats=resp[1])
