"""A short tone: use a suitable passive piezo; motor power off."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; confirm it is free and the piezo circuit is suitable.
# Start the piezo output LOW, before attaching PWM.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
# Prepare PWM at 2000 Hz, initially silent with zero fill ratio.
sound = PWM(pin, freq=2000, duty_u16=0)
try:
    sound.duty_u16(32768)  # Approximately 50% fill ratio.
    sleep_ms(200)
finally:
    # Cleanup runs after completion, an error or Ctrl+C.
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    # Release the PWM peripheral after normal completion, an error or Ctrl+C.
    sound.deinit()
    # Leave the physical pin LOW after PWM has been released.
    pin.value(0)
