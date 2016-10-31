from flask import Blueprint, render_template, request
import advanced_search

blueprint = Blueprint("search_advanced", __name__,
                      url_prefix="/search_advanced")


@blueprint.route("/")
def home():
    return render_template("search_engine/advanced_search.html", response=None)


@blueprint.route("/", methods=["POST"])
def home_post():
    qtitle = request.form["qtitle"]
    qbody = request.form["qbody"]
    underb = request.form["underb"]
    upperb = request.form["upperb"]

    query = (qtitle, qbody, underb, upperb)
    resp = advanced_search.advanced_search(query)
    return render_template("search_engine/advanced_search.html",
                           query=query, response=resp[0], barStats=resp[1],
                           cloudStats=resp[2], msg=resp[3])
