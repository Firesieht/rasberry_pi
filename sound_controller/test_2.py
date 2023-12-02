import librosa



y, s = librosa.load('res.wav', sr=8000) # Downsample 44.1kHz to 8kHz

print(y,s)