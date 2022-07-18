import pyaudio, wave, struct, math
import numpy as np

wavfile = 'acoustic.wav'

print('Play the wave file %s.' % wavfile)

# Open wave file (should be mono channel)
wf = wave.open( wavfile, 'rb' )

# Read the wave file properties
CHANNELS        = wf.getnchannels()     # Number of channels
RATE            = wf.getframerate()     # Sampling rate (frames/second)
signal_length   = wf.getnframes()       # Signal length
WIDTH           = wf.getsampwidth()     # Number of bytes per sample

print('The file has %d channel(s).'            % CHANNELS)
print('The frame rate is %d frames/second.'    % RATE)
print('The file has %d frames.'                % signal_length)
print('There are %d bytes per sample.'         % WIDTH)

p = pyaudio.PyAudio()

# Open audio stream
stream = p.open(
    format      = p.get_format_from_width(WIDTH),
    channels    = CHANNELS,
    rate        = RATE,
    input       = False,
    output      = True )

MAXVALUE = 2**15-1  # Maximum allowed output signal value (because WIDTH = 2)
minf = 100
maxf = 1000
fw = 200
delta = fw/RATE
damp = 0.05
Q1 = 2*damp
BLOCKLEN = 64

x1 = 0
x2 = 0
y11 = 0
y12 = 0

Fc = np.arange(start=minf, stop=maxf, step=delta)
while len(Fc) < signal_length:
    Fc = np.concatenate([Fc, Fc[::-1]])

Fc = Fc[0:signal_length]
# F1 = 2*math.sin(math.pi*Fc[0]/RATE)
# c = (math.tan(2*math.pi*Fc[0]/RATE)-1)/(math.tan(2*math.pi*Fc[0]/RATE)+1)
# d = -math.cos(math.pi*Fc[0]/RATE)

for i in range(0, signal_length):
    # Convert binary data to number
    input_bytes = wf.readframes(1)
    input_tuple = struct.unpack('h', input_bytes)  # One-element tuple
    input_value = input_tuple[0]/MAXVALUE  # Number

    # Set input to difference equation
    x0 = input_value

    # Difference equation
    c = (math.tan(2 * math.pi * Fc[i] / RATE) - 1) / (math.tan(2 * math.pi * Fc[i] / RATE) + 1)
    d = -math.cos(math.pi * Fc[i] / RATE)
    y1 = -c * x0 + d * (1-c) * x1 + x2 - d * (1-c) * y11 + c * y12
    # Band reject
    y0 = (x0+y1)*0.5
    # Or use Band pass
    # y0 = (x0 - y1) * 0.5

    y12 = y11
    y11 = y1
    x2 = x1
    x1 = x0

    y0_out = y0*MAXVALUE
    y0_out = np.clip(y0_out, -MAXVALUE, MAXVALUE)
    output_string = struct.pack('h', int(y0_out))  # 'h' for 16 bits
    stream.write(output_string)

print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
