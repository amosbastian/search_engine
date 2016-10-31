""" Amos Bastian - 10676481
    Carlo Locsin - 10724664

"""

from elasticsearch import Elasticsearch
from app.views.simple_search import summarise, get_bar_stats, get_cloud_stats
import json
import nltk.data


# Returns a JSON object snippet that matches term with the given facet.
# Used in filtering facets with the "or" operator
def filter_term_json(facet):
    return {
        "term": {
            "subject": facet
        }
    }


# faceted_query takes a query string and 4 different values for the different
# facets. The returned query JSON will search through the index like simple
# search would, but will filter out any results that do not belong to the
# specified facets using "filter" and "or"
def faceted_query(query):
    qstring, art, adv, fam, ill = query

    queries = [{"match": {"title": qstring}}, {"match": {"body": qstring}}]
    if qstring == "":
        queries = [{"match_all": {}}]
    selected_facets = []

    # Only search for specified facets
    if art == "True":
        selected_facets.append(filter_term_json("artikel"))
    if adv == "True":
        selected_facets.append(filter_term_json("advertentie"))
    if fam == "True":
        selected_facets.append(filter_term_json("familiebericht"))
    if ill == "True":
        selected_facets.append(filter_term_json("illustratie"))

    dis_max = {
        "query": {
            "filtered": {
                "query": {
                    "dis_max": {
                        "queries": queries,
                        "tie_breaker": 0.3
                    }
                },
                "filter": {
                    "or": selected_facets
                }
            }
        },
        # https://www.elastic.co/guide/en/elasticsearch/reference/current/search-aggregations-bucket-datehistogram-aggregation.html
        "aggregations": {
            "TermCounts": {
                # Aggregation of field "body" doesn't work for some reason
                "significant_terms": {"field": "title"}
            },
            "ArticleDates": {
                "date_histogram": {
                    "field": "date",
                    "interval": "1y",
                    "format": "yyyy-MM-dd"
                }
            }
        }
    }
    return dis_max


def faceted_search(query):
    es = Elasticsearch()

    es.indices.refresh(index="telegraaf")

    res = es.search(index="telegraaf", body=faceted_query(query))
    for hit in res["hits"]["hits"]:
        hit["_source"]["text"] = summarise(query[0], hit["_source"]["text"])

    barStats = get_bar_stats(res)
    cloudStats = get_cloud_stats(res)
    return res, barStats, cloudStats

if __name__ == '__main__':
    simple_search("oorlog in duitsland")
