"""Change one parameter at a time. Duty is not linear volume control."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; use a suitable passive piezo circuit.
# Start the piezo output LOW, before attaching PWM.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
# Prepare PWM at 2000 Hz, initially silent with zero fill ratio.
sound = PWM(pin, freq=2000, duty_u16=0)
try:
    # Compare pitch while keeping the fill ratio and duration unchanged.
    for frequency in [500, 1000, 2000, 4000]:
        print("Frequency:", frequency, "Hz; fill: 50%")
        # Set this trial frequency before enabling the waveform.
        sound.freq(frequency)
        # Keep fill at 50% while comparing different pitches.
        sound.duty_u16(32768)
        sleep_ms(300)
        sound.duty_u16(0)
        # Leave a silent gap before the next sound trial.
        sleep_ms(500)

    sound.freq(2000)
    # Now hold pitch fixed and compare waveform fill ratios, not linear volume.
    for percent in [10, 25, 50]:
        print("Frequency: 2000 Hz; fill:", percent, "%")
        # Convert a percentage to the integer PWM range 0..65535.
        sound.duty_u16(65535 * percent // 100)
        sleep_ms(300)
        sound.duty_u16(0)
        # Leave a silent gap before the next sound trial.
        sleep_ms(500)
finally:
    # Cleanup runs after completion, an error or Ctrl+C.
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    # Release the PWM peripheral after normal completion, an error or Ctrl+C.
    sound.deinit()
    # Leave the physical pin LOW after PWM has been released.
    pin.value(0)
