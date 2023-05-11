import threading
import main 
from record_and_send import main as mic_main
 
# Application settings
APP_NAME = 'AVMS - MERILEC USPEŠNOSTI KONCERTA'
BORDER_WIDTH = 70  # number of pixels that are empty around the border of the app window to account for taskbar position

# Arduino connection settings
COM_PORT = 'COM3'
BAUD_RATE = 115200
TIMEOUT = 2e-5

# Git settings and data
REPOSITORY_PATH = 'C:\\Users\\Urban\\Documents\\Fakulteta za Elektrotehniko\\AVMS\\AVMS-Meritve'

class main_thread(threading.Thread):
    def __init__(self, thread_name, thread_ID):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
 
        # helper function to execute the threads
    def run(self):
        app = main.Application(iApp_name=APP_NAME, iArduino_COM_port=COM_PORT,
                      iBaud_rate=BAUD_RATE, iTimeout=TIMEOUT)
        app.mainloop()

class mic_thread(threading.Thread):
    def __init__(self, thread_name, thread_ID):
        threading.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
 
        # helper function to execute the threads
    def run(self):
        mic_main()
 
thread1 = main_thread("GUI", 1000)
thread2 = mic_thread("Mic", 2000)
 
thread1.start()
thread2.start()
 
print("Exit")