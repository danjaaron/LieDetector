'''
Uses a QDA model fit on ./data/ to predict new data

###!!!!!!! PROB: Full collect is going to ask to verify. This is dumb -- verifying responses and seeing QDA predict that. 
INSTEAD -- go straight to online predict.
'''

from utils import *
from StreamHandler import *
from DataHandler import *

def load_model(filename):
	# get full filename
	full_name = './models/' + filename + str(len([f for f in os.listdir('./models/') if filename in f])-1) + '.pickle'
	print("Loading model: ", full_name)
	model = pickle.load(open(full_name, 'rb'))
	print("Model loaded!")
	return model

def verify_model_load():
	''' Verifies QDA model is loaded correctly by re-predicting on basal data '''
	# collect data for offline prediction (new interrogation)
	print("VERIFYING MODEL LOAD")
	dstem = './data/'
	d = DataHandler(dstem)
	d.bandpass(0.1, 2.0)
	d.split(0.1)
	X, y = d.X, d.y
	train_x, train_y = d.X_train, d.y_train 
	test_x, test_y = d.X_test, d.y_test
	# X = samples
	X = preprocessing.scale(X)
	# load latest QDA model 
	clf = load_model("QDA")
	# predict 
	preds = clf.predict(test_x)
	print("predicted")
	print("preds: ", preds)
	print("labels: ", test_y)
	num_wrong = len([i for i in range(len(preds)) if (preds[i] != test_y[i])])
	num_total = len(test_y)
	percent_right = 100.*(1.0 - (float(num_wrong)/float(num_total)))
	print("percent acc: ", percent_right)

def offline_predict(collect_new = True, dstem = './data_offline/'):
	''' Generate new data from new interrogation, then store offline and predict with saved QDA model '''
	# load latest QDA model 
	clf = load_model("QDA")

	# collect data
	if collect_new:
		full_collect(dstem)
	# process last collect
	d = DataHandler(dstem)
	d.bandpass(0.1, 2.0)
	# d.split(0.8)
	d.scale()

	# predict on all collected data
	preds = clf.predict(d.X[d.li, :])
	print("PREDICTIONS: ", preds)
	assert(len(preds) == len(d.li))

	'''
	# split collected data
	X, y = d.X, d.y
	train_x, train_y = d.X_train, d.y_train 
	test_x, test_y = d.X_test, d.y_test
	# load latest QDA model 
	clf = load_model("QDA")
	# predict 
	preds = clf.predict(test_x)
	print("predicted")
	print("preds: ", preds)
	print("labels: ", test_y)
	num_wrong = len([i for i in range(len(preds)) if (preds[i] != test_y[i])])
	num_total = len(test_y)
	percent_right = 100.*(1.0 - (float(num_wrong)/float(num_total)))
	print("percent acc: ", percent_right)
	'''


if __name__ == '__main__':
	offline_predict(collect_new = True, dstem = './data_offline/')
	# verify_model_load()
