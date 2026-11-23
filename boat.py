from machine import Pin, ADC, PWM, I2C
from lib.lcd1602 import LCD
import time

ADC_MAX = 65535
JOY_CENTER = 32768     # replace with your measured resting value
JOY_DEADZONE = 4000    # ignore wobble this close to the center

def clamp(v, lo, hi):
    return max(lo, min(hi, v))

joystick_x = ADC(Pin(13), atten=ADC.ATTN_11DB)
joystick_y = ADC(Pin(12), atten=ADC.ATTN_11DB)
joystick_button = Pin(11, Pin.IN, Pin.PULL_UP)

motor_in1 = PWM(Pin(4), freq=1000)
motor_in2 = PWM(Pin(5), freq=1000)

pot = ADC(Pin(8), atten=ADC.ATTN_11DB)
servo = PWM(Pin(17), freq=50) 

i2c = I2C(0, sda=Pin(37), scl=Pin(36), freq=400000)
lcd = LCD(i2c)

def normalize_motor(speed, min_speed=30):
    """Clamp to -100..100 and skip the low range where the motor only hums.
    Any non-zero request maps to min_speed..100, and 0 stays 0."""
    speed = clamp(speed, -100, 100)
    if speed == 0:
        return 0
    magnitude = min_speed + (abs(speed) - 1) / 99 * (100 - min_speed)
    return int(magnitude if speed > 0 else -magnitude)


def drive(speed):
    """speed: -100 (full reverse) to 100 (full forward), 0 = stop"""
    speed = normalize_motor(speed)
    duty = int(abs(speed) / 100 * 65535)
    if speed > 0:
        motor_in1.duty_u16(duty)
        motor_in2.duty_u16(0)
    elif speed < 0:
        motor_in1.duty_u16(0)
        motor_in2.duty_u16(duty)
    else:
        motor_in1.duty_u16(0)
        motor_in2.duty_u16(0)

def normalize_joystick(raw, center=JOY_CENTER, deadzone=JOY_DEADZONE):
    """raw 0-65535 -> -100..100, with 0 inside the deadzone."""
    offset = raw - center
    if abs(offset) < deadzone:
        return 0
    if offset > 0:
        value = (offset - deadzone) / (ADC_MAX - center - deadzone) * 100
    else:
        value = (offset + deadzone) / (center - deadzone) * 100
    return int(clamp(value, -100, 100))

def calibrate(adc, samples=30):
    """Average the stick's resting position. Don't touch it while this runs."""
    print("Calibrating joystick, please leave it alone...")
    total = 0
    for _ in range(samples):
        total += adc.read_u16()
        time.sleep_ms(10)
    print("Calibration complete.")
    return total // samples




current = 0
STEP = 5
MAX_SPEED = 70 # max change per loop (50 ms), so 0 to 100 takes about 0.5 s

def ramp(target):
    global current
    if target > current:
        current = min(current + STEP, target)
    elif target < current:
        current = max(current - STEP, target)
    return current

def read_smooth_potentiometer(samples=10):
    total = 0
    for _ in range(samples):
        total += pot.read_u16()
    return total // samples

def normalize_pot(raw):
    """raw 0-65535 -> 0..100."""
    return int(clamp(raw / ADC_MAX * 100, 0, 100))

SERVO_MIN_NS = 500_000      # 0.5 ms  = 0°
SERVO_MAX_NS = 2_500_000    # 2.5 ms  = 180°   (center = 1.5 ms)

def set_servo(angle):
    angle = clamp(angle, 0, 180)
    ns = SERVO_MIN_NS + angle / 180 * (SERVO_MAX_NS - SERVO_MIN_NS)
    servo.duty_ns(int(ns))

SERVO_MIN_NS = 600_000
SERVO_MAX_NS = 2_400_000
SERVO_STEP = 4            # max degrees per loop
servo_angle = 90.0

def move_servo_toward(target):
    global servo_angle
    if target > servo_angle:
        servo_angle = min(servo_angle + SERVO_STEP, target)
    else:
        servo_angle = max(servo_angle - SERVO_STEP, target)
    set_servo(servo_angle)

center_x = calibrate(joystick_x)
center_y = calibrate(joystick_y)


try:
    while True:
        limit = normalize_pot(read_smooth_potentiometer())
        x = normalize_joystick(joystick_x.read_u16(), center=center_x)
        y = normalize_joystick(joystick_y.read_u16(), center=center_y)

        speed = ramp(int(y * min(limit, MAX_SPEED) / 100))
        move_servo_toward(clamp(90 - x * 0.8, 10, 170))   # 10-170°, avoids the end stops
        drive(speed)
        lcd.write(10, 0, str(speed))
        print("X:", x, "Y:", y, "limit:", limit, "speed:", speed)
        time.sleep_ms(50)

except KeyboardInterrupt:
    drive(0)
    motor_in1.deinit()
    motor_in2.deinit()
    servo.deinit()