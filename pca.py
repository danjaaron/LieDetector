from utils import *
import sklearn
from sklearn import preprocessing
from sklearn.decomposition import PCA 
from matplotlib import pyplot as plt 
from matplotlib import pyplot
from mpl_toolkits.mplot3d import Axes3D
import random
from DataHandler import *
'''
Plots PCA of base data
'''

plt_none_labeled = False
dim3_plot = False

# get data matrix for directory 
d = DataHandler('./data/')
# d.scale()
d.bandpass(0.2, 2.0)
# d.scale()
d.divide_labeled()
X, y = d.X, d.y 
# X = samples
# X = preprocessing.scale(X)
# X_scaled = preprocessing.scale(X)
print("NUM SAMPLES: ", len(X))

# fit PCA on full stitched_empty, but only plot those with y 
if dim3_plot:
	pca = PCA(n_components = 3)
else:
	pca = PCA(n_components = 2)
# pca.fit(X)

X_r = pca.fit(X).transform(X) 
print("---PCA---")
print("Explained var: ", pca.explained_variance_ratio_)
print("---PCA---")

def assign_label_color(label):
	if label is None:
		return 'black'
	elif label == 1: # lie
		return 'red'
	elif label == 0: # truth
		return 'blue'
	else:
		raise NotImplementedError





if plt_none_labeled:
	# plot all PC (even if None labeled)
	plt_PC1 = [x[0] for x in X_r]
	plt_PC2 = [x[1] for x in X_r]
	if dim3_plot:
		plt_PC3 = [x[2] for x in X_r]
	plt_c = [assign_label_color(y[i]) for i in range(len(y))]
	# plt_c = ['black' for _ in y]
else:
	# plot all PC except None labeled
	plt_PC1 = [X_r[i][0] for i in range(len(X_r)) if y[i] in [1,0]]
	plt_PC2 = [X_r[i][1] for i in range(len(X_r)) if y[i] in [1,0]]
	if dim3_plot:
		plt_PC3 = [X_r[i][2] for i in range(len(X_r)) if y[i] in [1,0]]
	plt_c = [assign_label_color(y[i]) for i in range(len(y)) if y[i] in [1,0]]

if dim3_plot:
	# 3D PLOT
	fig = pyplot.figure()
	ax = Axes3D(fig)
	ax.scatter(plt_PC1, plt_PC2, plt_PC3, c = plt_c)
	# ax.scatter(plt_PC2, plt_PC3)
	pyplot.show()
else:
	plt.scatter(plt_PC1, plt_PC2, c = plt_c)
	plt.show()

'''

'''

'''
# KERNEL
transformer = sklearn.decomposition.KernelPCA(kernel = 'linear')
X_transformed = transformer.fit_transform(X)
print(dir(X_transformed))
'''