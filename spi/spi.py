import spidev
from datetime import datetime
from time import sleep

spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 4000000
NUM_BYTES = 128

now = datetime.now()
dt_string = now.strftime("%d.%m.%Y_%H-%M-%S")

my_file = open(f"{dt_string}.txt", "w+")
my_file.write("data\n" )
my_file.close()

while True:
    b  =  spi.readbytes(NUM_BYTES)
    my_file = open(f"{dt_string}.txt", "a+")
    print(type(b), b, type(b[0]), b[0])
    my_file.write(' ,'.join(map(str, b)) + '\n')
    my_file.close()
    sleep(1)
