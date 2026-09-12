
import sounddevice as sd
import numpy as np

print(sd.query_devices())

data = sd.rec(16000, samplerate=16000, channels=1, dtype='float32')
sd.wait()
print("OK, shape:", data.shape)