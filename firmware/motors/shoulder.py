import common


def init_gpio():
    common.gpio_setup(ena_pin=settings.PUL_PIN_SHOULDER,
                      dir_pin=settings.DIR_PIN_SHOULDER,
                      ena_pin=settings.ENA_PIN_SHOULDER)

def rotate(degrees, speed, direction):
    common.rotate_motor(pul_pin=settings.PUL_PIN_SHOULDER,
                        dir_pin=settings.DIR_PIN_SHOULDER,
                        ena_pin=settings.ENA_PIN_SHOULDER,
                        gear_ratio=settings.GEAR_RATIO_SHOULDER,
                        steps_per_degree=settings.STEPS_PER_DEGREE_SHOULDER,
                        degrees=degrees,
                        speed=speed,
                        direction=direction)
