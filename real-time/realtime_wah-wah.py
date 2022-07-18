import pyaudio, wave, struct, math
import numpy as np

WIDTH = 2           # bytes per sample
CHANNELS = 1        # mono
RATE = 8000         # frames per second
BLOCKLEN = 1       # Larger size would encounter distortion of the sound effect.
DURATION = 13      # Duration in seconds
signal_length=RATE*DURATION
num_block = int(signal_length/BLOCKLEN)
print('Block length: %d' % BLOCKLEN)
print('Number of blocks to read: %d' % num_block)
print('Duration of block in milliseconds: %.1f' % (1000.0 * BLOCKLEN/RATE))

# Open the audio stream
# Initialize the output block
output_block = BLOCKLEN * [0]

p = pyaudio.PyAudio()
PA_FORMAT = p.get_format_from_width(WIDTH)
stream = p.open(
    format = PA_FORMAT,
    channels = CHANNELS,
    rate = RATE,
    input = True,
    output = True)


MAXVALUE = 2**15-1  # Maximum allowed output signal value (because WIDTH = 2)
minf = 500
maxf = 3000
fw = 2000
delta = fw/RATE
damp = 0.05
Q1 = 2*damp
BLOCKLEN = 1
yh = 0
yb0 = 0
yb1 = 0
yl0 = 0
yl1 = 0

Fc = np.arange(start=minf, stop=maxf, step=delta)
while len(Fc)<signal_length:
    Fc = np.concatenate([Fc, Fc[::-1]])

x = np.arange(start=0, stop=signal_length, step=1)
Fc = Fc[0:signal_length]
Fc_block = [Fc[i:i+BLOCKLEN] for i in range(num_block)]
F1 = 2*math.sin(math.pi*Fc_block[0][0]/RATE)

for i in range(num_block):
    # Convert binary data to number
    input_bytes = stream.read(BLOCKLEN, exception_on_overflow=False)
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

stream.stop_stream()
stream.close()
p.terminate()


print('* Finished')
