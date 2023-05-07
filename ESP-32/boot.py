import sys
import time
import ujson
import _thread
import network
import machine
import urequests

## Konfigurasi.
WIFI_SSID = 'neszha'
WIFI_PASSWORD = '12345678'
BASE_URL = 'http://192.168.137.1:8000'

## Inisialisasi variabel global.
threadRunCounter = 0
threadMainRunner = True
wlan = network.WLAN(network.STA_IF)
deviceStateAPI = ujson.loads('{}')
deviceState = ujson.loads('{}')
stateStorageName = 'state.json'

## Inisialisasi variabel pin INPUT.
pinBtnStop = machine.Pin(4, machine.Pin.IN)
pinLdrHome = machine.ADC(machine.Pin(33))
pinLdrHome.atten(machine.ADC.ATTN_11DB)  # Rentang tegangan 0-3.6V
pinLdrHome.width(machine.ADC.WIDTH_12BIT)  # Resolusi 12-bit (0-4095)
pinLdrGarden = machine.ADC(machine.Pin(32))
pinLdrGarden.atten(machine.ADC.ATTN_11DB)  # Rentang tegangan 0-3.6V
pinLdrGarden.width(machine.ADC.WIDTH_12BIT)  # Resolusi 12-bit (0-4095)

## Inisialisasi variabel pin OUTPUT.
pinHomeLight = machine.Pin(5, machine.Pin.OUT)
pinGardenLight = machine.Pin(18, machine.Pin.OUT)

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

## Inisialisasi kondisi awal.
def stateBegin():
    pinHomeLight.off()
    pinGardenLight.off()

## Membaca data device state dari file storage.
def readDeviceSteteFromStorage():
    global deviceState
    try:
        with open(stateStorageName, 'r') as file:
            jsonString = file.read()
            deviceState = ujson.loads(jsonString)
    except:
        print('INF: File state.json tidak ada!')

## Menyimpan data device state ke file storage.
def saveDeviceStateToStorage():
    global deviceState
    with open(stateStorageName, 'w') as file:
        jsonString = ujson.dumps(deviceState)
        file.write(jsonString)

## Mengambol data device state dari API server.
def getDeviceStateFromAPI():
    global deviceState, deviceStateAPI
    url = BASE_URL + '/api/device/state?from=esp-32'
    try:
        response = urequests.get(url)
        dataJson = response.json()
        deviceStateAPI = dataJson['data']
        saveDeviceStateToStorage()
        response.close()
    except:
        print('ERR: Mengambil device state!')

## Update data device state le API server.
def updateDeviceStateToAPI():
    url = BASE_URL + '/api/device/state?from=esp-32'
    headers = {'Content-Type': 'application/json'}
    jsonString = ujson.dumps(deviceState)
    try:
        print('API: Update device state...')
        urequests.put(url, data=jsonString, headers=headers)
    except:
        print('ERR: Update device state!')

## Thread: Connection Thread.
def threadConnection(threadName, threadNumber):
    global threadRunCounter, threadMainRunner, deviceState
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1
    connectToWifi()

    ## Menjalankan thread runtime.
    while threadMainRunner:
        ## Mengecek koneksi (reconect WiFi).
        if not wlan.isconnected():
            print('Koneksi WiFi terputus!')
            wlan.active(False)
            connectToWifi()
        else:
            ## Mengambil data state dari API.
            getDeviceStateFromAPI()

            ## Singkronisasi data state.
            if deviceStateAPI != deviceState:
                updateDeviceStateToAPI()
                deviceState = deviceStateAPI.copy()

        ## Thread limiter.
        time.sleep(1)
    
    threadRunCounter -= 1
    _thread.exit()

## Thread: Home Light
def threadHomeLight(threadName, threadNumber):
    global threadRunCounter, threadMainRunner
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1

    ## Menjalankan thread runtime.
    while threadMainRunner:
        # Membaca konfigurasi home light.
        homeLightState = deviceState.get('homeLight', {})
        sensitivity = homeLightState.get('sensitivity', 255)
        modeAuto = homeLightState.get('auto', True)
        
        # Membaca nilai LDR.
        ldrHomeAnalogValue = pinLdrHome.read()
        pinLdrHomeValue = map(ldrHomeAnalogValue, 0, 4095, 0, 255)
        print("LDR Home Light:", pinLdrHomeValue, '| Sensitivity:', sensitivity, '| Auto:', modeAuto)

        # Kontrol output sinyal
        if not modeAuto:
            pinHomeLight.on()
            deviceState.setdefault('homeLight', {})['isActive'] = True
        else:
            if pinLdrHomeValue < sensitivity:
                pinHomeLight.on()
                deviceState.setdefault('homeLight', {})['isActive'] = True
                time.sleep(1)
            else:
                pinHomeLight.off()
                deviceState.setdefault('homeLight', {})['isActive'] = False

        # Thread limiter.
        time.sleep(0.5)

    threadRunCounter -= 1
    _thread.exit()
    

## Thread: Garden Light
def threadGardenLight(threadName, threadNumber):
    global threadRunCounter, threadMainRunner
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1

    ## Menjalankan thread runtime.
    while threadMainRunner:
        # Membaca konfigurasi garden light.
        gardenLightState = deviceState.get('gardenLight', {})
        sensitivity = gardenLightState.get('sensitivity', 255)
        modeAuto = gardenLightState.get('auto', True)
        
        # Membaca nilai LDR.
        ldrHGardenAnalogValue = pinLdrGarden.read()
        pinLdrGardenValue = map(ldrHGardenAnalogValue, 0, 4095, 0, 255)
        print("LDR Garden Light:", pinLdrGardenValue, '| Sensitivity:', sensitivity, '| Auto:', modeAuto)

        # Kontrol output sinyal
        if not modeAuto:
            pinGardenLight.on()
            deviceState.setdefault('gardenLight', {})['isActive'] = True
        else:
            if pinLdrGardenValue < sensitivity:
                pinGardenLight.on()
                deviceState.setdefault('gardenLight', {})['isActive'] = True
                time.sleep(1)
            else:
                pinGardenLight.off()
                deviceState.setdefault('gardenLight', {})['isActive'] = False

        # Thread limiter.
        time.sleep(0.5)

    threadRunCounter -= 1
    _thread.exit()

## Thread: Montion Detector
def threadMontionDetector(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    _thread.exit()

## Thread: Automatic Gate
def threadAutomaticGate(threadName, threadNumber):
    print('Thread:', threadName, threadNumber)
    _thread.exit()

## Jalankan fungsi: setup().
stateBegin()
readDeviceSteteFromStorage()

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
stateBegin()
print('EXITING PROGRAM...')
while threadRunCounter > 0:
    print('Menghentikan threads:', threadRunCounter)
    time.sleep(0.05)
print('Menghentikan threads:', threadRunCounter)
sys.exit()