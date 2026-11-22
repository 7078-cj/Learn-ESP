from machine import Pin, ADC, PWM
from time import sleep

# Initialize ADC on GPIO 1
pot = ADC(Pin(1))
led = PWM(Pin(4))
led.freq(2000)
led.duty(0)  # type: ignore # Start with LED off

# Set attenuation to read the full 0V - 3.3V range
pot.atten(ADC.ATTN_11DB)

def read_smooth(samples=10):
    total = 0
    for _ in range(samples):
        total += pot.read_u16()
    return total // samples

while True:
    # Read 16-bit value (0 to 65535)
    pot_value = read_smooth()
    brightness = int(pot_value / 64)
    print(pot_value, brightness)
    led.duty(brightness)  # type: ignore
    sleep(0.2)
