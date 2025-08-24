import wave
import struct
import math

def generate_blip_wav(filename="blip.wav", duration_ms=100, freq=1000, volume=0.5, sample_rate=44100):
    num_samples = int(sample_rate * duration_ms / 1000.0)
    with wave.open(filename, 'w') as wav_file:
        wav_file.setparams((1, 2, sample_rate, num_samples, 'NONE', 'not compressed'))
        for i in range(num_samples):
            sample = volume * math.sin(2 * math.pi * freq * (i / sample_rate))
            packed_sample = struct.pack('<h', int(sample * 32767.0))
            wav_file.writeframes(packed_sample)

generate_blip_wav()
