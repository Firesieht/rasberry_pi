import RPi.GPIO as GPIO

LedPin = 17    # pin11 --- led
BtnPin = 27    # pin13 --- button

def setup():
	GPIO.setmode(GPIO.BCM)       # Numbers GPIOs by BCM
	GPIO.setup(LedPin, GPIO.OUT)   # Set LedPin's mode is output
	GPIO.setup(BtnPin, GPIO.IN, pull_up_down=GPIO.PUD_UP)    # Set BtnPin's mode is input, and pull up to high level(3.3V)
	GPIO.output(LedPin, GPIO.LOW) # Set LedPin low to off led

def loop():
	while True:
		if GPIO.input(BtnPin) == GPIO.LOW: # Check whether the button is pressed or not.
			print('led on')
			GPIO.output(LedPin, GPIO.HIGH)  # led on
		else:
			print('led off')
			GPIO.output(LedPin, GPIO.LOW) # led off

def destroy():
	GPIO.output(LedPin, GPIO.LOW)     # led off
	GPIO.cleanup()                     # Release resource

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt: destroy()