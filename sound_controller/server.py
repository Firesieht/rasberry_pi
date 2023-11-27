from socket import *
import pyaudio
import asyncio
import wave


#5437 - порт для микрофона
#5438 - порт для динамика '192.168.0.7' - хост мака у меня дома

class AudioServerController:
    def __init__(self, host, port_mic, port_dynamic) -> None:
        self.audio = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16 
        self.CHANNELS = 1  
        self.RATE = 44100 
        self.CHUNK = 512
        self.host = host
        self.port_micro = 5437
        self.addr_micro = (host,port_mic)
        self.addr_dynamic = (host,port_dynamic)

        self.udp_socket = socket(AF_INET, SOCK_DGRAM)
        self.udp_socket.bind(self.addr_micro)

        self.dynamic_socket = socket(AF_INET, SOCK_DGRAM)
        self.dynamic_socket.bind(self.addr_dynamic)

        _, self.dynamic_addr_to_send = self.dynamic_socket.recvfrom(1024)

    def set_stream_settings(self, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=44100, CHUNK=512):
        self.RATE = RATE
        self.CHANNELS = CHANNELS
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT

    def play_audio(self, bytes:bytes):
        self.dynamic_socket.sendto(bytes, self.dynamic_addr_to_send)
    

    def start_microfone_stream(self, on_get_batch):
        out_stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                        rate=self.RATE, output=True)

        async def get_mic_stream():
            while True:
                data, _ = self.udp_socket.recvfrom(1024)
                on_get_batch(data)
                out_stream.write(data)
        asyncio.get_event_loop().run_until_complete(get_mic_stream())

    def bytes_to_WAV(self, bytes, name):#список байтиков на вход + имя заканчивающиеся на wav
        if type(bytes) != list:
            bytes = [bytes]
        

        file = wave.open(name, "wb")
        file.setnchannels(self.CHANNELS)
        file.setframerate(self.FRAMERATE)
        file.setsampwidth(self.FORMAT)

        for byte in bytes:
            file.writeframes(byte)
        
        return file





controller = AudioServerController('192.168.0.7', 5437, 5438)
controller.start_microfone_stream(on_get_batch=lambda x: print(len(x)))




# audio = pyaudio.PyAudio()
# FORMAT = pyaudio.paInt16  # глубина звука = 16 бит = 2 байта
# CHANNELS = 1  # моно
# RATE = 44100  # частота дискретизации - кол-во фреймов в секунду
# CHUNK = 512  # кол-во фреймов за один "запрос" к микрофону - тк читаем по кусочкам

# host = '192.168.0.7'
# port = 5437
# addr = (host,port)

# udp_socket = socket(AF_INET, SOCK_DGRAM)
# udp_socket.bind(addr)

# dynamic_socket = socket(AF_INET, SOCK_DGRAM)
# dynamic_socket.bind(('192.168.0.7', 5438))

# dynamic_data, dynamic_addr = dynamic_socket.recvfrom(1024)



# out_stream = audio.open(format=FORMAT, channels=CHANNELS,
#                         rate=RATE, output=True)



# async def get_mic_stream():
#     while 1:
#         data, _ = udp_socket.recvfrom(1024)
#         out_stream.write(data)

# def play_audio(bytes:bytes):
#     dynamic_socket.sendto(bytes, dynamic_addr)

# audio_file = wave.open("example.wav")

# play_audio(audio_file.readframes(16000))
# asyncio.get_event_loop().run_until_complete(get_mic_stream())
