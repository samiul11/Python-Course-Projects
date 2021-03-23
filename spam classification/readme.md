##Scenario
You have been hired by a company as a data scientist, and you need to help build a spam classifier. That is, create a model that is able to correctly classify 
the incoming emails to company email accounts as either spam or genuine non-spam ("ham") emails.

##Task
You are given a training dataset of over 82k emails, which are labeled either as spam or ham. Emails are stored as (ISO-8859-1 encoded) text files 
and organized in a set of folders (train/XYZ). The corresponding ground truth labels can be found in train/labels.csv.
Based on this data, your ultimate goal is to build a classifier that processes all emails under (test/XYZ), a total of over 9k documents, 
makes a ham/spam prediction for each, and outputs these in a similar CSV format.
The idea is to make this classification by assigning each email a spam score. Emails above a certain score threshold will be labeled as spam, otherwise regarded as ham. 
Figuring out how to compute the spam score and what is an appropriate threshold is your main task; this is where having labeled data will help you big time.
Your overall objective is to beat the baseline classifier (which labels everything with the majority class) by at least 10% in terms of Accuracy.

##Specific steps
1) Download corpus
Download the email corpus from the URL provided on Canvas and unzip it to a data folder.

2) Split the labeled data
Split the labeled dataset (i.e., the one under data/train) into training and validation splits for development. You may also split it k-fold for cross-validation.

NOTE: Below, we will simply assume that you copied part of the original train data as a training split to one folder (referred to as train-data-dir) and the remaining part as validation split to another folder (validation-data-dir). If you want to be smarter about it and avoid physically copying (and effectively duplicating) the collection (possibly multiple times), then you're free to do something more elegant (e.g., just creating a list of filenames that belong to the training/validation splits). But this is entirely optional.

3) Implement the spam classifier
Complete the missing parts of the classifier.py Python script.

Train a model on the training split of your dataset by running:

python classifier.py -mode train --data {train-data-dir} --output {model-file}
Then apply your model on the validation split:

python classifier.py -mode predict --data {validation-data-dir} --model {model-file} --output {prediction-file}
The format and contents of the model-file is completely up to you. You probably want to collect some statistics from the training data, which you can then utilize when computing the spam score.
The prediction-file should be in csv format, with Id and Label fields, where Id is the file path relative to the data folder, e.g.:
Id,Label
train/000/001,spam
train/000/007,spam
train/000/009,spam
You can evaluate your classifier's performance using:

python classifier.py -mode eval --predictions {predictions-file} -- ground_truth {ground-truth-file}
Iterate these steps until you're satisfied with the model's performance.
