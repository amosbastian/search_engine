from flask import Blueprint, render_template, request
import faceted_search

blueprint = Blueprint("search_faceted", __name__,
                      url_prefix="/search_faceted")


@blueprint.route("/")
def home():
    return render_template("search_engine/faceted_search.html", response=None)


@blueprint.route("/", methods=["POST"])
def home_post():
    query = request.form["query"]
    art = request.form.get("art")
    adv = request.form.get("adv")
    fam = request.form.get("fam")
    resp = faceted_search.faceted_search(query, (art, adv, fam))
    return render_template("search_engine/faceted_search.html", query=query, response=resp[0], barStats=resp[1])
