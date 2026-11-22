import machine
import time

led = machine.Pin(2, machine.Pin.OUT)

# led.on()  # Turn the LED on
# led.off()  # Turn the LED off

# led.on()  # Turn the LED on
# led.off()  # Turn the LED off

# led.value(1)  # Turn the LED on
# led.value(0)  # Turn the LED off

# led.value(True)  # Turn the LED on
# led.value(False)  # Turn the LED off

counter = 0
while counter < 10:
    led.on()  # Turn the LED on
    time.sleep(1)  # Wait for 1 second
    led.off()  # Turn the LED off
    time.sleep(1)  # Wait for 1 second
    counter += 1