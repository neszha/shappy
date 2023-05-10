import time
import machine

pinUltrasonicEcho = machine.Pin(12, machine.Pin.IN)
pinUltrasonicTrig = machine.Pin(14, machine.Pin.OUT)

def measureDistance():
    # Mengirimkan pluse ultrasonik.
    pinUltrasonicTrig.off()
    time.sleep_us(2)
    pinUltrasonicTrig.on()
    time.sleep_us(10)
    pinUltrasonicTrig.off()

    # Membaca waktu yang dibutuhkan untuk ultrasonik kembali.
    while pinUltrasonicEcho.value() == 0:
        pulseStart = time.ticks_us()
    while pinUltrasonicEcho.value() == 1:
        pulseEnd = time.ticks_us()
    pulseDuration = pulseEnd - pulseStart

    # Menghitung jarak berdasarkan waktu yang dibutuhkan.
    distance = (pulseDuration * 0.0343) / 2
    return distance

while True:
    distance = measureDistance()
    print(distance)
    time.sleep(0.5)