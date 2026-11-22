import machine
import time

servo = machine.PWM(machine.Pin(9), freq=50)   # set freq once

def scale(x, in_min, in_max, out_min, out_max):   # renamed: don't shadow built-in map()
    return int((x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min)

zero_angle_pulse = 500_000  # 0.5 ms pulse for zero angle
one_eighty_angle_pulse = 3_000_000  # 3 ms pulse for 180 degrees

def set_servo_angle(angle):
    # 0.5 ms to 2.5 ms pulse, in nanoseconds
    servo.duty_ns(scale(angle, 0, 180, zero_angle_pulse, one_eighty_angle_pulse))

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