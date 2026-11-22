import machine
import time

servo = machine.PWM(machine.Pin(9), freq=50)   # set freq once

def scale(x, in_min, in_max, out_min, out_max):   # renamed: don't shadow built-in map()
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

def set_servo_angle(angle):
    # 0.5 ms to 2.5 ms pulse, in nanoseconds
    servo.duty_ns(scale(angle, 0, 180, 500_000, 2_500_000))

try:
    while True:
        for angle in range(0, 181, 10):
            set_servo_angle(angle)
            time.sleep(0.5)
        for angle in range(180, -1, -10):
            set_servo_angle(angle)
            time.sleep(0.5)

except KeyboardInterrupt:
    servo.deinit()    # stop the signal when you press Ctrl+C