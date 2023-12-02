import RPi.GPIO as GPIO

LedPin = 17    # pin11 - светоидиот
BtnPin = 27    # pin13 -  кнопка

def setup():
	GPIO.setmode(GPIO.BCM)      
	GPIO.setup(LedPin, GPIO.OUT)   
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    
	GPIO.output(LedPin, GPIO.LOW) 

def loop():
	while True:
		if GPIO.input(BtnPin) == GPIO.LOW: 
			GPIO.output(LedPin, GPIO.HIGH)
		else:
			GPIO.output(LedPin, GPIO.LOW) 

def destroy():
	GPIO.output(LedPin, GPIO.LOW)     
	GPIO.cleanup()              

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt: destroy()