from utils import *
import sklearn
from sklearn import preprocessing
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from matplotlib import pyplot as plt 
from sklearn.decomposition import PCA 
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
import random
from DataHandler import *
'''
QDA on filtered data
... bandpass 0.1 - 2.0, 80/20 train-test split, scaled --> QDA --> 80% ACCURACY??
'''

plt_none_labeled = False
dim3_plot = True

# get data matrix for directory 
d = DataHandler('./data/')
d.bandpass(0.1, 2.0)
d.split(0.8)
X, y = d.X, d.y
train_x, train_y = d.X_train, d.y_train 
test_x, test_y = d.X_test, d.y_test

# X = samples
X = preprocessing.scale(X)

samples = X 
labels = y 


clf = QuadraticDiscriminantAnalysis()
# train_x_trans = clf.fit_transform(train_x, train_y)
# print(train_y)
clf.fit(train_x, list(train_y))

preds = clf.predict(test_x)

print("predicted")
print("preds: ", preds)
print("labels: ", test_y)
num_wrong = len([i for i in range(len(preds)) if (preds[i] != test_y[i])])
num_total = len(test_y)
percent_right = 100.*(1.0 - (float(num_wrong)/float(num_total)))
print("percent acc: ", percent_right)