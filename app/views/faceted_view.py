from flask import Blueprint, render_template, request
import faceted_search

blueprint = Blueprint("search_faceted", __name__,
                      url_prefix="/search_faceted")


@blueprint.route("/")
def home():
    return render_template("search_engine/faceted_search.html", response=None)


@blueprint.route("/", methods=["POST"])
def home_post():
    qstring = request.form["query"]
    art = request.form.get("art")
    adv = request.form.get("adv")
    fam = request.form.get("fam")
    ill = request.form.get("ill")

    query = (qstring, art, adv, fam, ill)
    resp = faceted_search.faceted_search(query)
    return render_template("search_engine/faceted_search.html",
                           query=query, response=resp[0], barStats=resp[1],
                           cloudStats=resp[2])
