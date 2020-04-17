import pandas as pd
from pandas import DataFrame, Series
import json
from elasticsearch import Elasticsearch

SETTINGS = {
    "index": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

TEXT_PROPERTIES = {
    "type": "text",
    "term_vector": "with_positions",
    "analyzer": "english"
}

TEXT_INDEX_SETTINGS = {
    "settings": SETTINGS,
    "mappings": {
        "properties": {
            "names": TEXT_PROPERTIES,
            "categories": TEXT_PROPERTIES,
            "similar_entities": TEXT_PROPERTIES,
            "abstract": TEXT_PROPERTIES,
            "catch_all": TEXT_PROPERTIES
        }
    }
}

DATA_DIR = "E:/Repositories/DAT640/assign3/output/"

INDEX_NAME = "dbpedia_text"

es = Elasticsearch()

if es.indices.exists(INDEX_NAME):
    # Delete the index if it exists
    resp = es.indices.delete(INDEX_NAME)
    print(f"Deleting the existing index: {resp}")

resp = es.indices.create(index=INDEX_NAME, body=TEXT_INDEX_SETTINGS)
print(f"Creating the index: {resp}")

# ENTITIES FILE
file_count = 0
chunks = pd.read_csv(DATA_DIR+"entities_cleaned.txt",
                     delimiter=';p;', skiprows=1,
                     names=['subject', 'label', 'page_link_entities',
                            'category_entities',
                            'category_names', 'abstract', 'page_link_names'],
                     engine='python', chunksize=10000)

for df in chunks:
    df['page_link_names'].replace(
        to_replace='[\s_;]+', value=' ', inplace=True, regex=True)
    bulk_data = []
    entity_list = json.loads(df.to_json(orient='records'))

    for entity in entity_list:
        catch_all_fields = [
            str(entity.get('label', " ")),
            str(entity.get('page_link_names', ' ')),
            str(entity.get('category_names', ' ')),
            str(entity.get('abstract', ' '))
        ]
        bulk_data.append(
            {
                "index": {
                    "_index": INDEX_NAME,
                    "_id": entity['subject']
                }
            }
        )
        bulk_data.append(
            {
                'names': entity.get('label', ' '),
                'categories': entity.get('category_names', ' '),
                'similar_entities': entity.get('page_link_names', ' '),
                'abstract': entity.get('abstract', ' '),
                'catch_all': "".join(catch_all_fields)
            }
        )

    es.bulk(index=INDEX_NAME, body=bulk_data, refresh=True)

    file_count = file_count+df.shape[0]
    print(file_count)


print("-"*100)
print("Finished indexing all the entities into index:  {}".format(INDEX_NAME))
