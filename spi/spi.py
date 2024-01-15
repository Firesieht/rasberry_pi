import spidev
from datetime import datetime
from time import sleep

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 4000000
NUM_BYTES = 128

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")

my_file = open(f"{dt_string}.txt", "w+")
my_file.write("data")
my_file.close()

while True:
    b  =  spi.readbytes(NUM_BYTES)
    my_file = open(f"{dt_string}.txt", "a+")
    my_file.write(b)
    my_file.close()
    sleep(1)
