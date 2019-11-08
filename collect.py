from StreamInterface import *
import sys, inspect, queue
from matplotlib import pyplot as plt 
from WavHandler import *

class Collector():

    # TODO
    # > stop all threads if any exception occurs
    # > line up timestamps
    # > on stop, check buffer for unread chunks and read all in before terminating 
    # > unit test bit / byte size to ensure accurate sampling rate (e.g. audio stream 2048 * # samples * 0.5 / duration = fs)

    def __init__(self, stream_names = None):

        # get specified streams 
        all_streams = [s() for s in StreamInterface.__subclasses__()]
        if not stream_names is None:
            all_streams = [s for s in all_streams if s.name in stream_names]
        
        # stream and data dicts
        self.streams = {s.name: s for s in all_streams}
        self.data = dict()
        
        print("Collected streams: ", list(self.streams.keys()))

    def _start(self):

        for name, stream in self.streams.items():
            print("Starting {}".format(name))
            stream.connect()
            stream.start()


    def _stop(self):

        for name, stream in self.streams.items():

            print("Stopping {}".format(name))
            q = stream.stop()
            # dump queue 
            d = list()
            while not q.empty():
                d.append(q.get())

            print(np.array(d).shape)
            
            self.data[name] = d
            print("Returned {} samples for {} stream".format(len(d), name))


    def collect(self, t):
        
        print('Starting collection')
        self._start()
        time.sleep(t)
        self._stop()
        print('Finished collecting')

    def write(self):

        pass

    def playback(self):

        ''' Plays back audio data '''

        print("Playing back audio data")

        # audio stream object and data
        astream = self.streams['AudioStream']
        data = self.data['AudioStream']
        playback_file = "playback.wav"

        # create new wav file
        wf = wave.open(playback_file, 'wb')
        wf.setnchannels(astream.CHANNELS)
        wf.setsampwidth(astream.p.get_sample_size(astream.FORMAT))
        wf.setframerate(astream.RATE)
        wf.writeframes(b''.join(data))
        wf.close()

        # play the new wav file 
        wh = WavHandler()
        wh.readWav(playback_file)
        wh.play()
        
        print("Completed audio playback")
        



if __name__ == '__main__':
    c = Collector("OxyStream")
    c.collect(10)
