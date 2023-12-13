import pyaudio
import wave
import requests
filename = 'http://9293-49-12-205-40.ngrok-free.app/media/audio_qADSwBY.wav'
 
# Defines a chunk size of 1024 samples per data frame.
chunk = 8192 

# Open sound file  in read binary form.
with open('answer.wav', 'wb') as a:
    resp = requests.get(filename)
    if resp.status_code == 200:
        a.write(resp.content)
        print('downloaded')
    else:
        print(resp.reason)
        exit(1)

file = wave.open('answer.wav', "rb")
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
while data != b'':
    stream.write(data)
    print(data[:16])
    data = file.readframes(chunk)
 
stream.stop_stream()
stream.close()
p.terminate()