import time
import machine

pinPwmGateServo = machine.PWM(machine.Pin(23), freq=50)

## Kontrol gerbang.
def gateControl(command = 'close'):
    if command == 'open':
        targetPosition = 72
        print('GATE: Membuka gerbang!')
        pinPwmGateServo.duty(targetPosition)
    elif command == 'close':
        targetPosition = 120
        print('GATE: Menutup gerbang!')
        pinPwmGateServo.duty(targetPosition)

gateControl('open')
time.sleep(1)
gateControl('close')