from abc import ABC, abstractmethod 
import unittest, time
import sounddevice as sd 
import numpy as np 
from queue import Queue 
from pylsl import *
import threading 
from scipy.io import wavfile
import pyaudio 
import wave
from WavHandler import *
import sys


class StreamInterface():

    # TODO: change connected from init var to method call

    """ Streams data from a single source. """

    def __init__(self):

        self.name = str(type(self).__name__)
        self.timeout = 10
        self.q = Queue()
        self.outfile = "{}stream_out".format(self.name[0].lower())
        self.connected = False
        self.terminate_event = threading.Event()
        self.thread = threading.Thread(
                name = self.name,
                target = self.stream,
                args = (),
                daemon = True)

    def start(self):

        if self.connected:
            self.thread.start()
        else:
            error_msg = "{} is not connected, cannot start streaming.".format(self.name)
            raise Exception(error_msg)

    def stop(self):

        # TODO: stop stream, check if anything more to read, wait to read it all into queue, then quit

        self.terminate_event.set()
        self.thread.join(timeout = self.timeout)
        self.connected = False
        return self.q

    def stream(self): # thread target

        while not self.terminate_event.isSet():
            self.q.put(self.sample())

    @abstractmethod

    def connect(self):

        pass

    @abstractmethod

    def sample(self):

        pass

    

class AudioStream(StreamInterface):

    """ Streams microphone data. 
        TODO: 
         > stream callback mode
         > check overwritten chunks
    """

    def __init__(self):
        super(AudioStream, self).__init__()
        self.outfile = self.outfile + '.wav'
        self.CHUNK = 1024
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100

    def connect(self):

        self.p = pyaudio.PyAudio()

        self.stream = self.p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)

        self.connected = True

    def sample(self):
        pre_chunk_time = time.time()
        sample = self.stream.read(self.CHUNK)
        post_chunk_time = time.time()
        print("Audio sampled {} = {}".format(time.ctime(pre_chunk_time), time.ctime(post_chunk_time)))
        print("    ", len(sample), type(sample))
        return sample 

    def stop(self):
        super(AudioStream, self).stop()

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        return self.q



class OxyStream(StreamInterface):

    """ Streams OxySoft data. """
    # TODO: configure max_chunklen, max_bufferlen

    def connect(self):

        self.streams = resolve_byprop('type', 'NIRS', timeout = self.timeout) 
        if (len(self.streams) > 0):
            self.inlet = StreamInlet(self.streams[0])
            self.connected = True

        print("OxyStream connected: ", self.connected)

    def sample(self):
        # (!) TODO: metadata with inlet.info(), src @ https://github.com/labstreaminglayer/liblsl-Python/blob/master/pylsl/examples/HandleMetadata.py

        pre_chunk_time = time.time()
        chunk = self.inlet.pull_chunk(timeout = self.timeout) # [samples, timestamps]
        post_chunk_time = time.time()
        time_bias = self.inlet.time_correction(timeout = self.timeout)
        ret_tuple = (chunk[0], [float(_) + time_bias for _ in chunk[1]])
        return chunk[0]


class TestInit(unittest.TestCase):


    def test_instance(self):

        a = AudioStream()
        o = OxyStream()
        assert(isinstance(o, OxyStream) and isinstance(a, AudioStream))

    def test_has_queue(self):

        a = AudioStream()
        o = OxyStream()
        assert(hasattr(o, 'q'))
        assert(hasattr(a, 'q'))
        assert(not o.q is a.q)

    def test_thread_names(self):

        a = AudioStream()
        assert(a.thread.name == str(a.__class__.__name__))
        o = OxyStream()
        assert(o.thread.name == str(o.__class__.__name__))


    def test_no_connect(self):

        a = AudioStream()
        assert(not a.connected)
        o = OxyStream()
        assert(not o.connected)

    def test_connected(self):

        a = AudioStream()
        assert(not a.connected)
        a.connect()
        assert(a.connected)
        a.start()
        assert(a.connected)
        a.stop()
        assert(not a.connected)

    def test_terminate(self):

        a = AudioStream()
        a.connect()
        a.start()
        time.sleep(5)
        a.stop()
        assert(not a.thread.is_alive())

    def test_filled_queue(self):

        a = AudioStream()
        a.connect()
        a.start()
        time.sleep(2)
        a.stop()
        assert(a.q.qsize() > 0)
        print(a.q.qsize())

    def test_get_while_connected(self):

        a = AudioStream()
        a.connect()
        a.start()
        time.sleep(3)
        qs1 = a.q.qsize()
        assert(qs1 > 0)
        time.sleep(3)
        a.stop()
        qs2 = a.q.qsize()
        assert(qs2 > qs1)



if __name__ == "__main__":

    unittest.main()
