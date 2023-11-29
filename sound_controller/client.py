import pyaudio
import asyncio
from socket import *
import sys

class AudioSenderController:

    def __init__(self, host, port_mic, port_dynamic) -> None:
        self.host = host
        self.port = port_mic
        self.addr = (host, port_mic)
        self.dynamic_addr = (host, port_dynamic)
        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.dynamic_socket = socket(AF_INET, SOCK_DGRAM)
        self.dynamic_socket.sendto(b'rasberry_pi', self.dynamic_addr)
        self.audio = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16 
        self.CHANNELS = 1  
        self.CHUNK = 512
        self.RATE = int(self.audio.get_device_info_by_index(0).get('defaultSampleRate'))
        self.mic_device_index = None

        for i in range(self.audio.get_device_count()):
            device_info = self.audio.get_device_info_by_index(i)
            if device_info['maxInputChannels'] > 0:
                self.mic_device_index = i
                break

        if self.mic_device_index is None:
                print("there is no mic")
                raise Exception('no microphone')
                
    def set_stream_settings(self, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=44100, CHUNK=512):
            self.RATE = RATE
            self.CHANNELS = CHANNELS
            self.CHUNK = CHUNK
            self.FORMAT = FORMAT
    
    def get_devices(self):
        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        print(info)
        print('RATE of MIC',int(self.audio.get_device_info_by_index(0).get('defaultSampleRate')))

        for i in range(0, numdevices):
            if (self.audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                print("Input Device id ", i, " - ", self.audio.get_device_info_by_host_api_device_index(0, i).get('name'))
        return info
    
    def record_microphone(self,stream):
        while True:
            data = stream.read(self.CHUNK,  exception_on_overflow=False)
            yield data
    
    def start_send_audio(self):
        stream = self.audio.open(format=pyaudio.paInt16,
                channels=1,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,)
        
        for data in self.record_microphone(stream):
            self.udp_socket.sendto(data, self.addr)


    def start_dynamic_stream(self, RATE = 44100, CHANNELS = 1, FORMAT = pyaudio.paInt16 ):
        print('START DYNAMIC STREAM')
        out_stream =self.audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, output=True)
        b = b''
        while True:
            data, _  = self.dynamic_socket.recvfrom(1024)
            if data == b'end':
                out_stream.write(b)
                b = b''
            else:
                b+=data



controller = AudioSenderController('192.168.0.7', 3001, 3002)
# controller.get_devices()


from threading import Thread, Lock


t1 = Thread(target=controller.start_send_audio)
t2 = Thread(target=controller.start_dynamic_stream, args=[44100, 2, 2])
t1.start()
t2.start()
t1.join()
t2.join()


# CHUNK = 512 
# def record_microphone(stream):
#     while True:
#         data = stream.read(CHUNK,  exception_on_overflow=False)
#         yield data


# host = '192.168.0.7'
# port = 5437
# addr = (host,port)
# udp_socket = socket(AF_INET, SOCK_DGRAM)

# dynamic_socket = socket(AF_INET, SOCK_DGRAM)

# dynamic_socket.sendto(b'rasberry_pi',(host, 5438))

# async def send_audio():
#     p = pyaudio.PyAudio()
#     mic_device_index = None
#     for i in range(p.get_device_count()):
#         device_info = p.get_device_info_by_index(i)

#         if device_info['maxInputChannels'] > 0:
#             mic_device_index = i
#             break

#     if mic_device_index is None:
#         print("there is no mic")
#         return
#     stream = p.open(format=pyaudio.paInt16,
#                     channels=1,
#                     rate=int(p.get_device_info_by_index(1).get('defaultSampleRate')),
#                     input=True,
#                     frames_per_buffer=512,)

#     for data in record_microphone(stream):
#         print('send')
#         udp_socket.sendto(data, addr)


# async def play_audio():

#     p = pyaudio.PyAudio()
#     FORMAT = pyaudio.paInt16 
#     CHANNELS = 1
#     RATE = 44100 

#     out_stream =p.open(format=FORMAT, channels=CHANNELS,
#                             rate=RATE, output=True)

#     data, addr  = dynamic_socket.recvfrom(65536)

#     out_stream.write(data)


# asyncio.get_event_loop().run_until_complete(play_audio())
# asyncio.get_event_loop().run_until_complete(send_audio())

