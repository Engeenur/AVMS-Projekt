import serial
import time
import numpy as np
import matplotlib.pyplot as plt

COM_PORT = 'COM5'
BAUD_RATE = 115200
ser = serial.Serial(COM_PORT, BAUD_RATE, timeout=4)
time.sleep(2)

SCD30_data = []
for i in range(10):
    line = ser.readline()   # read a byte string
    if line and i>0:
        string = line.decode()  # convert the byte string to a unicode string
        sens_data = string.split()
        SCD30_data.append(sens_data)
ser.close()

SCD30_data = np.array(SCD30_data)
# unpack data
# first element is always firmware version major and minor
# after that the data is structured as CO2\tTemp\tHumidity
# string_data = ['co2Concentration: 2790.25\ttemperature: 23.22\thumidity: 45.03\r\n', 'co2Concentration: 2865.87\ttemperature: 23.21\thumidity: 45.02\r\n', 'co2Concentration: 2820.39\ttemperature: 23.21\thumidity: 45.03\r\n', 'co2Concentration: 2756.64\ttemperature: 23.23\thumidity: 45.07\r\n', 'co2Concentration: 2786.45\ttemperature: 23.21\thumidity: 45.06\r\n', 'co2Concentration: 2749.64\ttemperature: 23.19\thumidity: 45.02\r\n', 'co2Concentration: 2727.25\ttemperature: 23.19\thumidity: 45.07\r\n', 'co2Concentration: 2714.52\ttemperature: 23.19\thumidity: 45.07\r\n', 'co2Concentration: 2705.67\ttemperature: 23.19\thumidity: 45.05\r\n', 'co2Concentration: 2688.69\ttemperature: 23.21\thumidity: 45.04\r\n', 'co2Concentration: 2680.52\ttemperature: 23.21\thumidity: 45.00\r\n', 'co2Concentration: 2672.63\ttemperature: 23.22\thumidity: 45.05\r\n', 'co2Concentration: 2671.06\ttemperature: 23.19\thumidity: 45.01\r\n', 'co2Concentration: 2669.76\ttemperature: 23.22\thumidity: 45.03\r\n', 'co2Concentration: 2665.95\ttemperature: 23.22\thumidity: 45.02\r\n']
# string_data = np.array(string_data)
# CO2_data = string_data[:].split()

# fig, (ax1,ax2,ax3) = plt.subplots(1,3)



# plt.plot(data)
# plt.xlabel('Time')
# plt.ylabel('Temp, CO2 & humidity reading')
# plt.title('Temp, CO2 & humidity reading vs. Time')
# plt.show()
