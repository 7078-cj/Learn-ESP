# Boat Controller Wiring (ESP32-S3 + Breadboard)

Wiring for `boat.py`: a joystick, potentiometer, L293D + DC motor, servo, and I2C LCD, all on one breadboard.

**Unplug USB while wiring.** Connect power last.

---

## 1. Pin map (from `boat.py`)

| Part | Signal | ESP32-S3 pin | Notes |
|---|---|---|---|
| Joystick | X axis (VRx) | GPIO 13 | ADC, controls the servo |
| Joystick | Y axis (VRy) | GPIO 12 | ADC, controls the motor |
| Joystick | Button (SW) | GPIO 11 | internal pull-up, pressed = 0 |
| Potentiometer | Wiper (middle pin) | GPIO 8 | ADC, top-speed limit |
| L293D | IN1 (pin 2) | GPIO 4 | PWM, 1000 Hz |
| L293D | IN2 (pin 7) | GPIO 5 | PWM, 1000 Hz |
| Servo | Signal | GPIO 17 | PWM, 50 Hz |
| LCD (I2C) | SDA | GPIO 37 | see the PSRAM note in section 8 |
| LCD (I2C) | SCL | GPIO 36 | see the PSRAM note in section 8 |

---

## 2. Block diagram

```
                         ┌───────────────────┐
 Joystick X  (VRx) ─────▶│ GPIO 13           │
 Joystick Y  (VRy) ─────▶│ GPIO 12           │
 Joystick button   ─────▶│ GPIO 11           │
 Potentiometer     ─────▶│ GPIO 8            │
                         │                   │
                         │     ESP32-S3      │
                         │                   │
                         │           GPIO 4  │─────▶ L293D IN1 ─┐
                         │           GPIO 5  │─────▶ L293D IN2 ─┴─▶ DC motor
                         │           GPIO 17 │─────▶ Servo signal
                         │           GPIO 37 │─────▶ LCD SDA
                         │           GPIO 36 │─────▶ LCD SCL
                         └───────────────────┘
```

---

## 3. Breadboard power rails

Set up the rails first, then connect parts to them.

| Rail | Connect to |
|---|---|
| Left `+` (red) | ESP32 **5V** |
| Left `−` (blue) | ESP32 **GND** |
| Right `+` (red) | ESP32 **3V3** |
| Right `−` (blue) | ESP32 **GND** (also link to the left `−` rail with one jumper) |

- Many full-size breadboards have rails that are **split in the middle**. Check for a gap in the red and blue lines, and bridge the halves with a jumper if your parts sit on both.
- The ESP32 **5V pin only has power while USB is plugged in**.
- Everything must share one ground.

---

## 4. Part by part

### Joystick

| Joystick pin | Connect to |
|---|---|
| GND | GND rail |
| +5V (may be labeled VCC) | **3V3 rail** (not 5V) |
| VRx | GPIO 13 |
| VRy | GPIO 12 |
| SW | GPIO 11 |

Power it from 3.3V so the signals never exceed what the ESP32 ADC pins tolerate.

### Potentiometer

| Pot pin | Connect to |
|---|---|
| Left leg | 3V3 rail |
| Middle (wiper) | GPIO 8 |
| Right leg | GND rail |

Swapping the outer legs only reverses the direction.

### L293D motor driver

Place the chip **across the center gap** of the breadboard, with the notch at the top (pin 1 top-left, pin 16 top-right).

```
            ┌───U───┐
 EN1,2  (1) │       │ (16)  VCC1
 IN1    (2) │       │ (15)  IN4      → GND
 OUT1   (3) │       │ (14)  OUT4     (leave empty)
 GND    (4) │ L293D │ (13)  GND
 GND    (5) │       │ (12)  GND
 OUT2   (6) │       │ (11)  OUT3     (leave empty)
 IN2    (7) │       │ (10)  IN3      → GND
 VCC2   (8) │       │ (9)   EN3,4    → GND
            └───────┘
```

