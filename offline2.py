'''
Offline QDA, but it verifies correct answers AFTER submitting predictions (so retained prompt as well)
... note -- only uses my data as base, should use as many peoples as possible (automate this process)
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

def offline_pre(dstem = './data_offline/'):
	''' Generate new data from new interrogation, then store offline and predict with saved QDA model '''
	''' NOTE: collect False makes NO SENSE. The whole point is to collect, and only show predictions on
	that most recent collect, and no other pickles in the folder. '''

	# load latest QDA model 
	clf = load_model("QDA")

	# collect data
	p = offline_collect(dstem = dstem, save = True) # hard False so that can assign labels etc

	# process last collect
	d = DataHandler(dir_path = dstem)
	d.bandpass(0.1, 2.0)
	# d.split(0.8)
	d.scale()

	'''
	# (1) - get timestamps of recent responses (should have char labels)
	response_timestamps = [r[1] for r in d.data_reader.responses if type(r[0]) == type('bro')]
	print("response timestamps: ", response_timestamps)
	# (2) - get samples by timestamps of recent responses (not li)
	response_ts_indices = [d.data_reader.timestamps.index(rts) for rts in response_timestamps]
	# (3) - predict samples of most recent responses 
	preds = clf.predict(d.X[response_ts_indices, :])
	# (4) - assign labels
	print("PREDICTIONS: ", preds)
	
	p.assign_labels()
	p.pickle()
	sys.exit()

	'''
	print("pred by ind response")
	pred_text_dict = {1: 'LIE', 0: 'TRUTH'}
	# PREDICT WITH RESPONSE PROMPT 
	for r in d.data_reader.responses:
		response_text, response_time = r
		if response_text is None or type(response_text) != type('bro'):
			continue 
		response_index = d.data_reader.timestamps.index(response_time)
		pred = clf.predict([d.X[response_index, :]])
		predicted_text = pred_text_dict[pred[0]]
		print("RESPONSE {} PREDICTED {} ".format(response_text, predicted_text))
	# response_timestamps = [r[1] for r in d.data_reader.responses if type(r[0]) == type('bro')]
	sys.exit()
	'''
	# predict on the LABELED indices 
	preds = clf.predict(d.X[d.li, :])
	print("PREDICTIONS: ", preds)
	print(d.data_reader.responses)
	print(len(d.data_reader.timestamps))
	print(len(d.X))
	'''

	'''
	print("TRUE: ", d.y[d.li])
	assert(len(preds) == len(d.li))

	if save_new:
		# p.assign_labels()
		p.pickle()
	

	# to get online .... 
	# .... I need ALL the samples to bandpass and scale, but only need to actually predict on labeled
	'''

if __name__ == '__main__':

	offline_pre(dstem = './data_offline/')
	# verify_model_load()
