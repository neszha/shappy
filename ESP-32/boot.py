import sys
import time
import _thread
import network
import machine

## Konfigurasi.
WIFI_SSID = 'neszha'
WIFI_PASSWORD = '12345678'

## Inisialisasi variabel global.
wlan = network.WLAN(network.STA_IF)

## Inisialisasi variabel pin.
pinBtnStop = machine.Pin(4, machine.Pin.IN)
pinLdrHome = machine.ADC(machine.Pin(35))

## Mengkoneksikan ke wifi.
def connectToWifi():
    print('Mengkoneksikan ke WiFi...')
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected():
        time.sleep(1)
    print('Terkoneksi ke WiFi!')

## Fungsi maping nilai.
def map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

## Thread: Connection Thread.
threadConnectionRunner = True
def threadConnection(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    connectToWifi()

    ## Mengecek koneksi (reconect WiFi).
    while threadConnectionRunner:
        if not wlan.isconnected():
            print('Koneksi WiFi terputus!')
            wlan.active(False)
            connectToWifi()
    time.sleep(1)

## Thread: Home Light
threadHomeLightRunner = True
def threadHomeLight(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    while threadHomeLightRunner:
        # Membaca konfigurasi home light.
        auto = True

        # Membaca nilai LDR.
        pinLdrHomeValue = map(pinLdrHome.read(), 0, 4095, 0, 255)
        print(pinLdrHomeValue)

        # Thread limiter.
        time.sleep(0.5)
    

## Thread: Garden Light
threadGardenLightRunner = True
def threadGardenLight(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)

## Thread: Montion Detector
threadMontionDetectorRunner = True
def threadMontionDetector(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)

## Thread: Automatic Gate
threadAutomaticGateRunner = True
def threadAutomaticGate(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)

## Inisialisasi threads program.
try:
    _thread.start_new_thread(threadConnection, ('Connection Thread', 1))
    _thread.start_new_thread(threadHomeLight, ('Home Light', 2))
    _thread.start_new_thread(threadGardenLight, ('Garden Light', 3))
    _thread.start_new_thread(threadMontionDetector, ('Montion Detector', 4))
    _thread.start_new_thread(threadAutomaticGate, ('Automatic Gate', 5))
except:
    print('Gagal membuat threads.')

threadMainRunner = True
while threadMainRunner:
    # Membaca nilai tombol stop program.
    pinBtnStopValue = pinBtnStop.value()
    if pinBtnStopValue == 1:
        threadMainRunner = False

    # Limiter.
    time.sleep(0.1)

## Menghentikan semua thread.
print("EXITING PROGRAM...")
threadConnectionRunner = False
threadHomeLightRunner = False
threadGardenLightRunner = False
threadMontionDetectorRunner = False
threadAutomaticGateRunner = False
time.sleep(2)
sys.exit(0)