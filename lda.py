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

# determine whether to save model 
def check_save_model(attempts = 3): 
	print("Save model?")
	save_response = input().lower()
	if save_response in ['y', 'n']:
		return save_response
	elif attempts <= 0:
		print("Max invalid responses, quitting without saving.")
	else:
		print("Received invalid response: ", save_response)
		print("please retry...")
		return check_save_model(attempts - 1)

def pickle_model(model, filename):
	# get full filename
	full_name = './models/' + filename + str(len([f for f in os.listdir('./models/') if filename in f])) + '.pickle'
	print("Saving model as: ", full_name)
	pickle.dump(model, open(full_name, 'wb'))
	print("Model saved!")


def load_model(filename):
	# get full filename
	full_name = './models/' + filename + str(len([f for f in os.listdir('./models/') if filename in f])-1) + '.pickle'
	print("Loading model: ", full_name)
	model = pickle.load(open(full_name, 'rb'))
	print("Model loaded!")
	return model

save_response = check_save_model()
if save_response == 'y':
	pickle_model(clf, "QDA")
else:
	print("Quitting without saving.")