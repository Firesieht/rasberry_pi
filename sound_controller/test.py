import pyaudio

audio = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16  # глубина звука = 16 бит = 2 байта
CHANNELS = 1  # моно
RATE = 44100
print(RATE)
# частота дискретизации - кол-во фреймов в секунду
CHUNK = 1024  # кол-во фреймов за один "запрос" к микрофону - тк читаем по кусочкам


in_stream = audio.open(format=FORMAT, channels=CHANNELS,
                       rate=RATE, input=True,
                       frames_per_buffer=CHUNK)

out_stream = audio.open(format=FORMAT, channels=CHANNELS,
                       rate=RATE, output=True,
                       frames_per_buffer=CHUNK)



while True:
    data = in_stream.read(CHUNK, exception_on_overflow=False)
    out_stream.write(data)
    print(data)


in_stream.stop_stream()
in_stream.close()
audio.terminate()