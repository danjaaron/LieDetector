from utils import *
from sklearn.cluster import KMeans 
from sklearn import preprocessing
import numpy as np

dr = DirReader('./data/')
X = preprocessing.scale(dr.X)
y = dr.y

kmeans = KMeans(n_clusters=2, random_state=0).fit(X)

# check overlap 
labeled_inds = np.array([y_i for y_i in range(len(y)) if y[y_i] != None])
print("total labeled: ", len(labeled_inds))
responses = X[labeled_inds]
true_labels = y[labeled_inds]
k_preds = kmeans.labels_[labeled_inds]
print(true_labels)
print(k_preds)

# get accuracy 
num_correct = len([k_preds[i] for i in range(len(k_preds)) if k_preds[i] == true_labels[i]])
num_total = len(k_preds)
print(float(num_correct)/float(num_total))
