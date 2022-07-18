import numpy as np
import pyaudio, wave, struct, math


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
minf = 500
maxf = 1000
fw = 20
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
c = (math.tan(2*math.pi*Fc[0]/RATE)-1)/(math.tan(2*math.pi*Fc[0]/RATE)+1)
d = -math.cos(math.pi*Fc[0]/RATE)

for i in range(0, signal_length):
    # Convert binary data to number
    input_bytes = stream.read(1, exception_on_overflow = False)
    input_tuple = struct.unpack('h', input_bytes)  # One-element tuple
    input_value = input_tuple[0]/MAXVALUE  # Number

    # Set input to difference equation
    x0 = input_value

    # Difference equation
    y1 = -c * x0 + d * (1-c) * x1 + x2 - d * (1-c) * y11 + c * y12
    # Band reject
    y0 = (x0+y1)*0.5
    # Or use Band pass
    # y0 = (x0 - y1) * 0.5
    
    c = (math.tan(2 * math.pi * Fc[i] / RATE) - 1) / (math.tan(2 * math.pi * Fc[i] / RATE) + 1)
    d = -math.cos(math.pi * Fc[i] / RATE)
    y12 = y11
    y11 = y1
    x2 = x1
    x1 = x0

    y0_out = y0*MAXVALUE
    y0_out = np.clip(y0_out, -MAXVALUE, MAXVALUE)

    output_string = struct.pack('h', int(y0_out))  # 'h' for 16 bits
    stream.write(output_string)

stream.stop_stream()
stream.close()
p.terminate()

print('* Finished')
