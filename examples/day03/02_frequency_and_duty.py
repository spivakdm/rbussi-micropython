"""Change one parameter at a time. Duty is not linear volume control."""
from machine import Pin, PWM
from time import sleep_ms

PIEZO_GPIO = 26  # D2; use a suitable passive piezo circuit.
pin = Pin(PIEZO_GPIO, Pin.OUT, value=0)
sound = PWM(pin, freq=2000, duty_u16=0)
try:
    for frequency in [500, 1000, 2000, 4000]:
        print("Frequency:", frequency, "Hz; fill: 50%")
        sound.freq(frequency)
        sound.duty_u16(32768)
        sleep_ms(300)
        sound.duty_u16(0)
        sleep_ms(500)

    sound.freq(2000)
    for percent in [10, 25, 50]:
        print("Frequency: 2000 Hz; fill:", percent, "%")
        sound.duty_u16(65535 * percent // 100)
        sleep_ms(300)
        sound.duty_u16(0)
        sleep_ms(500)
finally:
    sound.duty_u16(0)  # Stop the PWM waveform before releasing it.
    sound.deinit()
    pin.value(0)
