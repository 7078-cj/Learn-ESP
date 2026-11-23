from machine import Pin, PWM
import time

in1 = PWM(Pin(4), freq=1000)
in2 = PWM(Pin(5), freq=1000)

def drive(speed):
    """speed: -100 (full reverse) to 100 (full forward), 0 = stop"""
    duty = int(abs(speed) / 100 * 65535)
    if speed > 0:
        in1.duty_u16(duty)
        in2.duty_u16(0)
    elif speed < 0:
        in1.duty_u16(0)
        in2.duty_u16(duty)
    else:
        in1.duty_u16(0)
        in2.duty_u16(0)

try:
    drive(60);   time.sleep(2)    # forward
    drive(0);    time.sleep(1)    # stop
    drive(-60);  time.sleep(2)    # reverse
    drive(0)
finally:
    in1.deinit()
    in2.deinit()