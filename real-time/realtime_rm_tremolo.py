import pyaudio, wave, struct, math
import numpy as np

WIDTH = 2           # bytes per sample
CHANNELS = 1        # mono
RATE = 8000         # frames per second
BLOCKLEN = 1024     # block length in samples
DURATION = 13      # Duration in seconds
signal_length=RATE*DURATION
x_show = []
y_show = []
colors = []

K = int( DURATION * RATE / BLOCKLEN )   # Number of blocks

print('Block length: %d' % BLOCKLEN)
print('Number of blocks to read: %d' % K)
print('Duration of block in milliseconds: %.1f' % (1000.0 * BLOCKLEN/RATE))

n = range(0, BLOCKLEN)

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
minf = -0.5
maxf = 0.5
# fw = 2000
delta = 5e-4

BLOCKLEN = 64
# Use triangular wave
Fc = np.arange(start=minf, stop=maxf, step=delta)
while len(Fc) < signal_length:
    Fc = np.concatenate([Fc, Fc[::-1]])

Fc = Fc[0:signal_length]

for i in range(0, signal_length):
    # Convert binary data to number
    input_bytes = stream.read(1, exception_on_overflow = False)
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

stream.stop_stream()
stream.close()
p.terminate()

pyplot.ioff()           # Turn off interactive mode
pyplot.show()           # Keep plot showing at end of program
pyplot.close()

print('* Finished')
