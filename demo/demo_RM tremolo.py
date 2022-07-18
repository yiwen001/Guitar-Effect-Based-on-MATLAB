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
minf = -0.5
maxf = 0.5
delta = 5e-4

BLOCKLEN = 64

# Use triangular wave
Fc = np.arange(start=minf, stop=maxf, step=delta)
while len(Fc) < signal_length:
    Fc = np.concatenate([Fc, Fc[::-1]])

Fc = Fc[0:signal_length]

for i in range(0, signal_length):
    # Convert binary data to number
    input_bytes = wf.readframes(1)
    input_tuple = struct.unpack('h', input_bytes)  # One-element tuple
    input_value = input_tuple[0]/MAXVALUE  # Number

    # Set input to difference equation
    x0 = input_value

    # Difference equation
    y0 = x0 * Fc[i]

    y0_out = y0*MAXVALUE
    y0_out = np.clip(y0_out, -MAXVALUE, MAXVALUE)
    output_string = struct.pack('h', int(y0_out))  # 'h' for 16 bits
    stream.write(output_string)

print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
