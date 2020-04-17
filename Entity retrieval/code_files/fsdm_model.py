import json
import re

import pandas as pd
from pandas import DataFrame, Series
from elasticsearch import Elasticsearch
from pprint import pprint
import csv
import math

INDEX_NAME = "dbpedia_text"
FIELDS = ['names', 'abstract', 'categories', 'similar_entities']

QUERIES_1 = "data/queries2.txt"

RANKING_FILE = "data/first_pass_bm25_two.csv"

RE_RANKED_FILE = "data/fsdm_re_ranked2.csv"

es = Elasticsearch()


def load_ranking_pairs(ranking_file):
    ranking_pairs = []
    with open(ranking_file, 'r', encoding="utf-8") as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            ranking_pairs.append(tuple(row))

    return ranking_pairs


def load_queries(queries_file):
    queries_df = pd.read_csv(queries_file, header=None, delimiter=';')
    df = queries_df.replace(to_replace=['^\S+\d+\s'], value='', regex=True)
    queries_df = queries_df.applymap(
        lambda x: re.findall(r'^\S+\d+\s', x)[0].strip())
    queries_df = queries_df.merge(df, right_index=True, left_index=True)
    queries_df.columns = ['QueryId', 'Query']
    queries_df.set_index('QueryId', inplace=True)

    return queries_df['Query'].to_dict()


def tokenize_query(es, query):
    res = es.indices.analyze(index=INDEX_NAME, body={
        'analyzer': "english", 'text': query})
    return [token['token'] for token in res.get('tokens', {})]


def find_bigrams(input_list):
    return [b for b in zip(input_list, input_list[1:])]


def get_term_sequence(es, doc_id, field):
    tv = es.termvectors(index=INDEX_NAME, id=doc_id, fields=[field])
    # We first put terms in a position-indexed dict.
    pos = {}
    term_freq = {}

    default_tv = {
        'term_vectors': {
            'field': {
                'terms': {
                    'word': {
                        'term_freq': 1,
                        'tokens': [{'position': 0}]
                    }
                }
            }
        }
    }

    tv = tv if field in tv['term_vectors'].keys() else default_tv
    field = field if field in tv['term_vectors'].keys() else 'field'

    for term, tinfo in tv['term_vectors'][field]['terms'].items():
        for token in tinfo['tokens']:
            pos[token['position']] = term
        term_freq[term] = tinfo['term_freq']
    # Then, turn that dict to a list.
    seq = [None] * (max(pos.keys()) + 1)
    for p, term in pos.items():
        seq[p] = term
    # Document Length
    doc_length = len(pos.items())
    return doc_length, term_freq, seq


def count_ordered_bigram_matches(text, bigram):
    """Counts the number of bigram matches in text.
    Both text and bigram are represented as a list of terms."""
    count = 0
    for i in range(len(text) - 1):
        if text[i] == bigram[0]:
            if text[i + 1] == bigram[1]:
                count += 1
    return count


def count_unordered_bigram_matches(text, bigram, w):
    """Counts the number of unordered bigram matches in text within a given window size.
    Both text and bigram are represented as a list of terms."""
    count = 0
    for i in range(len(text) - 1):
        if text[i] in bigram:
            other_term = bigram[0] if text[i] == bigram[1] else bigram[1]
            if other_term in text[i+1:i+w]:
                count += 1
    return count


def collection_language_model(totals: Series):
    doc_len = totals['doc_length']
    return totals.map(lambda x: x/doc_len)


def feature_score(doc: Series, coll_lang_m: Series, smoothing_p):
    lm_score = 0
    for index in list(doc.index.unique()):
        score = math.log(
            (doc[index]+(smoothing_p*coll_lang_m[index]))/(doc['doc_length']+smoothing_p)) if coll_lang_m[index] > 0 else 0
        lm_score = lm_score+score
    return lm_score


