from socket import *
import pyaudio
import asyncio
import wave
import time

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

        self.task_group = asyncio.TaskGroup()

    def set_stream_settings(self, FORMAT=pyaudio.paInt16, CHANNELS=1, RATE=44100, CHUNK=512):
        self.RATE = RATE
        self.CHANNELS = CHANNELS
        self.CHUNK = CHUNK
        self.FORMAT = FORMAT

    def play_audio(self, bytes_:bytes):
        print('len_bytes:', len(bytes_))

        def grouper(iterable, n):
            args = [iter(iterable)] * n
            return zip(*args)

        list_data = [bytes(''.join(i), encoding='utf-8') for i in grouper(str(bytes_), 1024)]
        for data in list_data:
            self.dynamic_socket.sendto(data, self.dynamic_addr_to_send)
        
        self.dynamic_socket.sendto(b'end', self.dynamic_addr_to_send)

    

    def start_microfone_stream(self, on_get_batch):
        out_stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                        rate=self.RATE, output=True)

        print('start stream')
        while True:
            data, _ = self.udp_socket.recvfrom(1024)
            on_get_batch(data)
            out_stream.write(data)
    

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

    def WAW_to_bytes(self, path): #должен быть файл с расширением .waw
        audio_file = wave.open(path)
        FORMAT = audio_file.getsampwidth() # глубина звука
        CHANNELS = audio_file.getnchannels() # количество каналов
        RATE = audio_file.getframerate() 
        print(FORMAT, CHANNELS, RATE)
        N_FRAMES = audio_file.getnframes() 
        return audio_file.readframes(N_FRAMES)



from threading import Thread, Lock

controller = AudioServerController('192.168.0.7', 3001, 3002)
def play():
    while True:
        print('play')
        audio = controller.WAW_to_bytes('example.wav')
        controller.play_audio(audio)
        time.sleep(30)


def f(x): pass


def main():
    t1 = Thread(target=play, )
    t2 = Thread(target=controller.start_microfone_stream, args=(f,))

    t1.start()
    t2.start()
    t1.join()
    t2.join()

if __name__ == '__main__':
    main()








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
