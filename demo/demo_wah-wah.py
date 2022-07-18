import pyaudio, wave, struct, math
import numpy as np

wavfile = 'acoustic.wav'
# wavfile = 'autowah_original.wav'

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
minf = 500
maxf = 3000
fw = 2000

damp = 0.05
Q1 = 2*damp
BLOCKLEN = 1 # Larger size would encounter distortion of the sound effect.
num_block = int(signal_length/BLOCKLEN)
yh = 0
yb0 = 0
yb1 = 0
yl0 = 0
yl1 = 0
output_block = [0] * BLOCKLEN

delta = fw / RATE
Fc = np.arange(start=minf, stop=maxf, step=delta)
while len(Fc) < signal_length:
    Fc = np.concatenate([Fc, Fc[::-1]])

Fc = Fc[0:signal_length]
Fc_block = [Fc[i:i+BLOCKLEN] for i in range(num_block)]
F1 = 2*math.sin(math.pi*Fc_block[0][0]/RATE)

for i in range(num_block):
    # Convert binary data to number
    input_bytes = wf.readframes(BLOCKLEN)
    input_tuple = struct.unpack('h' * BLOCKLEN, input_bytes)  # One-element tuple
    for j in range(BLOCKLEN):
        # Difference equation
        x0 = input_tuple[j]/MAXVALUE
        yh = x0 - yl1 - Q1 * yb0
        yb0 = F1 * yh + yb1
        yl0 = F1 * yb0 + yl1
        F1 = 2 * math.sin(math.pi * Fc_block[i][j] / RATE)
        yb1 = yb0
        yl1 = yl0
        output_block[j] = int(yb0 * MAXVALUE)
    output_block = np.clip(output_block, -MAXVALUE, MAXVALUE)
    output_string = struct.pack('h' * BLOCKLEN, *output_block)  # 'h' for 16 bits
    stream.write(output_string)


print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
