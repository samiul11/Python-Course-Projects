# Python-Course-Projects
Data mining with various methods

##Retrieval
 The task is to implement document retrieval methods and evaluate them using a standard test collection.
 
 Download the document collection and index it by completing the missing parts of the provided code skeleton.
 Use two fields, title and content.
 See below for details about the document collection.
 The 1_Indexer.ipynb notebook contains the code skeleton that you need to complete.
 Complete the 1_Evaluation.ipynb notebook, which should be able to take a ranking file and ground truth file as input and output.
 A sample ranking file and ground truth file with dummy data is made available for testing purposes.
 
 Implement two (single-field) retrieval models (LM and BM25) and evaluate them using your evaluation solution from Part 1.
 Search only in the content field.
 Return the top 100 documents for each query in data/queries.txt and write the results to a data/baseline.txt file (see below for the  output file format).
 
 Implement multi-field versions of BM25 and LM retrieval models, i.e., BM25F and MLM.
 Tune the parameters
 For BM25F, tune the field weights, k1, and b parameters.
 For MLM, tune the field weights, smoothing method, and smoothing parameter.
 
 ##Advanced Retrieval
  The task is to implement a learning-to-rank approach for web search and evaluate it using a standard test collection.
  
  You are provided with a set of queries and with an initial ranking of top-100 results for each query (based on BM25). Your task is to re-rank these documents using a learning-to-rank approach. Specifically, you need to use a pointwise learning-to-rank approach, i.e., any standard regression algorithm that is available in scikit-learn.

  An Elasticsearch index is already created (that is, we already indexed the document collection for you) and can be accessed via an API.
  
  Implement a learning-to-rank method with the following minimum requirements:
  Consider document-query matching in minimum 3 fields (title, content and anchors) and at least two different retrieval models (e.g., BM25 and LM). That is, 6 document-query features minimum.
  Note that the anchor text index covers the entire ClueWeb collection, not just the Category B subset. I.e., you need to ignore documents that are not present in the regular index.
  Select one learning-to-rank algorithm to use throughout the assignment.
  Test your model using 5-fold cross-validation on the given training data (queries and relevance judgments, i.e., data/queries.txt and data/qrels.csv).
  
  Design and implement additional features to maximize retrieval performance.
  Add minimum 2 query features and minimum 2 document features.
  PageRank scores for the ClueWeb collection are available here. Specifically, since you are working with the "Category B" subset, the files under the "ClueWeb12-B13 PageRank" heading are to be used.
  Note: you don't have to use PageRank as a feature. If you want, you can take PageRank scores from one of these files (and you need to figure out the file format yourself; but really, it is not that complicated).
  
  Select a subset consisting of the five features, from the complete feature set, that give you the best overall performance.
  
##Entity Retrieval

  Your task is to implement three entity retrieval models on top of Elasticsearch and evaluate them on a standard test collection.
  
  You need to implement three models and report evaluation results on those. All models should be implemented as a re-ranking mechanism over top-100 (first-pass) retrieval results that you obtain using the default retrieval model (BM25) in Elasticsearch.

  MLM: The mixture of language models approach with two fields, title and content, with weights 0.2 and 0.8, respectively. Content should be the "catch-all" field. Use Dirichlet smoothing with the smoothing parameter set to 2000.
  SDM+ELR: Sequential dependence model with the ELR extension.
  This is a single-field variant of SDM, so you need to use the "catch-all" field for term-based scoring.
  Use standard weights, that is, 0.8 for unigram matches, 0.05 for ordered bigram matches, 0.05 for unordered bigram matches, and 0.1 for entity matches.
  Use Dirichlet smoothing with the smoothing parameter set to 2000.
  Note: you'll need to build a positional index.
  The entity annotations for queries are provided as part of the input.
  Your model: This may be any known extension/variant of existing models or your own invention. You may use any technique or combination of techniques introduced in the lectures, e.g., multiple fields, query expansion, word embeddings, etc. A standard option is FSDM+ELR, which should give you 10% relative improvement over SDM+ELR.