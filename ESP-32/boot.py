import sys
import time
import config
import _thread
import network
import machine

## Inisialisasi pin.
btnStop = machine.Pin(4, machine.Pin.IN)

## Inisialisasi koneksi WiFi.
wlan = network.WLAN(network.STA_IF)

## Mengkoneksikan ke wifi.
def connectToWifi():
    print('Mengkoneksikan ke WiFi...')
    wlan.active(True)
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print('Terkoneksi ke WiFi!')

## Thread: Connection Thread.
def connectionThread(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    connectToWifi()

    ## Mengecek koneksi (reconect WiFi).
    while True:
        if not wlan.isconnected():
            print('Koneksi WiFi terputus!')
            wlan.active(False)
            connectToWifi()
    time.sleep(1)

## Membuat threads.
try:
    _thread.start_new_thread(connectionThread, ('Connection Thread', 1))
except:
    print('Gagal membuat threads pada boot.')

while True:
    # Membaca nilai tombol stop sistem.
    btnStopValue = btnStop.value()
    if btnStopValue == 1:
        sys.exit() 

    # Limiter.
    time.sleep(0.5)

