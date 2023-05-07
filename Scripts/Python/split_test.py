import serial
import time
import numpy as np
import matplotlib.pyplot as plt

class Plotter:
    def __init__(self, iSubplots_rows=1, iSubplots_cols=1, iSubplot_w=32, iSubplot_h=18):
        self.fig , self.axs =  plt.subplots(iSubplots_rows,iSubplots_cols)
        #conversion from cm to inches is inches=cm/2.54
        self.fig.set_size_inches(w=iSubplot_w*iSubplots_cols/2.54, h=iSubplot_h*iSubplots_rows/2.54)

    def init_anim_plot(self,iX,iY,iSubplot_num=1,iTitle='', iYlabel='', iXlabel=''):
        self.axs[iSubplot_num-1].plot(iX,iY)
        self.axs[iSubplot_num-1].set_title(iTitle)
        self.axs[iSubplot_num-1].set_xlabel(iXlabel)
        self.axs[iSubplot_num-1].set_ylabel(iYlabel)
        self.fig.show()

        return 
        
    def animate_plot(self, iX, iY, iSample_num, iSubplot_num=1,iTitle='', iYlabel='', iXlabel=''):
        
        self.axs[iSubplot_num-1].clear()
        self.axs[iSubplot_num-1].set_title(iTitle)
        self.axs[iSubplot_num-1].set_xlabel(iXlabel)
        self.axs[iSubplot_num-1].set_ylabel(iYlabel)
        #if length of vectors is lower than sample_num then plot whole vectors
        if len(iX) < iSample_num:
            self.axs[iSubplot_num-1].plot(iX,iY)

        #limit x and y to last sample_num of samples
        X_t = iX[-iSample_num:] 
        Y_t = iY[-iSample_num:]

        self.axs[iSubplot_num-1].plot(X_t,Y_t)
        self.fig.canvas.draw()
        

string_data = ['2684.27\t23.43\t44.24', '2767.28\t23.45\t44.27', '2701.46\t23.45\t44.27', '2664.67\t23.43\t44.25', '2627.05\t23.42\t44.32', '2614.62\t23.43\t44.32', '2599.03\t23.43\t44.30', '2603.45\t23.42\t44.32', '2608.71\t23.43\t44.29']

GraphPlot = Plotter(3,1,iSubplot_h=10,iSubplot_w=15)
GraphPlot.init_anim_plot(0,0,iSubplot_num=1)
#GraphPlot.init_anim_plot(0,0,iSubplot_num=2)
#GraphPlot.init_anim_plot(0,0,iSubplot_num=3)

t_vec=[]
t = 0
plt.ion()

SCD30_data = []
for string in string_data:
    sens_data = string.split()
    #correct the time variable and save new time and data
    t += 1500
    SCD30_data.append(sens_data)
    t_vec.append(t)
    if len(SCD30_data) > 1:
        SCD30_array = np.array(SCD30_data).astype('float')
        print(SCD30_array.shape)
        GraphPlot.animate_plot(t_vec,SCD30_array[:,0],iSample_num=5, iSubplot_num=1)
        #GraphPlot.animate_plot(t_vec,SCD30_array[:,1],iSample_num=5,iSubplot_num=2)
        #GraphPlot.animate_plot(t_vec,SCD30_array[:,2],iSample_num=5,iSubplot_num=3)
        time.sleep(1)
    
    
t_vec = np.array(t_vec).astype('float')
SCD30_data = np.array(SCD30_data).astype('float')
plt.show()
input('Done')



    

        



