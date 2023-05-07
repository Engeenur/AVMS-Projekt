import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import tkinter as tk
import pandas as pd
import datetime

string_data = ['2684.27\t23.43\t44.24', '2767.28\t23.45\t44.27', '2701.46\t23.45\t44.27', '2664.67\t23.43\t44.25', '2627.05\t23.42\t44.32', '2614.62\t23.43\t44.32', '2599.03\t23.43\t44.30', '2603.45\t23.42\t44.32', '2608.71\t23.43\t44.29']
t_vec=[]
t = 0

SCD30_data = []
for string in string_data:
    sens_data = string.split()
    #correct the time variable and save new time and data
    t += 1500
    SCD30_data.append(sens_data)
    t_vec.append(t)
    print(datetime.datetime.now())

t_vec = np.array(t_vec).astype('float')
t_vec = np.reshape(t_vec,(t_vec.size, 1))
SCD30_data = np.array(SCD30_data).astype('float')

print(SCD30_data)
print(t_vec)

test = np.hstack((t_vec, SCD30_data))
print(test)