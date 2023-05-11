import soundcard as sc
import numpy as np
from circular_buffer_numpy.circular_buffer import CircularBuffer
import librosa as lr
import os

data = np.zeros(2)

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

if __name__ == '__main__':
    samplerate = 44100
    data_buffer = CircularBuffer(shape = (int(samplerate),2), dtype = 'float64')
    data_point = np.empty(shape = data_buffer.data_shape)
    # recording_mic = sc.get_microphone('Focusrite Usb Audio')
    recording_mic = sc.get_microphone('Realtek(R) Audio')
    
    dir_name = 'C:\\Users\\Urban\\Documents\\Fakulteta za Elektrotehniko\\AVMS\\AVMS-Projekt\\Data'
    
    test = os.listdir(dir_name)

    for item in test:
        if item.endswith(".npy"):
            os.remove(os.path.join(dir_name, item))
    
    with recording_mic.recorder(samplerate=samplerate) as mic:
        frame = 0
        i = 0
        file = 0
        while(1):
            data = mic.record(numframes=1)
            data = np.squeeze(data)
            data_buffer.append(data)

            
            if i == data_buffer.shape[0]:
                data = data_buffer.get_all()
                np.save(dir_name+'/recorded_data_' + str(file), data, allow_pickle=True)
                file += 1
                i = 0
                
            i += 1
            
            
            