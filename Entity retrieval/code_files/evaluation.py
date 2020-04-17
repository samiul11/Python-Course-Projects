
import math

# RANKING_FILE = "data/first_pass_bm25_one.csv"
# RANKING_FILE = "data/sdm_re_ranked.csv"
RANKING_FILE = "data/ranking_model3.csv"
QRELS_FILE = "data/qrels.csv"


def load_rankings(ranking_file):
    rankings = {}
    with open(ranking_file, "r", encoding="utf-8", errors='ignore') as fin:
        header = fin.readline().strip()
        if header != "QueryId,EntityId":
            raise Exception("Incorrect file format!")
        for line in fin.readlines():
            qid, _ = line.strip().split(",\"")
            docid = _[:-1]  # remove trailing "
            if qid not in rankings:
                rankings[qid] = []
            rankings[qid].append(docid)
    return rankings


def load_qrels(qrels_file):
    qrels = {}
    with open(qrels_file, "r", encoding="utf-8", errors='ignore') as fin:
        header = fin.readline().strip()
        if header != "QueryId,EntityId,Relevance":
            raise Exception("Incorrect file format!")
        for line in fin.readlines():
            qid, _ = line.strip().split(",\"")
            docid, rel = _.split("\",")
            if qid not in qrels:
                qrels[qid] = {}
            qrels[qid][docid] = int(rel)
    return qrels


def dcg(rel, p):
    dcg = rel[0]
    for i in range(1, min(p, len(rel))):
        dcg += rel[i] / math.log(i + 1, 2)  # rank position is indexed from 1..
    return dcg


def compute_ndcg(rankings, qrels, k=100):
    sum_ndcg = 0
    for qid, ranking in sorted(rankings.items()):
        gt = qrels[qid]
        gains = []  # holds corresponding relevance levels for the ranked docs
        for doc_id in ranking[:k]:
            gain = gt.get(doc_id, 0)
            gains.append(gain)

        # relevance levels of the idealized ranking
        gain_ideal = sorted([v for _, v in gt.items()], reverse=True)

        ndcg = dcg(gains, k) / dcg(gain_ideal, k)
        sum_ndcg += ndcg

    return sum_ndcg / len(rankings)


qrels = load_qrels(QRELS_FILE)
rankings = load_rankings(RANKING_FILE)

print("NDCG@10: {}".format(compute_ndcg(rankings, qrels, k=10)))
print("NDCG@100: {}".format(compute_ndcg(rankings, qrels)))
