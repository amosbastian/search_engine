import json, os, glob
from elasticsearch import Elasticsearch, helpers

index_body = {
    "settings": {
        "analysis": {
            "filter": {
                "dutch_stop": {
                "type": "stop",
                "stopwords": "_dutch_" 
                },
                "dutch_stemmer": {
                    "type": "stemmer",
                    "language": "dutch"
                }
            },
            "analyzer": {
                "dutch": {
                    "tokenizer": "standard",
                    "filter": [
                        "lowercase",
                        "dutch_stop",
                        "dutch_stemmer"
                    ]
                }
            }
        }
    },
    "mappings": {
        "article": {
            "properties": {
                "title":   { "type": "string", "analyzer": "dutch" },
                "body":    { "type": "string", "analyzer": "dutch" },
                "source":  { "type": "string"},
                "subject": { "type": "string"},
                "date":    { "type": "string"},
                "id":      { "type": "string"}
            }
        }
    }
}

if __name__ == '__main__':
    es = Elasticsearch()
    es.indices.delete(index="telegraaf", ignore=[400, 404])
    
    es.indices.create("telegraaf", body=index_body, request_timeout=300)

    for infile in glob.glob(os.path.join("JSON", "*.json")):
        print infile
        with open(infile, "r") as f:
            all_articles = json.load(f)

        k = ({"_type": "article", "_index": "telegraaf", "_source": article}
            for article in all_articles)

        helpers.bulk(es, k)