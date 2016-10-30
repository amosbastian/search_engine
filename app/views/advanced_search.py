from elasticsearch import Elasticsearch
import re
import json
import nltk.data


def advanced_query(query):
    qtitle, qbody, underb, upperb = query
    print "\t <<< [", qtitle, "|", qbody, "] >>>"

    matchqueryt = {"match": {"title": qtitle}}
    matchqueryb = {"match": {"body": qbody}}
    queries = [matchqueryt, matchqueryb]

    querytype = {
        "dis_max": {
            "queries": queries,
            "tie_breaker": 0.3
        }
    }

    # Return all records if query strings are empty
    if qtitle == "" and qbody == "":
        queries = [{"match_all": {}}]
    if qtitle == "" and qbody != "":
        querytype = {
            "term": {
                "body": qbody
            }
        }

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
                "query": querytype,
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


def summarise(query, text):
    tokenizer = nltk.data.load("nltk:tokenizers/punkt/dutch.pickle")
    summarisation = ""
    for sentence in tokenizer.tokenize(text):
        if any([word in sentence for word in query.split()]):
            print sentence.encode("utf-8"), word
            sentence = sentence.replace(
                word, "<b>{}</b>".format(word).encode("utf-8"))
            summarisation += sentence + " "
        if len(summarisation.split()) > 50:
            break

    if (len(summarisation) < 1):
        return " ".join(text.strip().split()[:50])
    else:
        return summarisation.strip()


def advanced_search(query):
    es = Elasticsearch()

    es.indices.refresh(index="telegraaf")

    body, error = advanced_query(query)
    res = es.search(index="telegraaf", body=body)
    for hit in res["hits"]["hits"]:
        hit["_source"]["text"] = summarise(query[1], hit["_source"]["text"])

    barStats = ""
    for dd in res["aggregations"]["ArticleDates"]["buckets"]:
        yr = dd['key_as_string'].split('-', 1)[0]
        dc = dd['doc_count']
        barStats += yr + '-' + str(dc) + '/'

    return res, barStats, error

if __name__ == '__main__':
    simple_search("oorlog in duitsland")
