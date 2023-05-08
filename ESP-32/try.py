import time
import machine

pinPwmServo = machine.PWM(machine.Pin(23), freq=50)

## Kontrol gerbang.
def geteControl(command = 'close'):
    smoot = 1
    currentPosition = pinPwmServo.duty()
    if currentPosition > 120:
        currentPosition = 90
        pinPwmServo.duty(currentPosition)
    if command == 'close':
        targetPosition = 120
        while currentPosition < targetPosition:
            pinPwmServo.duty(currentPosition + smoot)
            currentPosition = pinPwmServo.duty()
            time.sleep(0.05)
        pinPwmServo.duty(targetPosition)
    elif command == 'open':
        targetPosition = 70
        while currentPosition > targetPosition:
            pinPwmServo.duty(currentPosition - smoot)
            currentPosition = pinPwmServo.duty()
            time.sleep(0.05)
        pinPwmServo.duty(targetPosition)

print('RUNN')
geteControl('open')
time.sleep(1)
geteControl('close')