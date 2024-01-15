import spidev


spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 4000000
NUM_BYTES = 128

while True:
    b  =  spi.readbytes(NUM_BYTES)
    print(b)
