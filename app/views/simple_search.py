from elasticsearch import Elasticsearch
from collections import Counter, defaultdict
import json
import nltk.data


def simple_query(query):
    dis_max = {
        "query": {
            "dis_max": {
                "queries": [
                    {"match": {"title": query}},
                    {"match": {"body": query}}
                ],
                "tie_breaker": 0.3
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


def summarise(query, text):
    tokenizer = nltk.data.load("nltk:tokenizers/punkt/dutch.pickle")
    summarisation = ""
    for sentence in tokenizer.tokenize(text):
        if any([word in sentence for word in query.split()]):
            # print sentence.encode("utf-8"), word
            sentence = sentence.replace(
                word, "<b>{}</b>".format(word).encode("utf-8"))
            summarisation += sentence + " "
        if len(summarisation.split()) > 50:
            break

    if (len(summarisation) < 1):
        return " ".join(text.strip().split()[:50])
    else:
        return summarisation.strip()


def get_bar_stats(res):
    barStats = ""
    for dd in res["aggregations"]["ArticleDates"]["buckets"]:
        yr = dd['key_as_string'].split('-', 1)[0]
        dc = dd['doc_count']
        barStats += yr + '-' + str(dc) + '/'

    return barStats


def get_cloud_stats(res):
    if res["aggregations"]["TermCounts"]["buckets"] == []:
        return ""

    cloudStats = ""
    highest = res["aggregations"]["TermCounts"]["buckets"][0]["doc_count"]
    norm = highest / 15.0

    for tc in res["aggregations"]["TermCounts"]["buckets"]:
        tc["key"]
        tc["doc_count"]
        cloudStats += tc["key"] + '-' + str(tc["doc_count"] / norm) + '/'
    return cloudStats


def simple_search(query):
    es = Elasticsearch()

    es.indices.refresh(index="telegraaf")

    res = es.search(index="telegraaf", body=simple_query(query))
    for hit in res["hits"]["hits"]:
        hit["_source"]["text"] = summarise(query, hit["_source"]["text"])
    # print "Total results: {}!".format(results["hits"]["total"])
    # print "Showing top 5 results!\n"
    # for hit in results["hits"]["hits"][:5]:
    #     print "{} - {} - {}".format(hit["_score"], hit["_source"]["subject"], hit["_source"]["date"])
    #     print hit["_source"]["source"]
    #     print hit["_source"]["title"].encode("utf-8"), "\n"

    barStats = get_bar_stats(res)
    cloudStats = get_cloud_stats(res)

    return res, barStats, cloudStats

if __name__ == '__main__':
    simple_search("oorlog in duitsland")
