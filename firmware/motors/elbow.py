import common


def init_gpio():
    common.gpio_setup(ena_pin=settings.PUL_PIN_ELBOW,
                      dir_pin=settings.DIR_PIN_ELBOW,
                      ena_pin=settings.ENA_PIN_ELBOW)

def rotate(degrees, speed, direction):
    common.rotate_motor(pul_pin=settings.PUL_PIN_ELBOW,
                        dir_pin=settings.DIR_PIN_ELBOW,
                        ena_pin=settings.ENA_PIN_ELBOW,
                        gear_ratio=settings.GEAR_RATIO_ELBOW,
                        steps_per_degree=settings.STEPS_PER_DEGREE_ELBOW,
                        degrees=degrees,
                        speed=speed,
                        direction=direction)
