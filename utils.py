''' Contains classes for streaming and recording LSL data 
in a free response format (as opposed to Asker structured format) 
'''
from pylsl import StreamInlet, resolve_stream
import threading, time, copy
import numpy as np
from pprint import pprint
import os, pickle, torch
import matplotlib.pyplot as plt
from StreamHandler import *

class PassiveCollector():
    ''' Passively collects data via StreamCollector, saves to pickle '''
    def __init__(self, data_path, name):
        self.data_path = data_path
        self.user_name = name
        self.sH = StreamHandler()
        self.sH.collect_threads()
        time.sleep(3)
        print("RESPONSES: ", self.sH.responses)
        print("SAMPLES: ", [(len(x[0]), x[1])  for x in self.sH.samples])
    def pickle(self):
        # create file name
        fnames = os.listdir(self.data_path)
        num_named = len([_ for _ in fnames if self.user_name in _])
        file_name = self.data_path + str(self.user_name) + str(num_named) + '.pickle'
        # sH dict 
        sh_dict = {}
        sh_dict['responses'] = self.sH.responses
        sh_dict['samples'] = self.sH.samples
        sh_dict['format'] = "[sample/label, timestamp]"
        with open(file_name, 'wb') as handle:
            pickle.dump(sh_dict, handle, protocol=pickle.HIGHEST_PROTOCOL)
        print("SAVED {}".file_name)
    def assign_labels(self):
        # assigns truth / lie values based on index 
        print("------REVIEW------")
        for r_ind in range(len(self.sH.responses)):
            retry_question = True
            while retry_question:
                print("Did you lie about statement {}? [y/n]".format(r_ind + 1))
                response = input().lower()
                if response == 'y':
                    self.sH.responses[r_ind][0] = 1 # 1 marks a lie
                    retry_question = False
                    break
                elif response == 'n':
                    self.sH.responses[r_ind][0] = 0 # 0 makes a not lie
                    retry_question = False
                    break
                else:
                    retry_question = True         

def full_collect(dstem = './data/'):
    print("What's your first name?")
    name = input().strip()
    data_path = dstem #'./data/'
    p = PassiveCollector(data_path, name)
    p.assign_labels()
    p.pickle()
    print(p.sH.responses)

def read_data(dstem):
    with open(dstem, 'rb') as handle:
        b = pickle.load(handle)
        print(b)


if __name__ == '__main__':

    full_collect()
    
    '''
    print("What's your first name?")
    name = input().strip()
    data_path = './data/'
    p = PassiveCollector(data_path, name)
    p.assign_labels()
    p.pickle()
    print(p.sH.responses)
    '''

    '''
    # try reading
    
    with open('./data/Daniel0.pickle', 'rb') as handle:
        b = pickle.load(handle)
        print(b)

    '''

    # read_data('./data/Daniel0.pickle')
    
    