import pyaudio
import wave
 
filename = 'test.wav'
 
# Defines a chunk size of 1024 samples per data frame.
chunk = 8192 

# Open sound file  in read binary form.
file = wave.open(filename, 'rb')
 
# Initialize PyAudio
p = pyaudio.PyAudio()
 
# Creates a Stream to which the wav file is written to.
# Setting output to "True" makes the sound be "played" rather than recorded
print( p.get_format_from_width(file.getsampwidth()),  file.getnchannels(), file.getframerate())
stream = p.open(format = p.get_format_from_width(file.getsampwidth()),
                channels = file.getnchannels(),
                rate = file.getframerate(),
                output = True)
 
# Read data in chunks
data = file.readframes(chunk)
 
# Play the sound by writing the audio data to the stream
while data != '':
    stream.write(data)
    data = file.readframes(chunk)
 
stream.stop_stream()
stream.close()
p.terminate()