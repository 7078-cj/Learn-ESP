import machine
import time

led = machine.Pin(2, machine.Pin.OUT)
sw = machine.Pin(0, machine.Pin.IN) # 0 is input, 1 is output

sw_state = sw.value()  # Read the initial state of the switch
print(f"Initial switch state: {'pressed' if sw_state == 0 else 'not pressed'}")

while True:
    sw_state = sw.value()  # Read the current state of the switch
    if sw_state == 0:
        print("Switch is pressed")
        led.on()  # Turn the LED on
    else:
        print("Switch is not pressed")
        led.off()  # Turn the LED off
    time.sleep(0.1)  # Add a small delay to avoid flooding the output


# led.on()  # Turn the LED on
# led.off()  # Turn the LED off

# led.on()  # Turn the LED on
# led.off()  # Turn the LED off

# led.value(1)  # Turn the LED on
# led.value(0)  # Turn the LED off

# led.value(True)  # Turn the LED on
# led.value(False)  # Turn the LED off

# counter = 0
# while counter < 10:
#     led.on()  # Turn the LED on
#     time.sleep(1)  # Wait for 1 second
#     led.off()  # Turn the LED off
#     time.sleep(1)  # Wait for 1 second
#     counter += 1