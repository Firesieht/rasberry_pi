import pyaudio

FORMAT = pyaudio.paInt16  # глубина звука = 16 бит = 2 байта
CHANNELS = 1  # моно
RATE = 48000  # частота дискретизации - кол-во фреймов в секунду
CHUNK = 1024  # кол-во фреймов за один "запрос" к микрофону - тк читаем по кусочкам

audio = pyaudio.PyAudio()

in_stream = audio.open(format=FORMAT, channels=CHANNELS,
                       rate=RATE, input=True,
                       frames_per_buffer=CHUNK)

while True:
    print(in_stream.read(CHUNK))

in_stream.stop_stream()
in_stream.close()
audio.terminate()