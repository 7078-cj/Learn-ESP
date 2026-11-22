import time
import machine

#polling method 
led =machine.Pin(2, machine.Pin.OUT)
sw = machine.Pin(0, machine.Pin.IN)

def blink_led_ntimes(n, msg):
    print(msg)
    for _ in range(n):
        led.on()
        time.sleep(0.5)
        led.off()
        time.sleep(0.5)

while True:
    if sw.value() == 0:
        print("Switch is pressed")
        blink_led_ntimes(3, "Blinking LED 3 times because switch is pressed")
    else:
        print("Switch is not pressed")
        led.off()