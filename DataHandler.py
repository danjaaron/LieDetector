from utils import *
from sklearn import preprocessing
from scipy import signal

'''
Preprocess, transforms, filters and splits data
'''

'''
# NEW METHODOLOGY -- 2 control (truths), 2 lies about self, 2 ambiguous about self
... test (2) ambiguous 
... train (4) 2 controls, 2 lies 
'''

class DataHandler():
	def __init__(self, dir_path):
		# read data
		self.data_reader = DirReader(dir_path)
		self.X = self.data_reader.X
		self.y = self.data_reader.y 
		# get label indices (responses)
		self.li = np.array([y_i for y_i in range(len(self.y)) if self.y[y_i] != None])
		self.ui = np.array([y_i for y_i in range(len(self.y)) if not y_i in self.li])

		self.divide_labeled()
	def divide_labeled(self):
		# get label indices (responses)
		self.li = np.array([y_i for y_i in range(len(self.y)) if self.y[y_i] != None])
		self.ui = np.array([y_i for y_i in range(len(self.y)) if not y_i in self.li])
		# labeled
		self.X_l = self.X[self.li]
		self.y_l = self.y[self.li]
		# unlabeled 		
		self.X_u = self.X[self.ui]
		self.y_u = self.y[self.ui]
	def split(self, ratio):
		# split into train / test datasets (can only contain labeled inds)
		num_train = int(float(ratio)*len(self.li))
		train_inds = np.random.choice(self.li, num_train)
		assert(all([self.y[ti] >= 0 for ti in train_inds]))
		test_inds = [i for i in self.li if not i in train_inds]
		assert(all([self.y[ti] >= 0 for ti in test_inds]))
		print("num labeled: {}".format(len(self.li)))
		print("split into train size {}, test size {}".format(len(train_inds), len(test_inds)))
		self.X_train, self.y_train = self.X[train_inds, :], self.y[train_inds]
		self.X_test, self.y_test = self.X[test_inds, :], self.y[test_inds]
		self.divide_labeled()
	# Transform 
	def scale(self):
		self.X = preprocessing.scale(X)
		self.divide_labeled()
	def get_ratios(self):
		self.X = self.data_reader.X_ratios
		self.divide_labeled()
	# Filter 
	def bandpass(self, lowcut, highcut):
		# fc: cutoff freq
		fs = 10.0 # sampling freq of 10 hz
		nyq = fs / 2.0
		low = float(lowcut) / nyq
		high = float(highcut) / nyq 
		b, a = signal.butter(5, [low, high], 'band')
		# filter each feature
		for feature_ind in range(self.X.shape[1]):
			self.X[:, feature_ind] = signal.filtfilt(b, a, self.X[:, feature_ind])
		self.divide_labeled()
	def lowpass(self, fc):
		# fc: cutoff freq
		fs = 10.0 # sampling freq of 10 hz 
		w = float(fc) / (fs / 2.)
		b, a = signal.butter(5, w, 'low')
		# filter each feature
		for feature_ind in range(self.X.shape[1]):
			self.X[:, feature_ind] = signal.filtfilt(b, a, self.X[:, feature_ind])
		self.divide_labeled()
	def highpass(self, fc):
		# fc: cutoff freq
		fs = 10.0 # sampling freq of 10 hz 
		w = float(fc) / (fs / 2.)
		b, a = signal.butter(5, w, 'high')
		# filter each feature
		for feature_ind in range(self.X.shape[1]):
			self.X[:, feature_ind] = signal.filtfilt(b, a, self.X[:, feature_ind])
		self.divide_labeled()
		
	# FFT 
	def apply_FFT(self):
		''' applies FFT between labeled indices '''
		raise NotImplementedError # prob: what about end of sample? need a window before / after response for FFT

if __name__ == '__main__':
	d = DataHandler('./data/')
	d.split(0.8)
	print("pre")
	print(d.X)
	d.lowpass(0.1)
	print("post")
	print(d.X)