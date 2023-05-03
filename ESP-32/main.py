from machine import Pin, ADC
import time

# set up ADC pin
adc = ADC(Pin(4))

# read ADC value continuously
while True:
    # read analog value
    analog_value = adc.read()

    # print analog value
    print("Analog value:", analog_value)

    # wait for some time
    time.sleep_ms(500)