def get_entity_details(items, term_freq, term_seq, flag='unigram'):
    entity_details = {
        'entity': entity_id,
        'doc_length': doc_length
    }
    for item in items:
        if flag == 'unigram':
            entity_details[item] = term_freq.get(item, 0)
        elif flag == 'o_bigram':
            entity_details[' '.join(list(item))] = count_ordered_bigram_matches(
                term_seq, list(item))
        else:
            entity_details[' '.join(list(item))] = count_unordered_bigram_matches(
                term_seq, list(item), w=8)
    return entity_details


def calculate_scores(entities):
    df = pd.DataFrame.from_records(entities)
    df.set_index('entity', inplace=True)
    coll_lang_model = collection_language_model(
        df.apply(lambda x: x.sum()))
    scores = df.apply(
        feature_score, axis='columns', coll_lang_m=coll_lang_model, smoothing_p=2000)
    return scores


def apply_feature_weights(row: Series, feature_weights):
    fw = [row[index]*feature_weights[index]
          for index in list(row.index.unique())]
    return sum(fw)


def calculate_sdm_scores(unigram_entities, ordered_bigram_entities, unordered_bigram_entities, f_weights):
    unigram_scores = calculate_scores(unigram_entities)
    ordered_bigram_scores = calculate_scores(ordered_bigram_entities)
    unordered_bigram_scores = calculate_scores(unordered_bigram_entities)

    df = pd.concat([unigram_scores, ordered_bigram_scores, unordered_bigram_scores],
                   axis=1, names=['unigram', 'ordered', 'unordered']
                   )
    df.columns = ['unigram', 'ordered', 'unordered']
    return df.apply(apply_feature_weights, axis=1, feature_weights=f_weights)


ranking_pairs = load_ranking_pairs(RANKING_FILE)
queries_dict = load_queries(QUERIES_1)

re_ranked_dfs = []

for q_id in list(queries_dict.keys()):
    print(f"Re-ranking entities for query: {q_id}")
    pairs = [pair for pair in ranking_pairs if pair[0] == q_id]
    query = queries_dict.get(q_id, '')
    tokens = tokenize_query(es, query)
    bigrams = find_bigrams(tokens)

    field_sdm_scores = []

    for field in FIELDS:
        unigram_entities = []
        ordered_bigram_entities = []
        unordered_bigram_entities = []

        for _, entity_id in pairs:
            doc_length, term_freq, term_seq = get_term_sequence(
                es, entity_id, field)

            unigram_entities.append(get_entity_details(
                tokens, term_freq, term_seq, flag='unigram'))

            ordered_bigram_entities.append(get_entity_details(
                find_bigrams(tokens), term_freq, term_seq, flag='o_bigram'))

            unordered_bigram_entities.append(get_entity_details(
                find_bigrams(tokens), term_freq, term_seq, flag='u_bigram'))

        f_weights = {
            'unigram': 0.85,
            'ordered': 0.1,
            'unordered': 0.05
        }
        sdm_scores = calculate_sdm_scores(
            unigram_entities, ordered_bigram_entities, unordered_bigram_entities, f_weights)

        field_sdm_scores.append(sdm_scores)

    fsdm_df = pd.concat(field_sdm_scores, axis=1)
    final_scores = fsdm_df.apply(lambda x: x.sum(), axis=1)

    final_scores.sort_values(ascending=False, inplace=True)
    final_scores = final_scores.reset_index()
    final_scores.insert(0, 'QueryId', q_id)
    final_scores.drop(columns=[0], inplace=True)
    final_scores.columns = ['QueryId', 'EntityId']
    re_ranked_dfs.append(final_scores)

query_entity_df = pd.concat(re_ranked_dfs, ignore_index=True)
query_entity_df.columns = ['QueryId', 'EntityId']

with open(RE_RANKED_FILE, 'w', encoding="utf-8", errors='ignore') as f:
    f.write("QueryId,EntityId\n")
    for rec in query_entity_df.to_dict(orient='records'):
        f.write("{},{}\n".format(rec['QueryId'], '"'+rec['EntityId']+'"'))

print("-"*100)
print(
    f"Finished re-ranking file for {len(queries_dict.keys())} queries")
