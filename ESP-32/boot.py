import sys
import time
import _thread
import network
import machine

## Konfigurasi.
WIFI_SSID = 'neszha'
WIFI_PASSWORD = '12345678'

## Inisialisasi variabel global.
threadRunCounter = 0
threadMainRunner = True
wlan = network.WLAN(network.STA_IF)

## Inisialisasi variabel pin.
pinBtnStop = machine.Pin(4, machine.Pin.IN)
pinLdrHome = machine.ADC(machine.Pin(35))
pinLdrHome.atten(machine.ADC.ATTN_11DB)  # Rentang tegangan 0-3.6V
pinLdrHome.width(machine.ADC.WIDTH_12BIT)  # Resolusi 12-bit (0-4095)

## Mengkoneksikan ke wifi.
def connectToWifi():
    global threadMainRunner
    print('Mengkoneksikan ke WiFi...')
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while not wlan.isconnected() and threadMainRunner:
        time.sleep(1)
    if threadMainRunner:
        print('Terkoneksi ke WiFi!')

## Fungsi maping nilai.
def map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

## Thread: Connection Thread.
def threadConnection(threadName, threadNumber):
    global threadRunCounter, threadMainRunner
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1
    connectToWifi()

    ## Mengecek koneksi (reconect WiFi).
    while threadMainRunner:
        print("threadConnection", threadMainRunner)
        if not wlan.isconnected():
            print('Koneksi WiFi terputus!')
            wlan.active(False)
            connectToWifi()
        time.sleep(1)
    
    threadRunCounter -= 1
    _thread.exit()

## Thread: Home Light
def threadHomeLight(threadName, threadNumber):
    global threadRunCounter, threadMainRunner
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1

    while threadMainRunner:
        print("threadHomeLight", threadMainRunner)
        # Membaca konfigurasi home light.
        auto = True

        # Membaca nilai LDR.
        pinLdrHomeValue = map(pinLdrHome.read(), 0, 4095, 0, 255)
        print(pinLdrHome.read(), pinLdrHomeValue)

        # Thread limiter.
        time.sleep(0.5)

    threadRunCounter -= 1
    _thread.exit()
    

## Thread: Garden Light
def threadGardenLight(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    _thread.exit()

## Thread: Montion Detector
def threadMontionDetector(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    _thread.exit()

## Thread: Automatic Gate
def threadAutomaticGate(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    _thread.exit()

## Inisialisasi threads program.
try:
    _thread.start_new_thread(threadConnection, ('Connection Thread', 1))
    _thread.start_new_thread(threadHomeLight, ('Home Light', 2))
    _thread.start_new_thread(threadGardenLight, ('Garden Light', 3))
    _thread.start_new_thread(threadMontionDetector, ('Montion Detector', 4))
    _thread.start_new_thread(threadAutomaticGate, ('Automatic Gate', 5))
except:
    print('Gagal membuat threads.')

while threadMainRunner:
    # Membaca nilai tombol stop program.
    pinBtnStopValue = pinBtnStop.value()
    if pinBtnStopValue == 1:
        threadMainRunner = False

    # Limiter.
    time.sleep(0.1)

## Menghentikan semua thread.
threadMainRunner = False
print('EXITING PROGRAM...')
while threadRunCounter > 0:
    print('Menghentikan threads:', threadRunCounter)
    time.sleep(0.05)
print('Menghentikan threads:', threadRunCounter)
sys.exit()
