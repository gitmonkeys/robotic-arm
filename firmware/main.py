import threading
import settings
from .motors import *


if __name__ == "__main__":
    GPIO.setmode(GPIO.BCM)

    base.init_gpio()
    shoulder.init_gpio()
    elbow.init_gpio()
    wrist.init_gpio()

    try:
        print("Try")
        shoulder.rotate(degrees=10, speed=100, direction=settings.CW)
        time.sleep(0.5)
        shoulder.rotate(degrees=10, speed=100, direction=settings.CCW)

    except KeyboardInterrupt:
        print("Program Interrupt")

    finally:
        print("clean up")
        GPIO.cleanup()
