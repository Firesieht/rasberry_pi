import pyaudio
import asyncio
from socket import *
import sys
import wave
from time import sleep
from threading import Thread, Lock
import requests
from enum import Enum
import json
import uuid

class Statuses(Enum):
    STREAM_CONTEXT = 'stream'
    DYNAMIC_PLAY = 'dynamic_play'
    COMMAND = 'command'


class AudioController:
    def __init__(self, backend_url, LedPin = 17, BtnPin = 27) -> None:
        self.backend_url = backend_url
        self.audio = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16 
        self.CHANNELS = 1  
        self.CHUNK = 512
        self.RATE = int(self.audio.get_device_info_by_index(0).get('defaultSampleRate'))
        self.mic_device_index = None
        self.status = Statuses.STREAM_CONTEXT
        self.last_command_id = -1
        self.LedPin = LedPin   # pin11 - светоидиот
        self.BtnPin = BtnPin   # pin13 -  кнопка
        self.answers = []
        self.files_played = 0
        self.files_downloaded = 0

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
        stream = self.audio.open(format=self.FORMAT,
                channels=1,
                rate=self.RATE,
                input=True,
                frames_per_buffer=self.CHUNK,
                input_device_index=0,
        )

        b = b''
        command = b''
        for data in self.record_microphone(stream):
            if self.status == Statuses.STREAM_CONTEXT:
                if command != b'':
                    file = wave.open('command.wav', 'wb')
                    file.setnchannels(1)
                    file.setsampwidth(2)
                    file.setframerate(self.RATE)
                    file.writeframes(command)
                    file.close()

                    url = self.backend_url + '/command'
                    files=[
                    ('audio',('сommand.wav',open('command.wav','rb'),'audio/wav'))
                    ]
                    payload = {'type': 'command'}

                    r = requests.post(url, data=payload, files=files)
                    print(r.text)
                    self.last_command_id = int(json.loads(r.text)['id'])
                    command = b''
                    
                b += data

                if len(b) >= self.RATE*self.FORMAT/4*60:
                    print(len(b))
                    file = wave.open('micro.wav', 'wb')
                    file.setnchannels(1)
                    file.setsampwidth(2)
                    file.setframerate(self.RATE)
                    file.writeframes(b)
                    file.close()

                    
                    url = self.backend_url + '/command'
                    files=[
                    ('audio',('micro.wav',open('micro.wav','rb'),'audio/wav'))
                    ]
                    payload = {'type': 'transcription'}

                    # r = requests.post(url, files={'audio': (None, 'param 1 value'), 'param_2': (None, 'param 2 value')})
                    r = requests.post(url, data=payload, files=files)
                    print(r.text)
                    b = b''

            elif self.status == Statuses.COMMAND:
                print('COMMAND DATA')
                command += data
                if b != b'': 
                    b = b''
            else:
                if b == b'': 
                    continue
                else: 
                    b = b''


    def start_command_stream(self):
        import RPi.GPIO as GPIO

        GPIO.setmode(GPIO.BCM)      
        GPIO.setup(self.LedPin, GPIO.OUT)   
        GPIO.setup(self.BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    
        GPIO.output(self.LedPin, GPIO.LOW) 


        while True:
            if self.status == Statuses.DYNAMIC_PLAY:
                 GPIO.output(self.LedPin, GPIO.HIGH)
            if GPIO.input(self.BtnPin) == GPIO.LOW: 
                GPIO.output(self.LedPin, GPIO.HIGH)
                if self.status != Statuses.COMMAND: 
                    self.status = Statuses.COMMAND

                
            else:
                if self.status == Statuses.COMMAND:
                    self.status = Statuses.STREAM_CONTEXT
                GPIO.output(self.LedPin, GPIO.LOW)
        


    def download_audio(self, url):
        id = uuid.uuid4()
        print('start_download', f'answer_{id}.wav', url)
        
        with open(f'answer_{id}.wav', 'wb') as a:
            resp = requests.get(url)
            if resp.status_code == 200:
                a.write(resp.content)
                print('downloaded', f'answer_{id}.wav', url)
                self.answers.append(f'answer_{id}.wav')
                a.close()
                sleep(0.5)
                return
            else:
                print(resp.reason)
                exit(1)
                
    def start_listen_answers(self):
        while True:
            if self.last_command_id != -1:
                if self.status != Statuses.DYNAMIC_PLAY:
                    self.status = Statuses.DYNAMIC_PLAY
                url = self.backend_url + '/command/'+  str(self.last_command_id)
                data = requests.get(url)
                response = json.loads(data.text)

                if len(response['answer_files']) > self.files_downloaded:
                    threads = []
                    print(self.files_downloaded, response['answer_files'][self.files_downloaded:])
                    for file in response['answer_files'][self.files_downloaded:]:
                        self.files_downloaded += 1
                        thread = Thread(target=self.download_audio, args=[file,])
                        threads.append(thread)
                        thread.start()

                    for thread in threads:
                        thread.join()

                if self.files_played == len(response['answer_files']) and response['end_process']:
                    print('END PROCESSS')
                    self.status = Statuses.STREAM_CONTEXT
                    self.last_command_id = -1
                    self.files_played = 0
                    self.answers = []
                    self.files_downloaded = 0

                sleep(1)
            else:
                sleep(0.5)

    def start_dynamic_stream(self):

        

        while True:
            if len(self.answers) > 0:
                print('ANSWERS:', self.answers)
                file = wave.open(self.answers[0], "rb")
                data = file.readframes(32768)
                out_stream =  self.audio.open(
                    format = self.audio.get_format_from_width(file.getsampwidth()),
                    channels = file.getnchannels(),
                    rate = file.getframerate(),
                    output = True
                )
                while data != b'':
                    # print(data[:15])
                    out_stream.write(data)
                    data = file.readframes(32768)
                
                self.files_played += 1
                out_stream.stop_stream()
                out_stream.close()
                self.answers.pop(0)
              
            else: 
                sleep(0.1)



            


# GPIO.output(LedPin, GPIO.LOW)     
# 	GPIO.cleanup()   

controller = AudioController('https://ccc9-49-12-205-40.ngrok-free.app/api')
# controller.get_devices()


from threading import Thread, Lock


t1 = Thread(target=controller.start_send_audio)
t2 = Thread(target=controller.start_dynamic_stream)
t3 = Thread(target=controller.start_command_stream)
t4 = Thread(target=controller.start_listen_answers)
t1.start()
t2.start()
t3.start()
t4.start()
t1.join()
t2.join()
t3.join()
t4.join()
