from socket import *
import pyaudio
audio = pyaudio.PyAudio()


FORMAT = pyaudio.paInt16  # глубина звука = 16 бит = 2 байта
CHANNELS = 1  # моно
RATE = int(audio.get_device_info_by_index(1).get('defaultSampleRate'))  # частота дискретизации - кол-во фреймов в секунду
CHUNK = 1024  # кол-во фреймов за один "запрос" к микрофону - тк читаем по кусочкам

host = '192.168.0.7'
port = 5437
addr = (host,port)

udp_socket = socket(AF_INET, SOCK_DGRAM)
udp_socket.bind(addr)
out_stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, output=True)


while True:
    data, addr  = udp_socket.recvfrom(2048)
    out_stream.write(data)


