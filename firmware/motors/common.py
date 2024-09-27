import RPi.GPIO as GPIO
import time
import settings


def gpio_setup(pul_pin, dir_pin, ena_pin):
    GPIO.setup(pul_pin, GPIO.OUT)
    GPIO.setup(dir_pin, GPIO.OUT)
    GPIO.setup(ena_pin, GPIO.OUT)


def rotate_motor(pul_pin, dir_pin, ena_pin, gear_ratio, steps_per_degree, degrees, speed, direction):

    int delay = 1 / speed
    int steps = int(degrees * gear_ratio * steps_per_degree)

    if direction == settings.CW:
        GPIO.output(dir_pin, GPIO.LOW)
    elif direction == settings.CCW:
        GPIO.output(dir_pin, GPIO.HIGH)

    GPIO.output(ena_pin, GPIO.HIGH)

    for _ in range(steps):
        GPIO.output(pul_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(pul_pin, GPIO.LOW)
        time.sleep(delay)

    GPIO.output(ena_pin, GPIO.LOW)
