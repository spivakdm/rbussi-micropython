"""A local function and a three-note sequence."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; use a suitable passive piezo circuit.
# Start the piezo output LOW, before attaching PWM.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
# Prepare PWM at 2000 Hz, initially silent with zero fill ratio.
sound = PWM(pin, freq=2000, duty_u16=0)


def beep(frequency, duration_ms):
    # Change the repetition frequency in Hz: this changes the pitch.
    sound.freq(frequency)
    # Enable approximately 50% fill: half of each period HIGH, half LOW.
    sound.duty_u16(32768)
    try:
        # This first beep is blocking: other code waits until the note ends.
        sleep_ms(duration_ms)
    finally:
        sound.duty_u16(0)


try:
    # Visit each list item once, from the lowest to the highest note.
    for frequency in [1000, 1500, 2000]:
        beep(frequency, 200)
        sleep_ms(200)
finally:
    # Cleanup runs after completion, an error or Ctrl+C.
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    # Release the PWM peripheral after normal completion, an error or Ctrl+C.
    sound.deinit()
    # Leave the physical pin LOW after PWM has been released.
    pin.value(0)
