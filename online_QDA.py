from utils import * 
from StreamHandler import * 
from DataHandler import * 
# import lda 
# from lda import load_model, pickle_model

''' TODO
(1) complete online classification class 
(2) gather Alexis data 
(3) gather others data + pictures
... (!) red DAQ channel handling 

FUTURE
(1) model benchmarker
... try:
... 	FFT 
... 	CNN
(2) formalize methodology  
(3) confidence threshold for lie/truth decision 
(4) audio spectrum fusion 
'''

def load_model(filename):
	# get full filename
	full_name = './models/' + filename + str(len([f for f in os.listdir('./models/') if filename in f])-1) + '.pickle'
	print("Loading model: ", full_name)
	model = pickle.load(open(full_name, 'rb'))
	print("Model loaded!")
	return model

class OnlineQDA():
	def __init__(self, modelname):
		''' predict incoming samples from sH '''
		self.model = load_model(modelname)
		self.sH = StreamHandler
		self.sthread = threading.Thread(target = self.sH, daemon = True)
		self.sthread.start()
		self.monitor_time = 100 # time to predict online
	def monitorStream(self):
		start_time = time.time()
		prev_t = 0.
		# monitor the stream for incoming samples 
		while (time.time() - start_time) <= self.monitor_time:
			if self.sH.latest_timestamp != prev_t:
				print("New sample monitored!")
				prev_t = float(self.sH.latest_timestamp)
			else:
				print(self.sH.latest_timestamp)
			# else:
				# print("Same sample")
		print("Monitor time exceeded.")
		'''
			curr_timestamp = self.sH.latest_timestamp
			if curr_timestamp != prev_timestamp:
				print("New sample at {}!".format(curr_timestamp))
			else:
				print("Same sample.")
			prev_timestamp = self.sH.latest_timestamp
		print("Exiting monitor stream")
		'''


if __name__ == "__main__":
	oQDA = OnlineQDA("QDA")
	oQDA.monitorStream()


