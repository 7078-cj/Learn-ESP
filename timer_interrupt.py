from machine import Timer, Pin
import neopixel

led_1 = Pin(2, Pin.OUT)                  # plain LED (check your board's pin)
np = neopixel.NeoPixel(Pin(48), 1)       # RGB LED
rgb_on = False

def handle_A(timer):
    led_1.value(not led_1.value())

def handle_B(timer):
    global rgb_on
    rgb_on = not rgb_on
    np[0] = (20, 0, 0) if rgb_on else (0, 0, 0)   # red / off
    np.write()

tim0 = Timer(0)
tim1 = Timer(1)
tim0.init(period=100, mode=Timer.PERIODIC, callback=handle_A)   # every 100 ms
tim1.init(period=500, mode=Timer.PERIODIC, callback=handle_B)   # every 500 ms