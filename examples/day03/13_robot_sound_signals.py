"""Three original robot signals using lists, rests and a local function."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; confirm free pin and a suitable passive piezo circuit.
# A pair is (frequency in Hz, duration in ms); 0 Hz means a silent rest.
STARTUP = [(1000, 120), (1500, 120), (2000, 200)]
SUCCESS = [(1500, 100), (0, 80), (2000, 300)]
ALERT = [(800, 150), (0, 150), (800, 150), (0, 150), (800, 150)]

# Create the output with PWM initially silent.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)


def play_signal(sequence):
    # One function can play any of the lists above.
    for frequency, duration_ms in sequence:
        if frequency == 0:
            # Rest: do not call sound.freq(0); just disable the PWM drive.
            sound.duty_u16(0)
        else:
            sound.freq(frequency)
            sound.duty_u16(32768)  # Approximately 50% fill ratio.
        try:
            sleep_ms(duration_ms)  # Blocking, suitable for this local demo.
        finally:
            sound.duty_u16(0)  # Stop this note even if it is interrupted.
        sleep_ms(30)  # Separate adjacent notes slightly.


try:
    # This list contains three named sequences; play them one after another.
    for name, sequence in [("Startup", STARTUP), ("Success", SUCCESS), ("Alert", ALERT)]:
        print(name)  # Identify the signal in Thonny Shell.
        play_signal(sequence)
        sleep_ms(700)  # Silence between the three demonstrations.
finally:
    # Always stop and release PWM, including after Ctrl+C.
    sound.duty_u16(0)
    sound.deinit()
    pin.value(0)
