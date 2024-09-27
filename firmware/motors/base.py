import common


def init_gpio():
    common.gpio_setup(pul_pin=settings.PUL_PIN_BASE,
                      dir_pin=settings.DIR_PIN_BASE,
                      ena_pin=settings.ENA_PIN_BASE)

def rotate(degrees, speed, direction):
    common.rotate_motor(pul_pin=settings.PUL_PIN_BASE,
                        dir_pin=settings.DIR_PIN_BASE,
                        ena_pin=settings.ENA_PIN_BASE,
                        gear_ratio=settings.GEAR_RATIO_BASE,
                        steps_per_degree=settings.STEPS_PER_DEGREE_BASE,
                        degrees=degrees,
                        speed=speed,
                        direction=direction)
