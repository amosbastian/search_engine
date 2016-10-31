from elasticsearch import Elasticsearch
from app.views.simple_search import summarise, get_bar_stats, get_cloud_stats
import re
import json
import nltk.data


def advanced_query(query):
    qtitle, qbody, underb, upperb = query

    matchqueryt = {"match": {"title": qtitle}}
    matchqueryb = {"match": {"text": qbody}}
    queries = []

    querytype = {
        "dis_max": {
            "queries": queries,
            "tie_breaker": 0.3
        }
    }

    # Return all records if query strings are empty
    if qtitle == "" and qbody == "":
        queries = [{"match_all": {}}]

    queries = [matchqueryt, matchqueryb]

    # error is a string to return to the template if there are any
    # problems with the specified variable values
    error = ""

    # if underbound has not been specified, make underbound minimum value.
    # make upperbound maximum value if not specified.
    if underb == "":
        underb = "0000-01-01"
    if upperb == "":
        upperb = "9999-12-31"

    # Check if the dates have been set in the proper format
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
    return dis_max, error


def advanced_search(query):
    es = Elasticsearch()

    es.indices.refresh(index="telegraaf")

    body, error = advanced_query(query)
    res = es.search(index="telegraaf", body=body)
    for hit in res["hits"]["hits"]:
        hit["_source"]["text"] = summarise(query[1], hit["_source"]["text"])

    barStats = get_bar_stats(res)
    cloudStats = get_cloud_stats(res)

    return res, barStats, cloudStats, error

if __name__ == '__main__':
    simple_search("oorlog in duitsland")