| L293D pin | Connect to |
|---|---|
| 1 (EN1,2) | 5V rail |
| 2 (IN1) | GPIO 4 |
| 3 (OUT1) | motor wire A |
| 4, 5, 12, 13 (GND) | GND rail |
| 6 (OUT2) | motor wire B |
| 7 (IN2) | GPIO 5 |
| 8 (VCC2, motor power) | 5V rail for a first test, or battery `+` (see section 5) |
| 9, 10, 15 | GND rail (unused inputs, so they don't float) |
| 11, 14 | leave empty |
| 16 (VCC1, chip power) | 5V rail |

The motor's wires end in sockets, so plug a male-to-male jumper into each, then put the other ends in the breadboard rows of pins 3 and 6. If the motor spins the wrong way, swap those two jumpers.

### Servo

| Servo wire | Connect to |
|---|---|
| Red | 5V (see section 5) |
| Brown or black | GND rail |
| Orange or yellow | GPIO 17 |

### LCD (I2C backpack)

| LCD pin | Connect to |
|---|---|
| GND | GND rail |
| VCC | 5V rail |
| SDA | GPIO 37 |
| SCL | GPIO 36 |

If the text is invisible, turn the small blue contrast screw on the backpack.

---

## 5. Power notes

The motor and servo both draw spikes of current, and on USB power alone the board can reset when the motor reverses while the servo moves (symptom: `SerialException ... Access is denied` and COM6 disappearing).

- **Motor:** move L293D pin 8 to a battery `+` (such as the 9V connector) and connect the battery `−` to the shared GND rail. Keep pins 1 and 16 on the ESP32's 5V. The L293D drops about 2V, and `MAX_SPEED = 70` in the code limits the top speed. Check your motor's rating first.
- **Servo:** for best results, power it from its own 5-6V supply (for example 4×AA), with its ground joined to the shared GND rail.
- **Never** connect a battery or external supply `+` to the ESP32's 5V pin or to the servo from a 9V battery.
- **Capacitor:** put a 100-470 µF electrolytic across the 5V and GND rails, with the striped (negative) leg on GND.

---

## 6. Before powering on

- [ ] ESP32 GND, L293D GND (pins 4, 5, 12, 13), servo GND, LCD GND, and any battery `−` are all on the same ground
- [ ] L293D notch faces up, and the chip straddles the center gap
- [ ] L293D pins 1, 16, and 8 are powered, and pins 9, 10, 15 are on GND
- [ ] Joystick and pot are on **3V3**, not 5V
- [ ] Servo red is on 5V (or its own supply), not 3V3
- [ ] No bare jumper ends touching each other

---

## 7. Run it

From the `Learn ESP` folder (the one that contains `lib/`):

```powershell
python tools/run.py run boat.py
```

Leave the joystick alone while it prints "Calibrating joystick...". Stop with `Ctrl+C`.

---

## 8. Troubleshooting

| Problem | Check |
|---|---|
| Board resets or USB disconnects when the motor reverses | Section 5: separate motor supply, capacitor |
| Motor hums but doesn't spin | Raise `min_speed` in `normalize_motor`, or check pin 8 power |
| Motor doesn't move at all | L293D pins 1, 8, 16 powered, and GPIO 4 and 5 wires in place |
| Motor or servo moves the wrong way | Swap the motor jumpers, or change `90 - x * 0.8` to `90 + x * 0.8` |
| Servo buzzes at the ends | Narrow `SERVO_MIN_NS` and `SERVO_MAX_NS` |
| LCD blank | Contrast screw, VCC on 5V, SDA and SCL not swapped |
| `ImportError: no module named 'lib'` | Run from the `Learn ESP` folder so `mount .` includes `lib/` |
| ADC reads stuck near maximum | Keep `atten=ADC.ATTN_11DB` on the joystick and pot pins |

**ESP32-S3 pin cautions**

- **GPIO 36 and 37 (the LCD pins) are reserved for PSRAM on boards with octal PSRAM** (the N8R8 and N16R8 variants). If your LCD is flaky or the board misbehaves, move SDA and SCL to other pins such as GPIO 8 and 9, and update the `I2C(...)` line.
- **GPIO 12 and 13 are ADC2 pins.** They work as long as WiFi is off. If you add WiFi later, move the joystick to GPIO 1-10 (ADC1).