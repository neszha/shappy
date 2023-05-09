import sys
import time
import ujson
import _thread
import network
import machine
import urequests

## Konfigurasi.
WIFI_SSID = '.'
WIFI_PASSWORD = 'pppppppppp'
BASE_URL = 'http://103.13.206.251:80'

## Inisialisasi variabel global.
threadRunCounter = 0
threadMainRunner = True
wlan = network.WLAN(network.STA_IF)
deviceStateAPI = ujson.loads('{}')
deviceState = ujson.loads('{}')
stateStorageName = 'state.json'

## Inisialisasi variabel pin INPUT.
SERVO_PIN = 23
pinBtnStop = machine.Pin(15, machine.Pin.IN)
pinLdrHome = machine.ADC(machine.Pin(33))
pinLdrHome.atten(machine.ADC.ATTN_11DB)  # Rentang tegangan 0-3.6V
pinLdrHome.width(machine.ADC.WIDTH_12BIT)  # Resolusi 12-bit (0-4095)
pinLdrGarden = machine.ADC(machine.Pin(32))
pinLdrGarden.atten(machine.ADC.ATTN_11DB)  # Rentang tegangan 0-3.6V
pinLdrGarden.width(machine.ADC.WIDTH_12BIT)  # Resolusi 12-bit (0-4095)
pinPir = machine.Pin(13, machine.Pin.IN)
pinUltrasonicEcho = machine.Pin(12, machine.Pin.IN)

## Inisialisasi variabel pin OUTPUT.
pinConnectionIndicatorRed = machine.Pin(4, machine.Pin.OUT)
pinConnectionIndicatorGreen = machine.Pin(17, machine.Pin.OUT)
pinHomeLight = machine.Pin(5, machine.Pin.OUT)
pinGardenLight = machine.Pin(18, machine.Pin.OUT)
pinBuzzer = machine.Pin(27, machine.Pin.OUT)
pinPwmGateServo = machine.PWM(machine.Pin(SERVO_PIN), freq=50)
pinUltrasonicTrig = machine.Pin(14, machine.Pin.OUT)

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
        print('IP Address:', wlan.ifconfig()[0])

## Fungsi maping nilai.
def map(value, in_min, in_max, out_min, out_max):
    return (value - in_min) * (out_max - out_min) // (in_max - in_min) + out_min

## Inisialisasi kondisi awal.
def stateBegin():
    pinHomeLight.off()
    pinGardenLight.off()
    pinConnectionIndicatorRed.off()
    pinConnectionIndicatorGreen.off()
    pinBuzzer.off()
    gateControl('close')

## Membaca data device state dari file storage.
def readDeviceSteteFromStorage():
    global deviceState
    try:
        with open(stateStorageName, 'r') as file:
            jsonString = file.read()
            deviceState = ujson.loads(jsonString)
    except:
        print('INFO: File state.json tidak ada!')

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
        print('REQUEST ERROR: Mengambil device state!')

## Menyimpan aktifitas perangkat.
def postDeviceActivity(key, value):
    if not wlan.isconnected():
        return
    url = BASE_URL + '/api/device/activity?from=esp-32'
    headers = {'Content-Type': 'application/json'}
    body = {}
    body['key'] = key
    body['value'] = value
    jsonString = ujson.dumps(body)
    try:
        print('API: Post device activity...')
        urequests.post(url, data=jsonString, headers=headers)
    except:
        print('REQUEST ERROR: Post device activity!')

## Update data device state le API server.
def updateDeviceStateToAPI():
    url = BASE_URL + '/api/device/state?from=esp-32'
    headers = {'Content-Type': 'application/json'}
    jsonString = ujson.dumps(deviceState)
    try:
        print('API: Update device state...')
        urequests.put(url, data=jsonString, headers=headers)
    except:
        print('REQUEST ERROR: Update device state!')

## Kontrol buka tutup gerbang.
def gateControl(command = 'close'):
    if command == 'open':
        targetPosition = 72
        print('GATE: Membuka gerbang!')
        pinPwmGateServo.duty(targetPosition)
    elif command == 'close':
        targetPosition = 120
        print('GATE: Menutup gerbang!')
        pinPwmGateServo.duty(targetPosition)

## Memnaca data jarak dengan sensor ultrasonik (cm).
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

## Thread: Connection Thread.
def threadConnection(threadName, threadNumber):
    global threadRunCounter, threadMainRunner, deviceState, pinConnectionIndicatorGreen
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1
    pinConnectionIndicatorRed.on()
    connectToWifi()

    ## Menjalankan thread runtime.
    while threadMainRunner:
        ## Mengecek koneksi (reconect WiFi).
        if not wlan.isconnected():
            pinConnectionIndicatorRed.on()
            pinConnectionIndicatorGreen.off()
            print('Koneksi WiFi terputus!')
            wlan.active(False)
            connectToWifi()
        else:
            pinConnectionIndicatorRed.off()
            pinConnectionIndicatorGreen.on()

            ## Mengambil data state dari API.
            getDeviceStateFromAPI()

            ## Singkronisasi data state.
            if deviceStateAPI != deviceState:
                updateDeviceStateToAPI()
                getDeviceStateFromAPI()
                deviceState = deviceStateAPI.copy()

        ## Thread limiter.
        time.sleep(1)
    
    threadRunCounter -= 1
    _thread.exit()

