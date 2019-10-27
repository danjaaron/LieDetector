'''
Handles streaming LSL data
# (!) TODO: Record methodology (prompt, response)
'''

import threading
import time, sys
import logging, keyboard
from pylsl import StreamInlet, resolve_stream


class StreamHandler():
    ''' Handles streams, threads, etc. '''
    def __init__(self):
        # init time variables 
        self.stream_t = 1 # sampling max wait on CONN status update before retry 
        self.handler_t = 3 # timeout to connect to LSL before counting as an attempt (twrds attempt max / quit)
        self.handler_attempts = 4
        self.key_t = 1 # time to sleep after key press
        self.num_responses = 0
        self.latest_timestamp = 0

        # key press events 
        self.terminate_key = 'q' # this key press triggers global terminate
        self.response_key = 'p' # this key press marks a response entry
        self.response_pressed = False
        # self.response_keyword = None

        # events 
        self.stream_event = threading.Event()
        self.terminate_event = threading.Event()
        self.response_event = threading.Event()

        # timestamping 
        self.latest_timestamp = 0

        # saved data 
        self.samples = list() # [[sample, timestamp], ... ]
        self.responses = list() # [[label, timestamp], ...]


        # init logging etc
        logging.basicConfig(level=logging.DEBUG,
                    format='(%(threadName)-9s) %(message)s',)
        

        self.t2 = threading.Thread(name='handler', 
                      target=self.handler, 
                      args=())
        self.t2.start()

        self.t3 = threading.Thread(name='connect', 
                          target=self.connect, 
                          daemon = True,
                          args=())
        self.t3.start()

        self.t4 = threading.Thread(name='stream', 
                          target=self.stream, 
                          args=( ))
        self.t4.start()

        self.keyhandle_thread = threading.Thread(name='keyhandle', 
                          target=self.keyhandle, 
                          args=( ))
        self.keyhandle_thread.start() 

    def collect_threads(self):
        self.t2.join()
        print("Ready to begin.")
        # NOTE: dont need to collect stream, connect threads in order to get samples
        # self.t3.join()
        # print("joined t3")
        # self.t4.join()
        # print("joined t4")
        self.keyhandle_thread.join()
        print("joined keyhandle")
        print("returning responses")
        return self.samples #self.responses


    def check_terminate(self):
        if keyboard.is_pressed(self.terminate_key) or self.terminate_event.isSet():
            print("TERMINATING")
            print("NUM RESPONSES: ", self.num_responses)
            print("RESPONSES: ", self.responses)
            self.terminate_event.set()
            return True
        # elif keyboard.is_pressed(self.response_key):
            # print("CHECK: response key pressed")
            # return False

    def keyhandle(self):
        ''' Initiates a terminate signal if a specific key is pressed '''
        logging.debug("KEYHANDLE: Press Q at any time to TERMINATE all threads")
        logging.debug("KEYHANDLE: Press P at any time to enter PROMPT, and SPACEBAR to mark RESPONSE")
        # logging.debug("KEYHANDLE: Press SPACEBAR at any time to mark RESPONSE")
        while not self.check_terminate():
            if self.check_terminate():
                logging.debug("KEYHANDLE: Terminate called -- QUIT")
                return
            try:
                if keyboard.is_pressed(self.terminate_key) or self.check_terminate():
                    print('KEYQUIT: Q pressed, triggering TERMINATE')
                    self.terminate_event.set()
                    return
                elif keyboard.is_pressed(self.response_key):
                    # response recorded
                    if not self.response_pressed:
                        self.response_pressed = True
                        flush_input()
                        print('KEYHANDLER: Type PROMPT, return after response complete.')
                        # sys.stdin.flush()
                        latest_prompt = str(input("Prompt: "))
                        ltimestamp = self.latest_timestamp
                        self.num_responses += 1
                        self.responses.append([latest_prompt, ltimestamp]) # leave label as none by default
                    # key being held down
                    elif self.response_pressed:
                        pass
                else:
                    # pass
                    self.response_pressed = False 
            except Exception as ex:
                print("KEYEXCEPT: ", ex)
                print("KEYHANDLER: breaking....")
                break 


    def handler(self):
        attempt = 0
        
        while not self.stream_event.isSet():
            if self.check_terminate():
                # logging.debug("HANDLER: Terminate called -- QUIT")
                return
            # logging.debug('HANDLER waiting to hear from LSL')
            event_is_set = self.stream_event.wait(self.handler_t)
            if self.check_terminate():
                # logging.debug("HANDLER: Terminate called -- QUIT")
                return
            attempt += 1
            # logging.debug('HANDLER event set: %s', event_is_set)
            # logging.debug('HANDLER attempt {}/{}'.format(attempt, self.handler_attempts))
            # stream  
            if event_is_set:
                logging.debug('HANDLER SUCCESS - event is SET! Keep streaming until im told to stop') 
                self.stream_event.set()
                # mock_stream(e)
                # time.sleep(5)
                # logging.debug('HANDLER Time to stop streaming, CLEARING event and TERMINATING')
                # assert NotImplementedError # IMPLEMENT: take keyboard input
                # self.stream_event.clear()
            elif attempt >= self.handler_attempts:
                # logging.debug('HANDLER FAIL - attempt max reached! Quitting, TERMINATING')
                self.terminate_event.set()
                return
            else:
                logging.debug('HANDLER retrying connection')
        # logging.debug('HANDLER broke out cause event set')

    def connect(self):
        # logging.debug('CONN: initializing stream / inlet')
        # initiate LSL
        self.streams = resolve_stream('type', 'NIRS')
        self.inlet = StreamInlet(self.streams[0])
        # attempts to pull sample 
        # logging.debug('CONN: pulling initial sample')
        sample, timestamp = self.sample() #self.inlet.pull_sample()
        # print("CONN: got (t, s): ({}, {}/{})".format(timestamp, len([_ for _ in sample if _ != 0.0]), len(sample), sample))
        # connects to LSL, starts streaming
        if self.check_terminate():
            # logging.debug("CONN: Terminate called -- QUIT")
            return
        # logging.debug('CONN: SETTING stream_event and returning')
        self.stream_event.set()
        return

    def sample(self):
        ''' Pulls a single sample from inlet '''
        # assert(hasattr(self, inlet))
        # logging.debug("SAMPLE: pulling now")
        sample, timestamp = self.inlet.pull_sample()
        self.latest_timestamp = timestamp
        full_sample = [sample, timestamp]
        self.samples.append(full_sample)
        return full_sample

    def stream(self):
        # self.samples.append("test")
        # waits for stream event to be set by CONN, then samples while event is still set
        event_is_set = self.stream_event.isSet()
        while not event_is_set:
            if self.check_terminate():
                # logging.debug("STREAM: Terminate called -- QUIT")
                return
            # logging.debug("STREAM: no event, can't collect, retry with 1 s timeout")
            event_is_set = self.stream_event.wait(self.stream_t)

        logging.debug("STREAM: events up, time to sample!")
        # print("STREAM: PRE thread enum ", list(threading.enumerate()))    
        # while streaming is on
        while event_is_set:
            # check if global terminate
            if self.check_terminate():
                # logging.debug("STREAM: Terminate called -- QUIT")
                return
            # pull sample 
            # logging.debug("STREAM: Sampling")
            sample, timestamp = self.sample() #self.inlet.pull_sample()
            # print("STREAM: got (t, s>0 len, s): ({}, {}/{}, {})".format(timestamp, len([_ for _ in sample if _ != 0.0]), len(sample), sample))
            # check if stream event changed
            event_is_set = self.stream_event.wait(self.stream_t)

        # logging.debug("STREAM: event was CLEARED. Time to stop sampling.")
        # check active threads
        # print("STREAM: POST thread enum ", list(threading.enumerate())) # all stopped except itself, cause it hasnt yet returned

def flush_input():
    # print("input flushing")
    try:
        import msvcrt
        while msvcrt.kbhit():
            msvcrt.getch()
    except ImportError:
        import sys, termios    #for linux/unix
        termios.tcflush(sys.stdin, termios.TCIOFLUSH)

if __name__ == '__main__':
    s = StreamHandler()
    s.collect_threads()
    print("RESPONSES: ", s.responses)
    print("SAMPLES: ", s.samples)
    # write to dataset                                

 