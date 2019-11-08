from pylab import *
from scipy.io import wavfile
import matplotlib.pyplot as plt
import pyaudio 
import sounddevice as sd
from scipy import signal
import wave

'''
### (!) TODO: stream NIRS data in parallel, auto break up data by audio chunks, assemble into pytorch dataset. 

WavHandler: inputs, transforms, and outputs / visualizes wav file data
Notes: dont filter by brickwalling FFT, actually filter s1 into self.filt then reapply fft (https://dsp.stackexchange.com/questions/6220/why-is-it-a-bad-idea-to-filter-by-zeroing-out-fft-bins)
'''

class WavHandler():
	def __init__(self):
		self.CHUNK = 1024
		self.FORMAT = pyaudio.paInt16
		self.CHANNELS = 1
		self.RATE = 44100
		self.RECORD_SECONDS = 5
		# self.pAudi = pyaudio.PyAudio()

	''' INPUT '''
	
	def record(self, WAVE_OUTPUT_FILENAME = "output.wav"):
		p = pyaudio.PyAudio()

		stream = p.open(format=self.FORMAT,
		                channels=self.CHANNELS,
		                rate=self.RATE,
		                input=True,
		                frames_per_buffer=self.CHUNK)

		print("* recording")

		frames = []

		for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
		    data = stream.read(self.CHUNK)
		    frames.append(data)

		print("* done recording")

		stream.stop_stream()
		stream.close()
		p.terminate()

		'''
		wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
		wf.setnchannels(self.CHANNELS)
		wf.setsampwidth(p.get_sample_size(self.FORMAT))
		wf.setframerate(self.RATE)
		wf.writeframes(b''.join(frames))
		wf.close()
		'''

		self.writeWav(data = frames, outfile = WAVE_OUTPUT_FILENAME)

		print("saved recording {} and read into WavHandler".format(WAVE_OUTPUT_FILENAME))

		self.readWav(WAVE_OUTPUT_FILENAME)

	@staticmethod
	def writeWav(self, data, outfile = "write.wav"):
		''' Write data array to wav file '''
		p = pyaudio.PyAudio()
		wf = wave.open(outfile, 'wb')
		wf.setnchannels(self.CHANNELS)
		wf.setsampwidth(p.get_sample_size(self.FORMAT))
		wf.setframerate(self.RATE)
		wf.writeframes(b''.join(data))
		wf.close()
		p.terminate()

	def readWav(self, filename):
		''' read and do basic processing '''
		if not '.wav' in filename:
			filename = filename + '.wav'
		plot_amp = True
		plot_pwr = True
		plot_pwr_dB = True
		sampFreq, snd = wavfile.read(filename)
		assert(sampFreq == self.RATE)
		numSamples = snd.shape[0]
		assert(len(snd.shape) == 1) # assert single channel wav file
		duration = numSamples / sampFreq
		print("Read {} samples at {} Hz over {:.2f} seconds".format(numSamples, sampFreq, duration))
		# convert snd from +/- int to floating point between -1 and 1 
		s1 = snd / (2.**15)
		# get time array
		timeArray = arange(0, numSamples, 1)
		timeArray = timeArray / sampFreq
		timeArray = timeArray * 1000  #scale to milliseconds
		# store all newly created variables 
		self.readDict = {k: v for k, v in locals().items() if not k in ['self', 'filename']}
		self.filt = copy(s1)

	''' TRANSFORM '''

	def filter(self, filterType, fc):
		assert(filterType in ['low', 'high', 'band'])
		if isinstance(fc, list):
			fc = np.array(fc)
		else:
			fc = float(fc)
		nyq = self.RATE / 2.0
		filter_order = 5
		w = fc / nyq
		b, a = signal.butter(filter_order, w, filterType)
		self.filt = signal.filtfilt(b, a, copy(self.readDict['s1']))
	def getFFT(self):
		''' Gets FFT on filtered from read wav '''
		p = fft(self.filt) # fft obtains power spectrum over all sample points, returns freq components mag and phase with complex 
		nUniquePts = int(ceil((self.readDict['numSamples']+1)/2.0)) # because fft returns symmetrical, numUnique is only half of p
		p = p[0:nUniquePts]
		# fft returns magnitude and phase of frequency components with complex. abs(fft(signal)) returns magnitude of freq coponents.
		p = abs(p) 
		p = p / float(self.readDict['numSamples']) # scale by the number of points so that
		                 # the magnitude does not depend on the length 
		                 # of the signal or on its sampling frequency  
		p = p**2  # square it to get the power 

		# multiply by two (see technical document for details)
		# odd nfft excludes Nyquist point
		if self.readDict['numSamples'] % 2 > 0: # we've got odd number of points fft
		    p[1:len(p)] = p[1:len(p)] * 2
		else:
		    p[1:len(p) -1] = p[1:len(p) - 1] * 2 # we've got even number of points fft

		freqArray = arange(0, nUniquePts, 1.0) * (self.readDict['sampFreq'] / self.readDict['numSamples']) 

		self.freqArray = freqArray
		self.p = p

	''' OUTPUT '''

	def plot(self, plotType, max_freq = None, filename = None):
		self.getFFT()
		if max_freq is None:
			max_freq = max(self.freqArray)
		freq_inds = [i for i, v in enumerate(self.freqArray) if v < max_freq]
		# check for existing read
		if filename is None:
			assert(hasattr(self, 'readDict'))
		else:
			self.readWav(filename)
		# plot according to type 
		if plotType == 'a':
			# plots amplitude
			plt.xlabel('Time (ms)')
			plt.ylabel('Amplitude')
			plt.plot(self.readDict['timeArray'], abs(self.filt), color='k')
			plt.show()
		elif plotType == 'p':
			# plots power of each frequency component
			plt.plot(self.freqArray[freq_inds], self.p[freq_inds], color='k') # / 1000 for kHz
			plt.xlabel('Frequency (Hz)')
			plt.ylabel('Power')
			plt.show()
		elif plotType == 'pdb':
			# plots dB power of each frequency component
			plt.plot(self.freqArray[freq_inds], 10*log10(self.p)[freq_inds], color='k')
			plt.xlabel('Frequency (Hz)')
			plt.ylabel('Power (dB)')
			plt.show()
	
	def play(self):
		''' Plays the filtered read using sounddevice '''
		print("begin playback")
		play_filt = np.array(self.filt * (2.**15), dtype = np.int16)
		sd.play(play_filt, self.RATE)
		sd.wait()
		print("end playback")
		

if __name__ == "__main__":
	w = WavHandler()
	# w.record()
	w.readWav('./astream_out')
	w.play()
	# w.plot('a', 600)
	# w.filter('low', 5000)
	# w.play()
	# w.plot('a', 600)