## Thread: Home Light
def threadHomeLight(threadName, threadNumber):
    global threadRunCounter, threadMainRunner, deviceState
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1

    ## Menjalankan thread runtime.
    while threadMainRunner:
        # Membaca konfigurasi home light.
        homeLightState = deviceState.get('homeLight', {})
        sensitivity = homeLightState.get('sensitivity', 255)
        modeAuto = homeLightState.get('auto', True)
        isActive = homeLightState.get('isActive', True)
        
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
                if not isActive:
                    postDeviceActivity('homeLight', 'Lampu rumah menyala!')
                pinHomeLight.on()
                deviceState.setdefault('homeLight', {})['isActive'] = True
                time.sleep(1)
            else:
                if isActive:
                    postDeviceActivity('homeLight', 'Lampu rumah mati!')
                pinHomeLight.off()
                deviceState.setdefault('homeLight', {})['isActive'] = False

        # Thread limiter.
        time.sleep(0.5)

    # Proses thread selesai.
    threadRunCounter -= 1
    _thread.exit()
    
## Thread: Garden Light
def threadGardenLight(threadName, threadNumber):
    global threadRunCounter, threadMainRunner, deviceState
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1

    ## Menjalankan thread runtime.
    while threadMainRunner:
        # Membaca konfigurasi garden light.
        gardenLightState = deviceState.get('gardenLight', {})
        sensitivity = gardenLightState.get('sensitivity', 255)
        modeAuto = gardenLightState.get('auto', True)
        isActive = gardenLightState.get('isActive', True)
        
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
                if not isActive:
                    postDeviceActivity('gardenLight', 'Lampu taman menyala!')
                pinGardenLight.on()
                deviceState.setdefault('gardenLight', {})['isActive'] = True
                time.sleep(1)
            else:
                if isActive:
                    postDeviceActivity('gardenLight', 'Lampu taman mati!')
                pinGardenLight.off()
                deviceState.setdefault('gardenLight', {})['isActive'] = False

        # Thread limiter.
        time.sleep(0.5)

    # Proses thread selesai.
    threadRunCounter -= 1
    _thread.exit()

## Thread: Montion Detector
def threadMontionDetector(threadName, threadNumber):
    global threadRunCounter, threadMainRunner, deviceState
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1

    # Menjalankan thread runtime.
    while threadMainRunner:
        # Membaca konfigurasi garden light.
        montionDetectorState = deviceState.get('montionDetector', {})
        modeAuto = montionDetectorState.get('auto', False)
        isAlertActive =montionDetectorState.get('isActive', False)

        # Membaca nilai sensor PIR.
        pinPirDigitalValue = pinPir.value()
        # print("PIR:", pinPirDigitalValue, '| Auto:', modeAuto)

        # Kontrol output sinyal
        if not modeAuto: # Fitur tidak aktif
            pinBuzzer.off()
            deviceState.setdefault('montionDetector', {})['isActive'] = False
        else: # Fitur aktif
            if pinPirDigitalValue == 1:
                pinBuzzer.on()
                deviceState.setdefault('montionDetector', {})['isActive'] = True
                updateDeviceStateToAPI()
                postDeviceActivity('montionDetector', 'Terdeteksi gerakan!')
                time.sleep(2)
                pinBuzzer.off()
                time.sleep(5)
            else:
                pinBuzzer.off()
                deviceState.setdefault('montionDetector', {})['isActive'] = False

        # Thread limiter.
        time.sleep(0.5)

    # Proses thread selesai.
    threadRunCounter -= 1
    _thread.exit()

## Thread: Automatic Gate
def threadAutomaticGate(threadName, threadNumber):
    global threadRunCounter, threadMainRunner, deviceState, pinPwmGateServo
    print('Thread:', threadName, threadNumber)
    threadRunCounter += 1

    # Menjalankan thread runtime.
    while threadMainRunner:
        # Membaca konfigurasi garden light.
        automaticGateState = deviceState.get('automaticGate', {})
        modeAuto = automaticGateState.get('auto', False)
        isGateOpened = automaticGateState.get('isActive', False)

        # Membaca nilai sensor ultrasonik.
        ultrasonikDistanceValue = measureDistance()
        print("Ultrasonik:", ultrasonikDistanceValue, '| Opened:', isGateOpened, '| Auto:', modeAuto)

        # Kontrol output sinyal.
        if not modeAuto: # Fitur tidak aktif
            pinPwmGateServo.deinit()
        else: # Fitur aktif
            pinPwmGateServo = machine.PWM(machine.Pin(SERVO_PIN), freq=50)
            
            # Deteksi objek.
            minDistance = 10
            if ultrasonikDistanceValue <= 10:
                # Menunggu konfirmasi ulang.
                time.sleep(1.5)
                ultrasonikDistanceValue = measureDistance()
                if ultrasonikDistanceValue > 10:
                    continue
                
                # Membuka gerbang.
                gateControl('open')
                if not isGateOpened:
                    deviceState.setdefault('automaticGate', {})['isActive'] = True
                    postDeviceActivity('automaticGate', 'Gerbang terbuka!')
                    time.sleep(5)
            else:
                # Menunggu konfirmasi ulang.
                time.sleep(5)
                ultrasonikDistanceValue = measureDistance()
                if ultrasonikDistanceValue <= 10:
                    continue

                # Menutup gerbang.
                gateControl('close')
                if isGateOpened:
                    deviceState.setdefault('automaticGate', {})['isActive'] = False
                    postDeviceActivity('automaticGate', 'Gerbang tertutup!')

        # Thread limiter.
        time.sleep(0.5)

    # Proses thread selesai.
    threadRunCounter -= 1
    _thread.exit()

## Jalankan fungsi: setup().
stateBegin()
readDeviceSteteFromStorage()

## Inisialisasi threads program.
print('Mambuat threads....')
time.sleep(1.5)
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
