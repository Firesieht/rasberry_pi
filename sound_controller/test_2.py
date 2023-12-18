import pyaudio
import wave
import requests
filename = 'http://9293-49-12-205-40.ngrok-free.app/media/audio_qADSwBY.wav'
 
chunk = 8192 

with open('answer.wav', 'wb') as a:
    resp = requests.get(filename)
    if resp.status_code == 200:
        a.write(resp.content)
        print('downloaded')
    else:
        print(resp.reason)
        exit(1)

file = wave.open('answer.wav', "rb")
p = pyaudio.PyAudio()
 

print( p.get_format_from_width(file.getsampwidth()),  file.getnchannels(), file.getframerate())
stream = p.open(format = p.get_format_from_width(file.getsampwidth()),
                channels = file.getnchannels(),
                rate = file.getframerate(),
                output = True)
 
data = file.readframes(chunk)


while data != b'':
    print(data[:16])
    stream.write(data)
    data = file.readframes(chunk)
 
stream.stop_stream()
stream.close()
p.terminate()
file.close()
