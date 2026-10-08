"""Stop both motor channels. May be run at any time from Thonny."""
from machine import Pin, PWM
for gpio in (25, 23):
    pwm = PWM(Pin(gpio), freq=1000, duty_u16=0)
    pwm.deinit()
    Pin(gpio, Pin.OUT, value=0)
Pin(13, Pin.OUT, value=1)
Pin(12, Pin.OUT, value=1)
print('Both motors stopped')
