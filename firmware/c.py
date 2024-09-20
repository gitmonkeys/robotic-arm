import RPi.GPIO as GPIO
import time

# Define GPIO pins
PUL_PIN = 22  # Pulse pin
DIR_PIN = 27  # Direction pin
ENA_PIN = 17  # Optional enable pin

# Motor parameters
STEPS_PER_REV = 3200
STEPS_PER_DEGREE = STEPS_PER_REV / 360

# Define step counts
steps_right = int(45* STEPS_PER_DEGREE)
steps_left = int(15* STEPS_PER_DEGREE)

# Setup GPIO mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUL_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(ENA_PIN, GPIO.OUT)


 #Function to rotate the motor
def rotate_motor(steps, direction):
	GPIO.output(DIR_PIN,direction) # Set direction
	GPIO.output(ENA_PIN,GPIO.HIGH) #Enable the driver
	
	for _ in range(steps):
		GPIO.output(PUL_PIN, GPIO.HIGH)
		time.sleep(0.005)
		GPIO.output(PUL_PIN, GPIO.LOW)
		time.sleep(0.005)
		# End for
	GPIO.output(ENA_PIN, GPIO.LOW) #Disable the driver
	
try:
	print("Try")
	# Rotate right 45 degrees
	rotate_motor(steps_right,GPIO.HIGH)
	
	time.sleep(0.5)
	GPIO.output(ENA_PIN,GPIO.HIGH)
	# Rotate left 15 degrees
	rotate_motor(steps_left,GPIO.LOW)
#	time.sleep(5)
#	
#	# Rotate left 15 degrees
#	rotate_motor(steps_left, GPIO.LOW)
#	time.sleep(5)
#	
#	# Rotate left 15 degrees
#	rotate_motor(steps_left,GPIO.LOW)
#	time.sleep(5)
	
except KeyboardInterrupt:
	print("Program Interrupt")
	
finally:
	print("clean up")
	GPIO.cleanup()
	
	
