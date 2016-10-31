""" Amos Bastian - 10676481
    Carlo Locsin - 10724664

"""

from elasticsearch import Elasticsearch
from app.views.simple_search import summarise, get_bar_stats, get_cloud_stats
import re
import json
import nltk.data


# Advanced_query takes a tuple containing two different query strings and
# two date strings. The two query strings qtitle and qbody are used to
# search the title and body with their respective strings. The two date
# strings are for the upper and lower bound of the time period in which the
# user wants to search through

def advanced_query(query):
    qtitle, qbody, underb, upperb = query

    queries = [{"match": {"title": qtitle}}, {"match": {"text": qbody}}]

    # Return all records if query strings are empty
    if qtitle == "" and qbody == "":
        queries = [{"match_all": {}}]

    # error is a string to return to the template if there are any
    # problems with the specified bounds
    error = ""

    # if underbound has not been specified, make underbound minimum value.
    # make upperbound maximum value if not specified.
    if underb == "":
        underb = "0000-01-01"
    if upperb == "":
        upperb = "9999-12-31"

    # Check if the dates have been set in the proper format, change both
    # bounds to 1 january 0 to prevent any matches. Also display error message
    if not re.match('[\d-]+$', underb):
        underb = "0000-01-01"
        upperb = underb
        error = "One of the date bounds not set properly!"
    if not re.match('[\d-]+$', upperb):
        upperb = "0000-01-01"
        upperb = underb
        error = "One of the date bounds not set properly!"

    dis_max = {
        "query": {
            "filtered": {
                "query": {
                    "bool": {
                        "should": queries
                    }
                },
                "filter": {
                    "bool": {
                        "must": {
                            "range": {
                                "date": {
                                    "gte": underb,
                                    "lte": upperb
                                }
                            }
                        }
                    }
                }
            }
        },

        "aggregations": {
            "TermCounts": {
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
    return dis_max, error


def advanced_search(query):
    es = Elasticsearch()

    es.indices.refresh(index="telegraaf")

    body, error = advanced_query(query)
    res = es.search(index="telegraaf", body=body)

    # Highlight term in the body for one word queries
    for hit in res["hits"]["hits"]:
        hit["_source"]["text"] = summarise(query[1], hit["_source"]["text"])

    # get statistics strings for rendering the bargraph and wordcloud
    barStats = get_bar_stats(res)
    cloudStats = get_cloud_stats(res)

    return res, barStats, cloudStats, error

if __name__ == '__main__':
    simple_search("oorlog in duitsland")
