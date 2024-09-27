import common


def init_gpio():
    common.gpio_setup(pul_pin=settings.PUL_PIN_WRIST,
                      dir_pin=settings.DIR_PIN_WRIST,
                      ena_pin=settings.ENA_PIN_WRIST)

def rotate(degrees, speed, direction):
    common.rotate_motor(pul_pin=settings.PUL_PIN_WRIST,
                        dir_pin=settings.DIR_PIN_WRIST,
                        ena_pin=settings.ENA_PIN_WRIST,
                        gear_ratio=settings.GEAR_RATIO_WRIST,
                        steps_per_degree=settings.STEPS_PER_DEGREE_WRIST,
                        degrees=degrees,
                        speed=speed,
                        direction=direction)
