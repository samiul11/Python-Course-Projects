import pandas as pd
from elasticsearch import Elasticsearch

from pandas import DataFrame, Series
import re


QUERIES_1 = "data/queries.txt"
QUERIES_2 = "data/queries2.txt"
QUERIES_1_FIRST_PASS = "data/first_pass_bm25_one.csv"
QUERIES_2_FIRST_PASS = "data/first_pass_bm25_two.csv"

INDEX_NAME = "dbpedia_text"

es = Elasticsearch()

# Loading the actual queries


def load_queries(queries_file):
    queries_df = pd.read_csv(queries_file, header=None, delimiter=';')
    df = queries_df.replace(to_replace=['^\S+\d+\s'], value='', regex=True)
    queries_df = queries_df.applymap(
        lambda x: re.findall(r'^\S+\d+\s', x)[0].strip())
    queries_df = queries_df.merge(df, right_index=True, left_index=True)
    queries_df.columns = ['QueryId', 'Query']

    return queries_df.to_dict(orient='records')


def search(query, query_id):
    res = es.search(index=INDEX_NAME, q=query, size=100,
                    _source=False, analyzer='english', request_timeout=30)
    hits = res['hits']['hits']
    matched_entities = [(query_id, entity['_id']) for entity in hits]

    return DataFrame.from_records(matched_entities)


def generate_first_pass_file(queries_file, output_file):
    query_top_100_dfs = []

    queries = load_queries(queries_file)
    for q in queries:
        print(f"Searching entities for query: {q['QueryId']}")
        top_100 = search(q['Query'], q['QueryId'])
        query_top_100_dfs.append(top_100)

    query_entity_df = pd.concat(query_top_100_dfs, ignore_index=True)
    query_entity_df.columns = ['QueryId', 'EntityId']

    with open(output_file, 'w', encoding="utf-8", errors='ignore') as f:
        f.write("QueryId,EntityId\n")
        for rec in query_entity_df.to_dict(orient='records'):
            f.write("{},{}\n".format(rec['QueryId'], '"'+rec['EntityId']+'"'))

    print("-"*100)
    print(
        f"Finished generating first pass file for {len(queries)} queries")


# Generating first pass file for `Queries.txt`
generate_first_pass_file(QUERIES_1, QUERIES_1_FIRST_PASS)

# Generating first pass file for `Queries2.txt`
generate_first_pass_file(QUERIES_2, QUERIES_2_FIRST_PASS)
