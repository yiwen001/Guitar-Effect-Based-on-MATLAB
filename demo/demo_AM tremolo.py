import pyaudio, wave, struct, math
import numpy as np

wavfile = 'acoustic.wav'

print('Play the wave file %s.' % wavfile)

# Open wave file (should be mono channel)
wf = wave.open(wavfile, 'rb')

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
fw = 100
alpha = 0.5
BLOCKLEN = 64

for i in range(0, int(signal_length/BLOCKLEN)):
    # Convert binary data to number
    input_bytes = wf.readframes(BLOCKLEN)
    input_tuple = struct.unpack('h' * BLOCKLEN, input_bytes)  # One-element tuple

    # Difference equation
    output_block = [int((1 + alpha * math.sin(2 * math.pi * i * fw / RATE)) * n) for n in input_tuple]

    y0_out = np.clip(output_block, -MAXVALUE, MAXVALUE)
    output_string = struct.pack('h' * BLOCKLEN, *y0_out)  # 'h' for 16 bits
    stream.write(output_string)


print('* Finished')

stream.stop_stream()
stream.close()
p.terminate()
