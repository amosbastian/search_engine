from elasticsearch import Elasticsearch
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


def faceted_search(query):
    es = Elasticsearch()

    es.indices.refresh(index="telegraaf")

    res = es.search(index="telegraaf", body=faceted_query(query))
    for hit in res["hits"]["hits"]:
        hit["_source"]["text"] = summarise(query[0], hit["_source"]["text"])

    barStats = ""
    for dd in res["aggregations"]["ArticleDates"]["buckets"]:
        yr = dd['key_as_string'].split('-', 1)[0]
        dc = dd['doc_count']
        barStats += yr + '-' + str(dc) + '/'

    return res, barStats

if __name__ == '__main__':
    simple_search("oorlog in duitsland")
