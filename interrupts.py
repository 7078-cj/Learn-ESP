import machine
import time

led = machine.Pin(2, machine.Pin.OUT)
sw = machine.Pin(0, machine.Pin.IN)

def handle_interrupt(pin):
    state = 'pressed' if pin.value() == 0 else 'not pressed'
    print(f"Switch state changed: {state}")
    led.value(not led.value())  # Toggle the LED state

sw.irq(trigger=machine.Pin.IRQ_FALLING, handler=handle_interrupt)