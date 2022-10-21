import RPi.GPIO as IO

IO.setmode(IO.BCM) # choix de la norme d'appel des pins
PIN_MOTOR_PWM = 19
PIN_MOTOR_DIR = 16
IO.setup(PIN_MOTOR_PWM,IO.OUT)
IO.setup(PIN_MOTOR_DIR,IO.OUT)

SAMPLING_FREQ=100
motor=IO.PWM(19,SAMPLING_FREQ))

MOTOR_DUTYCYCLE=0
motor.start(MOTOR_DUTYCYCLE)

obstable = TRUE
DURATION_OBSTACLE=5 # secondes
DURATION_OBSTACLE_EDGE=0.5 #secondes

if obstacle=TRUE :
    # Serrage du frein
    for time in range(DURATION_OBSTACLE_EDGE) :
        Dir = HIGH
        IO.ouput(PIN_MOTOR_DIR,Dir)

        MOTOR_DUTYCYCLE=10 # pourcentage
        motor.ChangeDutyCycle(MOTOR_DUTYCYCLE)
        time.sleep(1/SAMPLING_FREQ)

    # Plateau
    for time in range(DURATION_OBSTACLE-2*DURATION_OBSTACLE_EDGE) :
        time.sleep(1/SAMPLING_FREQ)

    # Déserrage du frein
    for time in range(DURATION_OBSTACLE_EDGE) :
        Dir = HIGH
        IO.ouput(PIN_MOTOR_DIR,Dir)

        MOTOR_DUTYCYCLE=10 # pourcentage
        motor.ChangeDutyCycle(MOTOR_DUTYCYCLE)
        time.sleep(1/SAMPLING_FREQ)
