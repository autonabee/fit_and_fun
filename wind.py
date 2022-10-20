import threading
import time

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
        self.run_status= False
        self.debug=True


    def resistance(self):
        """ client function launched in a thread
        """
        if self.debug==True: print("Start wind resistance")
        
        while self.run_status:
            self.lock.acquire()
            if self.run_status:
                print('Resistance up')
                time.sleep(5)
                print('Resistance down')
        
        if self.debug==True: print("End wind resistance")

    def activate(self):
        try:
            wind.lock.release()
        except:
            print('wind resistance already in use')
   
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