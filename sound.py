from machine import Pin, PWM
import time

p9 = Pin(9, Pin.OUT)


# buzzer.freq(1000)  # Set frequency to 1 kHz
# buzzer.duty(50)  # type: ignore # Set duty cycle to 50% (range is 0-65535)

# time.sleep(1)  # Play sound for 1 second
# buzzer.duty(0)  # type: ignore # Turn off the buzzer
# buzzer.deinit()  # Deinitialize the PWM to free up the pin
C4, D4, E4, F4, G4, A4, B4, C5 = 262, 294, 330, 349, 392, 440, 494, 523
REST = 0

mary = [
    E4, D4, C4, D4, E4, E4, E4, REST,
    D4, D4, D4, REST,
    E4, G4, G4, REST,
    E4, D4, C4, D4, E4, E4, E4, E4,
    D4, D4, E4, D4, C4,
]

def play(pin, melodies, delays, duty, gap=0.05):
    buzzer = PWM(pin)
    for note in melodies:
        if note == REST:
            buzzer.duty(0)  # type: ignore
        else:
            buzzer.freq(note)
            buzzer.duty(duty)  # type: ignore
        time.sleep(delays - gap)
        buzzer.duty(0)  # type: ignore   # short silence between notes
        time.sleep(gap)
    buzzer.duty(0)  # type: ignore
    buzzer.deinit()

play(p9, mary, 0.15, 512)  # Play the melody on pin 9 with 50% duty cycle
