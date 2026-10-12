"""Move forward using GPIO and PWM directly, without RBussi.

Run with wheels lifted and the motor battery connected.
Wemos D1 R32 header names below map to ESP32 GPIO numbers.
"""
from machine import Pin, PWM
from time import sleep

D3 = 25
D8 = 12
D9 = 13
D11 = 23
D12 = 19
D13 = 18

# Direction: 0 means forward on our robot.
right_direction = Pin(D12, Pin.OUT, value=0)
left_direction = Pin(D13, Pin.OUT, value=0)

# Brake: 1 = engaged, 0 = released.
right_brake = Pin(D9, Pin.OUT, value=1)
left_brake = Pin(D8, Pin.OUT, value=1)

# PWM: start with zero power.
right_pwm = PWM(Pin(D3), freq=1000, duty_u16=0)
left_pwm = PWM(Pin(D11), freq=1000, duty_u16=0)

try:
    # Select forward direction.
    right_direction.value(0)
    left_direction.value(0)

    # Release both brakes.
    right_brake.value(0)
    left_brake.value(0)

    # Set motor power to 70%.
    duty = int(65535 * 0.70)
    right_pwm.duty_u16(duty)
    left_pwm.duty_u16(duty)

    # Keep moving for half a second.
    sleep(0.5)

finally:
    # Stop both motors, including on Ctrl+C.
    right_pwm.duty_u16(0)
    left_pwm.duty_u16(0)
    right_brake.value(1)
    left_brake.value(1)

    # Release PWM resources.
    right_pwm.deinit()
    left_pwm.deinit()
