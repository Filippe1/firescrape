from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")

doc = {
    "title": "Example Page",
    "content": "This is a sample indexed webpage."
}

es.index(index="webpages", id=1, body=doc)
