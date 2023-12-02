from socket import *
import pyaudio
import asyncio
import wave
import time
import sys
#3001 - порт для микрофона
#3002 - порт для динамика '192.168.0.7' - хост мака у меня дома

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
        len_bytes = 0
        chunks = 0
        for i in range(0, len(bytes_)-8193, 8192):
            time.sleep(0.001)
            chunks += 1
            len_bytes += len(bytes_[i:i+8192])
            self.dynamic_socket.sendto(bytes_[i:i+8192], self.dynamic_addr_to_send)

        self.dynamic_socket.sendto(b'end', self.dynamic_addr_to_send)
        print('len_bytes_sended',len_bytes)
        print('chunks_sended', chunks)


    

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
        file.setframerate(self.RATE)
        file.setsampwidth(2)

        for byte in bytes:
            file.writeframes(byte)
        
        return file

    def WAW_to_bytes(self, path): #должен быть файл с расширением .waw
        audio_file = wave.open(path)
        FORMAT = audio_file.getsampwidth() # глубина звука
        CHANNELS = audio_file.getnchannels() # количество каналов
        RATE = audio_file.getframerate() 
        print('SETTINGS FILE', FORMAT, CHANNELS, RATE)
        N_FRAMES = audio_file.getnframes() 
        return audio_file.readframes(N_FRAMES)



from threading import Thread, Lock

controller = AudioServerController('192.168.0.19', 3001, 3002)
def play():
    while True:
        print('play')
        audio = controller.WAW_to_bytes('res.wav')
        controller.play_audio(audio)
        time.sleep(30)


bytes_f = b''

def f(x): pass
    # global bytes_f
    # bytes_f += x
    # if len(bytes_f) > 1000000:
    #     controller.bytes_to_WAV(bytes_f, 'out.wav')
    #     sys.exit()



def main():
    t1 = Thread(target=play,)
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
