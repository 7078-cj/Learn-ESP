from machine import Pin, ADC, PWM
import utime

xAxis = ADC(Pin(1))
yAxis = ADC(Pin(2))
button = Pin(42, Pin.IN, Pin.PULL_UP)
led = PWM(Pin(40))
led.freq(2000)
led.duty(0)  # Start with LED off

while True:
    xValue = xAxis.read_u16()
    yValue = yAxis.read_u16()
    buttonValue = button.value()
    buttonStatus = "not pressed"

    if buttonValue == 0:
        buttonStatus = "pressed"
        
    print("X:", xValue, "Y:", yValue, 
            "-- button value:", buttonValue, 
            "status:", buttonStatus)

    brightness = int(xValue / 64)  # 65535 / 1023 = 64
    
    led.duty(brightness)
    print("X:", xValue, "Brightness:", brightness)
    utime.sleep(0.2)