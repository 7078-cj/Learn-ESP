from machine import I2C, Pin
from .lib.lcd1602 import LCD   # <-- your class saved as lcd1602.py
import time

# -----------------------------------------------------
# 1. Setup I2C and LCD
# -----------------------------------------------------
# Adjust pins SDA=12 and SCL=11 to match your wiring
i2c = I2C(0, sda=Pin(12), scl=Pin(11), freq=400000)

# Create an LCD object
lcd = LCD(i2c)

# -----------------------------------------------------
# 2. Basic text output
# -----------------------------------------------------
# Write a simple message (line 1 & 2 separated by \n)
lcd.message("Hello World!\nLine 2")
time.sleep(3)

# Clear the screen
lcd.clear()

# -----------------------------------------------------
# 3. Using lcd.write(x, y, text)
# -----------------------------------------------------
# lcd.write(column, row, text)
# column: 0-15   (16 characters per line)
# row:    0-1    (2 lines total)
lcd.write(0, 0, "Top Left")
lcd.write(8, 0, "Center")
lcd.write(0, 1, "Bottom Line")
time.sleep(3)

lcd.clear()

# -----------------------------------------------------
# 4. Update text dynamically
# -----------------------------------------------------
lcd.write(0, 0, "Counting:")
for i in range(11):
    lcd.write(10, 0, str(i))  # overwrite number each loop
    time.sleep(0.5)

lcd.clear()

# -----------------------------------------------------
# 5. Multiline message with lcd.message()
# -----------------------------------------------------
lcd.message("Line One\nLine Two")
time.sleep(3)

lcd.clear()

# -----------------------------------------------------
# 6. Backlight control (optional)
# -----------------------------------------------------
lcd.openlight()   # turn on backlight (already on by default)
# (You can add more if you extend the class)