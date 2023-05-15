import soundcard as sc
import numpy as np
from circular_buffer_numpy.circular_buffer import CircularBuffer
import librosa as lr
import os
from pathlib import Path

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

def get_tempo(buffer, sample_rate):
    '''
    Funkcija iz bufferja, v katerem je shranjen wav zvočni zapis, na podlagi sample ratea izračuna tempo
    
    Input:
        buffer - wav sound buffer
        sample_rate - sample rate of data in buffer
        
    Output:
        tempo - tempo of data in buffer
    '''
    buffer = np.array(buffer.get_all(), dtype='float64')
    buffer_right = buffer[:,0]
    buffer_left = buffer[:,1]
    tempo_levo, beats = lr.beat.beat_track(y=buffer_left,sr=sample_rate)
    tempo_desno, beats = lr.beat.beat_track(y=buffer_right,sr=sample_rate)
    
    tempo = (tempo_desno+tempo_levo)/2
    
    return tempo


def rec_mic_main(mic_data_path):
    samplerate = 44100
    data_buffer = CircularBuffer(shape = (int(samplerate),2), dtype = 'float64')
    data_point = np.empty(shape = data_buffer.data_shape)
    #recording_mic = sc.get_microphone('Focusrite Usb Audio')
    recording_mic = sc.get_microphone('Realtek(R) Audio')
    start_file_path = Path(mic_data_path + '\\Mic_controll_data\\START.txt')
    stop_file_path = Path(mic_data_path + '\\Mic_controll_data\\STOP.txt')
    
    dir_name = mic_data_path + '\\Rec_mic_data'
    
    with recording_mic.recorder(samplerate=samplerate) as mic:
        frame = 0
        i = 0
        file = 0
        while(1):
            
            if start_file_path.is_file():
                data = mic.record(numframes=1)
                data = np.squeeze(data)
                data_buffer.append(data)

                
                if i == data_buffer.shape[0]:
                    data = data_buffer.get_all()
                    np.save(dir_name + '/recorded_data_' + str(file), data, allow_pickle=True)
                    file += 1
                    i = 0
                    
                i += 1
            elif stop_file_path.is_file():
                print('ending mic thread')
                break

if __name__ == '__main__':
    rec_mic_main(MIC_DATA_PATH)
            
            
            