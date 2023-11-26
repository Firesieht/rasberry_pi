import pyaudio
import asyncio
from socket import *
import sounddevice

def record_microphone(stream):
    CHUNK = 1024
    while True:
        data = stream.read(CHUNK)
        yield data

host = '192.168.0.7'
port = 777
addr = (host,port)

udp_socket = socket(AF_INET, SOCK_DGRAM)


async def send_audio():
    p = pyaudio.PyAudio()
    mic_device_index = None
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info['maxInputChannels'] > 0:
            mic_device_index = i
            break

    if mic_device_index is None:
        print("there is no mic")
        return

    stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=int(p.get_device_info_by_index(1).get('defaultSampleRate')),
                    input=True,
                    frames_per_buffer=1024,
                    input_device_index=mic_device_index)

    for data in record_microphone(stream):
        udp_socket.sendto(data, addr)


asyncio.get_event_loop().run_until_complete(send_audio())