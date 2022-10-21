import threading
import time
#import RPi.GPIO as IO
class wind():
    """ Wind resistance simulation"""
    def __init__(self):
        """
        Class constructor

        Parameter:
        ---------
        synchro: threading.Lock
            to synchronize the end of the client subscriber
         
        """
        # Lock thread synchronization
        self.lock = threading.Lock()
        self.lock.acquire()
        self.run_status=False
        self.debug=True
        # Raspberry configuration
        # Pins and parameters config
        self.pin_motor_pwm=19
        self.pin_motor_dir=16
        # In Hz
        self.sampling_freq=100
        # From 0 to 100
        self.motor_dutycycle_max=10
        # Raspberry I/O init
        self.init_pwm
        # Duration of wind simulation in seconds
        self.brake_duration=5 
        self.brake_slope=1

    def init_pwm(self):
        IO.setmode(IO.BCM) 
        IO.setup(self.pin_motor_pwm, IO.OUT)
        IO.setup(self.pin_motor_dir, IO.OUT)
        self.motor=IO.PWM(self.pin_motor_pwm, self.sampling_freq)
        self.motor.start(0)
        IO.ouput(self.pin_motor_dir, IO.HIGH)

    def seq_pwm(self):
        # Brake application
        IO.ouput(self.pin_motor_dir, IO.HIGH)
        # Brake slope
        step_time=self.brake_slope/self.motor_dutycycle_max
        for index in range(1, self.motor_dutycycle_max+1):
            self.motor.ChangeDutyCycle(self.motor_dutycycle_max)
            time.sleep(step_time)
        # Constant
        time.sleep(self.brake_duration-2*self.brake_slope)
        # Brake release
        IO.ouput(self.pin_motor_dir, IO.LOW)
        for index in range(1, self.motor_dutycycle_max+1):
            self.motor.ChangeDutyCycle(self.motor_dutycycle_max)
            time.sleep(step_time)

    def resistance(self):
        """ client function launched in a thread
        """
        if self.debug==True: print("Start thread wind resistance")
        
        while self.run_status:
            self.lock.acquire()
            if self.run_status:
                if self.debug==True: print("Break application")
                self.seq_pwm(self)
                if self.debug==True: print("Break release")

        if self.debug==True: print("End thread wind resistance")

    def activate(self):
        try:
            self.lock.release()
        except:
            print('wind resistance synchro problem')
   
    def run(self):
        """ Start the thread """
        self.task=threading.Thread(target=self.resistance) 
        self.run_status=True
        self.task.start()

    def wait(self):
        """ Wait the thread ending"""
        self.task.join()

    def stop(self):
        """ Stop the thread """
        self.run_status=False
        self.lock.release()
        self.task.join()

if __name__ == "__main__":
    """ Exemple of subscriber use"""

    wind=wind()
    wind.run()
    time.sleep(2)
    print('Activate')
    wind.activate()
    time.sleep(10)
    wind.stop()