'''
Streams LSL data and predicts in real time
'''

import threading
import time, sys
import logging, keyboard
from pylsl import StreamInlet, resolve_stream
from StreamHandler import *
from utils import *
from DataHandler import *

class StreamPredict(StreamHandler):
    ''' Predicts on stream '''
    def __init__(self, data_stem, model_name):
        self.model = self.load_model(model_name)
        self.d = DataHandler(data_stem)
        self.d.bandpass(0.1, 2.0)
        self.d.scale()
        super().__init__()
    def load_model(self, model_name):
        # get full filename
        full_name = './models/' + model_name + str(len([f for f in os.listdir('./models/') if model_name in f])-1) + '.pickle'
        print("Loading model: ", full_name)
        model = pickle.load(open(full_name, 'rb'))
        print("Model loaded!")
        return model
    def sample(self):
        ''' Pulls a single sample from inlet '''
        # assert(hasattr(self, inlet))
        # logging.debug("SAMPLE: pulling now")
        sample, timestamp = self.inlet.pull_sample()
        self.latest_timestamp = timestamp
        full_sample = [sample, timestamp]
        self.samples.append(full_sample)
        # PREDICT 
        self.d.append_sample(full_sample)
        #self.d.y = np.append(self.d.y, None)
        self.d.bandpass(0.1, 2.0)
        self.d.scale()
        pred = self.model.pred(self.d.X[-1])
        print("PREDICTION: ", pred)
        return full_sample

if __name__ == '__main__':
    sp = StreamPredict("./data/", "QDA")