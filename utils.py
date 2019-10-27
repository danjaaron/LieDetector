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
        # print("RESPONSES: ", self.sH.responses)
        # print("SAMPLES: ", [(len(x[0]), x[1])  for x in self.sH.samples])
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
        print("SAVED {}".format(file_name))
    def assign_labels(self):
        # assigns truth / lie values based on index 
        print("------REVIEW------")
        for r_ind in range(len(self.sH.responses)):
            retry_question = True
            while retry_question:
                print("Response " + str(self.sH.responses[r_ind]) + " [T/F]:")
                # print("Statment {} truth value [t/f]: ".format(r_ind + 1))
                flush_input()
                sys.stdin.flush()
                response = input().lower()
                if response == 't':
                    self.sH.responses[r_ind][0] = 0 # 0 is a truth
                    retry_question = False
                    break
                elif response == 'f':
                    self.sH.responses[r_ind][0] = 1 # 1 is a lie
                    retry_question = False
                    break
                else:
                    print(".... enter t/f: ")
                    retry_question = True         

def full_collect(dstem = './data/'):
    print("What are your initials?")
    flush_input()
    sys.stdin.flush()
    name = input().strip()
    data_path = dstem #'./data/'
    p = PassiveCollector(data_path, name)
    p.assign_labels()
    p.pickle()
    # print(p.sH.responses)

def read_data(dstem):
    with open(dstem, 'rb') as handle:
        b = pickle.load(handle)
        # print(b)
    samples = b['samples']
    responses = b['responses']
    # print("SAMPLES: ", [(len(s[0]), s[1]) for s in samples])
    # print("# SAMPLES: ", len(samples))
    # print("RESPONSES: ", [r for r in responses])
    return [samples, responses]


class DirReader():
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.dir_files = [filename for filename in os.listdir(data_dir) if (".pickle" in filename)]
        # collect all fomr dir
        master_samples = list()
        master_responses = list()
        for d in self.dir_files:
            if '0' in d or '1' in d or '2' in d:
                continue
            s, r = read_data(self.data_dir + d)
            master_samples.extend(s)
            master_responses.extend(r)
        # print("LEN MASTER S: {} R: {}".format(len(master_samples), len(master_responses)))
        self.samples = master_samples
        self.responses = master_responses
        # get all timestamps 
        all_t = [_[1] for _ in self.samples]
        all_t.extend([_[1] for _ in self.responses])
        self.timestamps = sorted(all_t)
        # get samples and labels 
        X, y = [], []
        for t in self.timestamps:
            match_sample = [s[0] for s in self.samples if s[1] == t][0]
            match_label = [r[0] for r in self.responses if r[1] == t]
            if not match_label:
                match_label = None 
            else:
                match_label = match_label[0]
            X.append(match_sample)
            y.append(match_label)
        self.X = np.array(X)
        self.X_ratios = np.array([np.divide(x[::2], x[1::2]) for x in self.X])
        self.y = np.array(y)
        assert(len(self.X) == len(self.y))



if __name__ == '__main__':
    dr = DirReader('./data/')
    print(type(dr.X))
    print(dr.X[:, 1])
    # get data matrix
    # dr.matrix_stitch()


    