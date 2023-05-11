import os
import numpy as np
from pathlib import Path
import librosa as lr
import time

def get_tempo(buffer, sample_rate):
    '''
    Funkcija iz bufferja, v katerem je shranjen wav zvočni zapis, na podlagi sample ratea izračuna tempo
    
    Input:
        buffer - wav sound buffer
        sample_rate - sample rate of data in buffer
        
    Output:
        tempo - tempo of data in buffer
    '''
    buffer = np.array(buffer, dtype='float64')
    buffer_right = buffer[:,0]
    buffer_left = buffer[:,1]
    tempo_levo, beats = lr.beat.beat_track(y=buffer_left,sr=sample_rate)
    tempo_desno, beats = lr.beat.beat_track(y=buffer_right,sr=sample_rate)
    
    tempo = (tempo_desno+tempo_levo)/2
    
    return tempo


path = Path('recorded_data.npy')
data = np.load(path, allow_pickle=True)
time_created = path.stat().st_mtime

file = 0

path = Path('Data/recorded_data_' + str(file) + '.npy')

print(path)

tempo_avg = 100
alfa = 0.5
gamma = 0.5
tempo_change = 0

while(1):
    if path.is_file():
        time_created = path.stat().st_mtime
        time.sleep(0.1)
        data = np.load(path, allow_pickle=True)
        tempo = get_tempo(data, sample_rate=44100)
        
        if abs(tempo - tempo_avg) > 5:
            tempo_avg = tempo_avg
            tempo_change += 1
        
        else:
            tempo_avg = tempo_avg + alfa*(tempo - tempo_avg)
            tempo_change = 0
            
        if tempo_change > 5:
            tempo_avg = tempo_avg + alfa*(tempo - tempo_avg)
            
            
            
        
        data_prev = data
        os.remove(path)
        file += 1
        path = Path('Data/recorded_data_' + str(file) + '.npy')
        
        
        tempo_avg = int(tempo_avg)
        tempo = int(tempo)
        print(tempo_avg, tempo)
    