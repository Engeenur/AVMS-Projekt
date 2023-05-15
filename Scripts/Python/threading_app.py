import threading as thr
from record_and_send import rec_mic_main
from main import Application as App

# Application settings
APP_NAME = 'AVMS - MERILEC USPEŠNOSTI KONCERTA'
BORDER_WIDTH = 70  # number of pixels that are empty around the border of the app window to account for taskbar position

# Arduino connection settings
COM_PORT = 'COM3'
BAUD_RATE = 115200
TIMEOUT = 2e-5

# Git settings and data
REPOSITORY_PATH = 'C:\\Users\\Urban\\Documents\\Fakulteta za Elektrotehniko\\AVMS\\AVMS-Meritve'
MIC_DATA_PATH = 'C:\\Users\\Urban\\Documents\\Fakulteta za Elektrotehniko\\AVMS\\AVMS-Projekt\\Data'

class rec_mic_thread(thr.Thread):
    def __init__(self, thread_name, thread_ID):
        thr.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
 
        # helper function to execute the threads
    def run(self):
        rec_mic_main(MIC_DATA_PATH)

class app_thread(thr.Thread):
    def __init__(self, thread_name, thread_ID):
        thr.Thread.__init__(self)
        self.thread_name = thread_name
        self.thread_ID = thread_ID
 
        # helper function to execute the threads
    def run(self):
        app = App(iApp_name=APP_NAME, iArduino_COM_port=COM_PORT,
                      iBaud_rate=BAUD_RATE, iTimeout=TIMEOUT, 
                      iGit_repository_path=REPOSITORY_PATH, 
                      iMic_data_path=MIC_DATA_PATH)
        app.mainloop()
 
app_thr = app_thread("GUI_thread", 1000)
mic_thr = rec_mic_thread("mic_rec_thread", 2000)
 
app_thr.start()
mic_thr.start()

print('Exit')