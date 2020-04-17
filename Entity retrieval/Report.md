# Assignment 3 report

**Team number:** *Team-005*

**Team members:** 

* Peter Kioko
* Samiul Ehsan Chowdhury
* Collins Kimutai Korir

## Indexing and fields

Indexing the DBPedia collections was very resource intensive. For this reason, we chose to work with a smaller subset of the collection.
We indexed the the following four files in full:

* labels_en.ttl
* long_abstracts_en.ttl
* page_links_en.ttl
* article_categories_en.ttl

To resolve categories, we also worked with `category_labels_en.ttl` with was downloaded separately from this [link](<http://downloads.dbpedia.org/2015-10/core-i18n/en/>)

Still, with the above subset, it was still very resource intensive because of looking up entities (resolving entities) in other subcollections. For this reason, part of the pre-processing was done with the help of a third-party tool for ETL: [Pentaho Community Edition](https://community.hitachivantara.com/s/article/downloads). This helped to combine all relevant and partly processed entities in one text file we named `entities_cleaned.txt`, found [here](https://drive.google.com/open?id=17hMZECtkvKCypqHB9N1FStwD6Oq9N5D_)

The following fields were indexed:

  - **names**: Was retrieved from rdfs:labels and was cleaned by removing trailing '@en'
  - **abstract**: Passed through the `english` analyzer 
  - **categories**: Resolved the object URIs for each category by looking up the `category_labels_en.ttl` to get the text representation
  - **similar_entities**: Retrieved from `page_links` then the entities further resolved using the `labels_en` file.
  - **catch_all**: A combination of all the other text based fields after they have been pre-processed

We used the default english analyzer for all the fields

## Implementation of MLM

For implementation of MLM, we used two fields('names','catch_all'). Before sending the queries to MLM, they were lower cased and stemmed using Porterstemmer. It was done due to the reason that, in index the terms were stemmed and lower cased.   

We have taken 'terms' from 'term verctors' of elasticsearch for lengthof the fields. Then calculated term probability from field terms divided by total term frequency. After that, Dirichlet smoothing was used with the smoothing parameter set to 2000.

After getting the scores, it was sorted according to MLM score and top 100 results were taken. Then the results simply generated to csv.
 
## Implementation of SDM+ELR

We implemented SDM as a re-ranking mechanism. After generating the top 100 first-pass file with results from elastic search, we used the `catch_all` field to implement the SDM function. This was done by first tokenizing the query using the default `english` analyzer in elasticsearch, then identifying bigrams in the tokens. These were fed into the feature functions for:

* unigrams
* ordered bigrams
* unordered bigrams

We used dirichlet smoothing with parameter as 2000. The result from each feature function was then multiplied against the corresponding weight and the totals were added together. (SDM function from lectures). After this, the list of documents is sort according to the scores from highest to lowest and written to file

## Implementation of Your model

We implemented the Fielded SDM for this part of model implementation. The underlying method was done similarly to the SDM implementation, with the exception that instead of calculating SDM score for one field, i.e. `catch_all`, we calculated the score for the remaining four fields i.e. names, categories, abstract and similar_entities. The scores were then added together to produce the final FSDM score


## Results

| Model | NDCG@10 | NDCG@100 |
| -- | -- | -- |
| MLM title+content | *0.1587548215695161* | *0.22463357890145005* |
| SDM+ELR | 0.20048156512156712 | 0.27422470010460687 |
| *Our model: FSDM* | 0.19843961154396 | 0.2770401907388836 |


## Discussion

Indexing the data presented a good challenge and understanding of pre-processing huge amounts of data. From the results, we observed better results using FSDM than with just SDM or MLM.


## References
  - Lecture Notes (Lectures 13, 14, 19)
