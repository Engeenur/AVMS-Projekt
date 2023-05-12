import serial
import time
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg# , NavigationToolbar2Tk
import tkinter as tk
import pandas as pd
import datetime
from git import Repo
from pathlib import Path
import librosa as lr
import os


###########################################################################################################################################################
#------------------------------------------------------------------ GLOBAL VARIABLES ---------------------------------------------------------------------#
###########################################################################################################################################################

# Application settings
APP_NAME = 'AVMS - MERILEC USPEŠNOSTI KONCERTA'
BORDER_WIDTH = 70  # number of pixels that are empty around the border of the app window to account for taskbar position

# Arduino connection settings
COM_PORT = 'COM5'
BAUD_RATE = 115200
TIMEOUT = 2e-5

# Git settings and data
REPOSITORY_PATH = 'C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Meritve'

class Arduino_SCD30():
    def __init__(self, iCom_port, iBaud_rate=115200, iTimeout=4):
        # Create variables for serial communication
        self.baud_rate = iBaud_rate
        self.com_port = iCom_port
        self.timeout = iTimeout
        self.t0 = 0

        # Create data list for measurements
        # Inside list the formatting is [CO2_concentration,Temperature,Relative_humidity] for each element
        self.data = []
        self.time_data = []
        self.timestamps = []

        # create serial connection object
        self.serial = serial.Serial()

    def start_serial(self):
        # Start the serial connection and wait for 2 seconds for it to establish
        self.serial.baudrate = self.baud_rate
        self.serial.port = self.com_port
        self.serial.timeout = self.timeout
        self.serial.open()
        time.sleep(2)
        self.t0 = time.time()

    def read_data(self):
        # read current data on the serial connection 
        # (from the arduino) and unpack it
        line = self.serial.readline()   # read a byte string
        if line:
            # record capture time and timestamp
            self.time_data.append(time.time()-self.t0)
            self.timestamps.append(datetime.datetime.now())
            string = line.decode()  # convert to a unicode string
            new_data = string.split() # split in 3 numbers
            self.data.append(new_data) # log new data

    def close_serial(self):
        self.serial.close()

    def change_sample_time(self):
        pass

class Microphone():
    # TODO: create a usable microphone class, that you can use to get microphone data
    def __init__(self):
        self.data = []
        self.time_data = []
        self.timestamps = []
        self.file_num = 0
        self.mic_file_path = Path('C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt\\Data\\Rec_mic_data\\recorded_data_' + str(self.file_num) + '.npy')
        self.rec_data_path = 'C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt\\Data\\Rec_mic_data'
        self.t0 = 0
        self.mic_controll_path = 'C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt\\Data\\Mic_controll_data'
        self.stop_path = Path(os.path.join(self.mic_controll_path,"STOP.txt"))
        self.start_path = Path(os.path.join(self.mic_controll_path,"START.txt"))

    def start(self):
        # create start file for recording thread and remove stop file
        open(os.path.join(self.mic_controll_path,"START.txt"), "w")
        if self.stop_path.is_file():
            os.remove(self.stop_path)
        # intialize
        self.data = []
        self.time_data = []
        self.timestamps = []
        self.file_num = 0
        self.mic_file_path = Path('C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt\\Data\\Rec_mic_data\\recorded_data_' + str(self.file_num) + '.npy')

    def get_tempo(self, buffer, sample_rate):
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
    
    def read_data(self):
        if self.mic_file_path.is_file():
            if self.file_num == 0:
                # record starting time
                self.t0 = self.mic_file_path.stat().st_mtime
            time_created = self.mic_file_path.stat().st_mtime
            self.time_data.append(time_created-self.t0)
            self.timestamps.append(datetime.datetime.fromtimestamp(time_created))
            data = np.load(self.mic_file_path, allow_pickle=True)
            tempo = self.get_tempo(data, sample_rate=44100)
            self.data.append(tempo)

            #change path for next read and delete current file
            os.remove(self.mic_file_path)
            self.file_num += 1
            self.mic_file_path = Path('C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt\\Data\\Rec_mic_data\\recorded_data_' + str(self.file_num) + '.npy')

    def stop(self):
        # create stop file for recording thread and remove start file
        open(os.path.join(self.mic_controll_path,"STOP.txt"), "x")
        if self.start_path.is_file():
            os.remove(self.start_path)
        # reset file_num and path
        self.file_num = 0
        self.mic_file_path = Path('C:\\Users\\Urban\\Documents\\Fakulteta za elektrotehniko\\BMA 2. Semester\\Avtomatizirani_In_Virtualni_Merilni_Sistemi\\AVMS Projekt\\Data\\Rec_mic_data\\recorded_data_' + str(self.file_num) + '.npy')
    
    def exit(self):
        # clear all leftover files
        for item in os.listdir(self.rec_data_path):
            if item.endswith(".npy"):
                os.remove(os.path.join(self.rec_data_path, item))
        os.remove(self.stop_path)

class Plotter():
    def __init__(self, iTkMaster, iFig_width=5, iFig_height=5, iSubplots_vertical=1, iSubplots_horizontal=1, iDpi=100):
        # create figure for the subplots
        self.fig = Figure(
            figsize=(iFig_width/iDpi, iFig_height/iDpi), dpi=iDpi)
        # create a list of subplots
        self.subplots = []

        # create subplots
        for i in range(iSubplots_vertical*iSubplots_horizontal):
            subplot_pos = int(str(iSubplots_vertical) +
                              str(iSubplots_horizontal) + str(i+1))
            self.subplots.append(self.fig.add_subplot(subplot_pos))

        self.canvas = FigureCanvasTkAgg(self.fig, master=iTkMaster)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack()
        self.canvas.get_tk_widget().place(x=(iFig_width/22), y=-(iFig_height)*0.06)

    def subplot_plot(self, iX, iY, iSampleTime=1.5, iAutoScale=1, iY_offset=0, iYscale=100, iX_lower_limit=0, iXscale=100, iTitle='', iMarker='b-', iSubplot_num=0, iXlabel='', iYlable=''):
        iX = np.array(iX)
        iY = np.array(iY)

        self.subplots[iSubplot_num].clear()
        self.subplots[iSubplot_num].set_title(iTitle)
        self.subplots[iSubplot_num].title.set_size(13)
        self.subplots[iSubplot_num].grid()
        self.subplots[iSubplot_num].set_xlabel(iXlabel)
        self.subplots[iSubplot_num].set_xlim(
            iX_lower_limit, iX_lower_limit+iXscale)
        self.subplots[iSubplot_num].set_ylabel(iYlable)
        if iAutoScale == 0:
            # set scale to specified values only if autoscale not selected
            self.subplots[iSubplot_num].set_ylim(
                iY_offset-iYscale/2, iY_offset+iYscale/2)
        else:
            # if autoscale on, set y scale so that the shown data is maximized
            # calculate idx of the first shown element based on the x scale
            low_idx = int(iX_lower_limit/iSampleTime)
            if low_idx >= 1:
                low_idx -= 1
            low_limit = np.min(iY[low_idx:])
            high_limit = np.max(iY[low_idx:])
            limit_range = high_limit-low_limit
            self.subplots[iSubplot_num].set_ylim(
                low_limit-limit_range*0.05, high_limit+limit_range*0.05)
        self.subplots[iSubplot_num].plot(iX, iY, iMarker)

        self.canvas.draw()


class Application():
    def __init__(self, iApp_name, iArduino_COM_port, iBaud_rate=115200, iTimeout=4, iGit_repository_path=REPOSITORY_PATH):

        self.git_repo_path = iGit_repository_path
        # create root and name it
        self.root = tk.Tk()

        Window_width = self.root.winfo_screenwidth()
        Window_height = self.root.winfo_screenheight() - 20
        #Window_width = 1920
        #Window_height = 1080
        Button_width = int(np.ceil(Window_width/200))
        Button_height = int(np.floor(Window_height/500))
        self.root.title(iApp_name)

        # create main frame of the specified dimensions for all the widgets
        self.main_frame = tk.Frame(
            self.root, width=Window_width, height=Window_height, bg='white')
        self.main_frame.pack()

        ########################################################################################
        # GUI elements

        self.plot_height = (Window_height*7/8/2)
        self.plot_width = (Window_width*10/11/2)
        # create plot canvas and place it on the specified position
        self.plotter = Plotter(iTkMaster=self.main_frame, iFig_width=self.plot_width*2,
                               iFig_height=self.plot_height*2, iSubplots_vertical=2, iSubplots_horizontal=2)

        # create start button
        self.start_button = tk.Button(self.main_frame, text="Start", width=Button_width,
                                      height=Button_height, command=self.start_measurement,
                                      bg='green', fg='white', activebackground='#0be646',
                                      activeforeground='white')
        self.start_button.pack()
        self.start_button.place(
            x=BORDER_WIDTH, y=Window_height-(BORDER_WIDTH + Button_height*10))

        # create stop button
        self.stop_button = tk.Button(self.main_frame, text="Stop", width=Button_width,
                                     height=Button_height, command=self.stop_measurement,
                                     bg='#b30802', fg='white', activebackground='#f50b02',
                                     activeforeground='white')
        self.stop_button.pack()
        self.stop_button.place(x=(BORDER_WIDTH + Button_width*8 + 20),
                               y=Window_height-(BORDER_WIDTH + Button_height*10))
        self.stop_button['state'] = tk.DISABLED

        # create exit button
        self.exit_button = tk.Button(self.main_frame, text="Izhod", width=Button_width,
                                     height=Button_height, command=self.safe_exit)
        self.exit_button.pack()
        self.exit_button.place(x=Window_width-(BORDER_WIDTH + Button_width*8),
                               y=Window_height-(BORDER_WIDTH + Button_height*10))

        # create export button
        self.export_button = tk.Button(self.main_frame, text="Izvozi\npodatke", justify=tk.CENTER,
                                       width=Button_width, height=Button_height, command=self.export_data_popup)
        self.export_button.pack()
        self.export_button.place(x=Window_width-(BORDER_WIDTH + Button_width *
                                 8*2 + 20), y=Window_height-(BORDER_WIDTH + Button_height*10))

        # make time label at the bottom of the graphs
        self.time_label = tk.Label(self.main_frame, text='Čas [s]',
                                   justify=tk.CENTER)
        self.time_label.pack()
        self.time_label.place(
            x=Window_width/2, y=Window_height-self.plot_height*2/7-self.plot_height*0.22)

        # current state logger (disabled entry so it's still a box, but can't be written in)
        self.state_logger = tk.Entry(
            self.main_frame, width=60, font='Arial 15')
        self.state_logger.pack()
        self.state_logger.place(x=BORDER_WIDTH, y=Window_height-150)
        self.state_logger.config(state=tk.DISABLED)
        self.state_logger_label = tk.Label(
            self.main_frame, text='Trenutno stanje:')
        self.state_logger_label.pack()
        self.state_logger_label.place(x=BORDER_WIDTH, y=Window_height-175)

        # end of measurement result display
        self.result_display = tk.Entry(
            self.main_frame, font='Arial 20', width=10)
        self.result_display.pack()
        self.result_display.place(
            x=Window_width-BORDER_WIDTH-153, y=Window_height-150)
        self.result_display.config(state=tk.DISABLED)
        self.result_display_label = tk.Label(
            self.main_frame, text='Rezultat meritve:', font='Arial 15')
        self.result_display_label.pack()
        self.result_display_label.place(
            x=Window_width-BORDER_WIDTH-153, y=Window_height-180)

        ############################################## GRAPH WIDGETS ###################################################
        self.graphs_data_to_plot = []
        self.graphs_data_to_plot_options = [
            'CO2', 'Temp', 'Vlažnost', 'Mikrofon']
        self.graph_time_scale_sliders = []
        self.graph_amp_scale_sliders = []
        self.graph_amp_offs_entries = []
        self.graph_amp_autoscale = []
        self.graph_amp_scale_labels = []
        self.graph_amp_offs_labels = []
        for i in range(len(self.plotter.subplots)):
            x_subplot_idx = i % 2
            y_subplot_idx = i//2
            plot_h = self.plot_height*0.85

            if x_subplot_idx == 0:
                # LEFT TWO SUBPLOTS
                # drop down menu
                clicked = tk.StringVar()
                dropdown = tk.OptionMenu(
                    self.main_frame, clicked, *self.graphs_data_to_plot_options)
                dropdown.pack()
                dropdown.place(x=(BORDER_WIDTH), y=(
                    y_subplot_idx*plot_h + BORDER_WIDTH))
                self.graphs_data_to_plot.append(clicked)

                # time scale slider
                time_scale_slider = tk.Scale(
                    self.main_frame, from_=30, to=180, resolution=10, length=125, orient=tk.HORIZONTAL)
                time_scale_slider.set(60)
                time_scale_slider.pack()
                time_scale_slider.place(x=(BORDER_WIDTH), y=(
                    y_subplot_idx*plot_h + BORDER_WIDTH + 47))
                self.graph_time_scale_sliders.append(time_scale_slider)
                time_scale_label = tk.Label(
                    self.main_frame, text='Časovna skala [s]')
                time_scale_label.pack()
                time_scale_label.place(x=(BORDER_WIDTH), y=(
                    y_subplot_idx*plot_h + BORDER_WIDTH + 32))

                # amplitude scale slider
                amp_scale_slider = tk.Scale(
                    self.main_frame, from_=30, to=180, resolution=10, length=125, orient=tk.HORIZONTAL)
                amp_scale_slider.set(60)
                amp_scale_slider.pack()
                amp_scale_slider.place(x=(BORDER_WIDTH), y=(
                    y_subplot_idx*plot_h + BORDER_WIDTH + 107))
                self.graph_amp_scale_sliders.append(amp_scale_slider)
                amp_scale_label = tk.Label(
                    self.main_frame, text='Amplitudna skala')
                amp_scale_label.pack()
                amp_scale_label.place(x=(BORDER_WIDTH), y=(
                    y_subplot_idx*plot_h + BORDER_WIDTH + 92))
                self.graph_amp_scale_labels.append(amp_scale_label)

                # amplitude offset entry
                amp_offs_slider = tk.Entry(self.main_frame, width=5)
                amp_offs_slider.insert(0, '60')
                amp_offs_slider.pack()
                amp_offs_slider.place(
                    x=(BORDER_WIDTH+90), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 162))
                self.graph_amp_offs_entries.append(amp_offs_slider)
                amp_offs_label = tk.Label(
                    self.main_frame, text='Amplitudni\npremik', justify=tk.LEFT)
                amp_offs_label.pack()
                amp_offs_label.place(x=(BORDER_WIDTH), y=(
                    y_subplot_idx*plot_h + BORDER_WIDTH + 152))
                self.graph_amp_offs_labels.append(amp_offs_label)

                # auto scale amplitude check box
                amp_autoscale_var = tk.IntVar(self.main_frame)
                self.graph_amp_autoscale.append(amp_autoscale_var)
                amp_auto_scale_cehckbox = tk.Checkbutton(
                    self.main_frame, text='Amplituda autoscale', variable=amp_autoscale_var, height=1, width=15)
                amp_auto_scale_cehckbox.pack()
                amp_auto_scale_cehckbox.select()  # check the box
                amp_auto_scale_cehckbox.place(x=(BORDER_WIDTH), y=(
                    y_subplot_idx*plot_h + BORDER_WIDTH + 192))
            else:
                # RIGHT TWO SUBPLOTS
                # drop down menu
                clicked = tk.StringVar()
                dropdown = tk.OptionMenu(
                    self.main_frame, clicked, *self.graphs_data_to_plot_options)
                dropdown.pack()
                dropdown.place(x=(Window_width-BORDER_WIDTH-150),
                               y=(y_subplot_idx*plot_h + BORDER_WIDTH))
                self.graphs_data_to_plot.append(clicked)

                # time scale slider
                time_scale_slider = tk.Scale(
                    self.main_frame, from_=30, to=180, resolution=10, length=125, orient=tk.HORIZONTAL)
                time_scale_slider.set(60)
                time_scale_slider.pack()
                time_scale_slider.place(
                    x=(Window_width-BORDER_WIDTH-150), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 47))
                self.graph_time_scale_sliders.append(time_scale_slider)
                time_scale_label = tk.Label(
                    self.main_frame, text='Časovna skala [s]')
                time_scale_label.pack()
                time_scale_label.place(
                    x=(Window_width-BORDER_WIDTH-150), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 32))

                # amplitude scale slider
                amp_scale_slider = tk.Scale(
                    self.main_frame, from_=30, to=180, resolution=10, length=125, orient=tk.HORIZONTAL)
                amp_scale_slider.set(60)
                amp_scale_slider.pack()
                amp_scale_slider.place(
                    x=(Window_width-BORDER_WIDTH-150), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 107))
                self.graph_amp_scale_sliders.append(amp_scale_slider)
                amp_scale_label = tk.Label(
                    self.main_frame, text='Amplitudna skala')
                amp_scale_label.pack()
                amp_scale_label.place(
                    x=(Window_width-BORDER_WIDTH-150), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 92))
                self.graph_amp_scale_labels.append(amp_scale_label)

                # amplitude offset entry
                amp_offs_slider = tk.Entry(self.main_frame, width=5)
                amp_offs_slider.insert(0, '60')
                amp_offs_slider.pack()
                amp_offs_slider.place(
                    x=(Window_width-BORDER_WIDTH-60), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 162))
                self.graph_amp_offs_entries.append(amp_offs_slider)
                amp_offs_label = tk.Label(
                    self.main_frame, text='Amplitudni\npremik', justify=tk.LEFT)
                amp_offs_label.pack()
                amp_offs_label.place(
                    x=(Window_width-BORDER_WIDTH-150), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 152))
                self.graph_amp_offs_labels.append(amp_offs_label)

                # auto scale amplitude check box
                amp_autoscale_var = tk.IntVar(self.main_frame)
                self.graph_amp_autoscale.append(amp_autoscale_var)
                amp_auto_scale_cehckbox = tk.Checkbutton(
                    self.main_frame, text='Amplituda autoscale', variable=amp_autoscale_var, height=1, width=15)
                amp_auto_scale_cehckbox.pack()
                amp_auto_scale_cehckbox.select()  # check the box
                amp_auto_scale_cehckbox.place(
                    x=(Window_width-BORDER_WIDTH-150), y=(y_subplot_idx*plot_h + BORDER_WIDTH + 192))

        ########################################################################################
        # Measurement elements
        self.SCD30 = Arduino_SCD30(
            iCom_port=iArduino_COM_port, iBaud_rate=iBaud_rate, iTimeout=iTimeout)
        self.Microphone = Microphone()

        ########################################################################################
        # Running time variables (and dirty flags)
        self.running_measurement = False
        self.shutdown = False
        self.exported = True

    def save_file_to_Github(self, file_path, commit_message=''):
        repo = Repo(self.git_repo_path)
        #file_path = REPOSITORY_PATH + '\\' + relative_file_path
        repo.index.add(file_path)
        repo.index.commit(commit_message)
        origin = repo.remote('origin')
        origin.push()

    def result_log(self, result):
        self.result_display.config(state=tk.NORMAL)
        self.result_display.delete(0, 11)
        self.result_display.insert(0, str(result))
        self.result_display.config(state=tk.DISABLED)
        self.root.update()

    def state_log(self, message):
        self.state_logger.config(state=tk.NORMAL)
        self.state_logger.delete(0, 101)
        self.state_logger.insert(0, message)
        self.state_logger.config(state=tk.DISABLED)
        self.root.update()

    def start_measurement(self):
        # update visuals and functionality of buttons
        self.update_buttons('start')
        # clean the sensor data
        self.SCD30.data = []
        self.SCD30.time_data = []
        self.SCD30.timestamps = []
        self.Microphone.start()

        # starting the serial connection if not open already
        if not self.SCD30.serial.is_open:
            self.state_log('Vzpostavljanje povezave s senzorjem SCD30')
            self.SCD30.start_serial()

        self.state_log('Merjenje...')
        # record starting time
        self.t0 = time.time()
        # set the dirty flag for running a measurement and reset it for the exported data
        self.running_measurement = True
        self.exported = False


    def stop_measurement(self):
        # update visuals and functionality of buttons
        self.update_buttons('stop')
        self.state_log('Zaključek meritev')
        # reset the dirty flag for running a measurement
        self.running_measurement = False
        self.Microphone.stop()

    def safe_exit(self):
        # check dirty flag for running a measurement
        if self.running_measurement == False:
            # check with the user if they want to save the measured data into a csv file
            if self.exported == False:
                # inform the user about the not saved data and ask them if they really want to exit
                self.not_exported_popup = tk.Toplevel(self.root)
                self.not_exported_popup.geometry('230x120')
                self.not_exported_popup.title('Neshranjeni podatki')
                info_text = tk.Label(self.not_exported_popup, text='Podatki zadnje meritve niso bili shranjeni.\n\nAli želite shraniti podatke?',
                                     justify=tk.CENTER)
                info_text.pack()
                self.go_to_export_button = tk.Button(self.not_exported_popup, text='Shrani', width=10,
                                                     height=2, command=self.go_to_export)
                self.go_to_export_button.pack()
                self.go_to_export_button.place(x=20, y=70)
                self.cancel_export_button = tk.Button(self.not_exported_popup, text='Izhod', width=10,
                                                      height=2, command=self.ack_not_saved_data_and_exit)
                self.cancel_export_button.pack()
                self.cancel_export_button.place(x=120, y=70)
            else:
                # end the serial connection
                self.SCD30.serial.close()
                # exit the application
                self.exit_app()
        else:
            # make an error popup informing you about a running measurement
            # should not happen because the button is disabled while measuring
            error_popup = tk.Toplevel(self.root)
            error_popup.geometry('230x80')
            error_popup.title('Error')
            tk.Label(error_popup, text='Trenutno se izvaja meritev, zato se aplikacija\nne more zapreti.\n\nUstavite meritev in poskusite ponovno.',
                     justify=tk.CENTER).grid(row=0)

    def ack_not_saved_data_and_exit(self):
        # end the serial connection
        self.SCD30.serial.close()
        # exit the application
        self.exit_app()

    def go_to_export(self):
        # make the export_data_popup and destroy the information about not saved data popup
        self.export_data_popup()
        self.not_exported_popup.destroy()

    def exit_app(self):
        self.Microphone.exit()
        self.root.after(1000, self.root.destroy)
        self.root.update()
        self.shutdown = True

    def export_data_popup(self):
        # make a popup window for exporting data
        self.popup = tk.Toplevel(self.root)
        self.popup.geometry('300x100')
        self.popup.title('Izvozi podatke')
        # make labels for entry fields
        tk.Label(self.popup, text='Pot do mape (absolutna)').grid(row=0)
        tk.Label(self.popup, text='Ime shranjene datoteke').grid(row=1)
        # make entry fields
        self.path_entry = tk.Entry(self.popup)
        self.filename_entry = tk.Entry(self.popup)
        self.path_entry.grid(row=0, column=1)
        self.filename_entry.grid(row=1, column=1)
        # make buttons to confirm saving the data and canceling
        self.cancel_button = tk.Button(self.popup, text='Prekliči', width=10,
                                       height=2, command=self.cancel_export).grid(row=2, column=1)
        self.save_button = tk.Button(self.popup, text='Shrani', width=10,
                                     height=2, command=self.save_data).grid(row=2, column=0)

    def cancel_export(self):
        # close the popup window
        self.popup.destroy()

    def save_data(self):
        # get the inputted path and name of file
        path = self.path_entry.get()
        filename = self.filename_entry.get()
        if path[-1] == '\\':
            filepath = path + filename
        else:
            filepath = path + '\\' + filename
        # convert sensory and time data into a pandas dataframe and save it as a csv to the filepath
        sensory_data = np.array(self.SCD30.data).astype('float').round(2)
        # .astype('float').round(2)
        time_data = np.array(self.SCD30.timestamps)
        time_data = np.reshape(time_data, (time_data.size, 1))
        data_DF = pd.DataFrame(np.hstack((time_data, sensory_data)))
        try:
            # save data locally to a csv
            data_DF.to_csv(filepath, header=['time stamp [date h:m:s]', 'CO2 concentration [ppm]', 'Temperature [°C]', 'Relative humidity [%]'],
                           index=False)
            commit_message = 'meritve dne: ' + \
                str(datetime.datetime.now().date())
            self.save_file_to_Github(filepath, commit_message=commit_message)
            # set the dirty flag for data being exported
            self.exported = True
        except OSError:
            # invalid entries for path or filename
            # make another popup telling you to try exporting again
            error_popup = tk.Toplevel(self.root)
            error_popup.geometry('230x80')
            error_popup.title('Error')
            tk.Label(error_popup, text='Napačen vnos poti do mape shranjevanja\nali imena datoteke.\n\nPoskusite ponovno.',
                     justify=tk.CENTER).grid(row=0)

        self.popup.destroy()

    def update_buttons(self, button_pressed):
        if button_pressed == 'start':
            # start button was pressed -> make it green to indicate running measurement and disable all buttons except stop
            self.stop_button.configure(state=tk.NORMAL)
            self.start_button.configure(state=tk.DISABLED)
            self.exit_button.configure(state=tk.DISABLED)
            self.export_button.configure(state=tk.DISABLED)
            self.start_button.config(bg='#0be646', fg='white')
        elif button_pressed == 'stop':
            # enable start and exit buttons and disable the stop button, also return start button to normal
            self.stop_button.configure(state=tk.DISABLED)
            self.start_button.configure(state=tk.NORMAL)
            self.exit_button.configure(state=tk.NORMAL)
            self.export_button.configure(state=tk.NORMAL)
            self.start_button.config(bg='green', fg='white')

    def mainloop(self):
        while not self.shutdown:
            if self.running_measurement == True:
                # read the data from the sensor and convert it to an numpy array
                self.SCD30.read_data()
                self.Microphone.read_data()

            y_data = np.array(self.SCD30.data).astype('float')
            x_data = np.array(self.SCD30.time_data).astype('float').round(2)
            mic_data = np.array(self.Microphone.data).astype('float')
            mic_time_data = np.array(self.Microphone.time_data).astype('float')

            # plot the last NUM_OF_SAMPLES readings
            if x_data.size > 1:
                # plot each graph with the desired data
                for i in range(len(self.plotter.subplots)):
                    # calculate correct time and amplitude scale values
                    if self.graph_amp_offs_entries[i].get() != '':
                        # if the entry box is not empty convert the input to float
                        amp_offs = float(self.graph_amp_offs_entries[i].get())
                    else:
                        # else set the offset to 0
                        amp_offs = 0
                    amp_scale = float(self.graph_amp_scale_sliders[i].get())
                    autoscale = self.graph_amp_autoscale[i].get()
                    time_scale = float(self.graph_time_scale_sliders[i].get())
                    if x_data[-1] > time_scale:
                        time0 = x_data[-1] - time_scale
                    else:
                        time0 = 0
                    # calculate average sample time in last 60 samples (or all samples if there are less)
                    if x_data.size < 60:
                        sample_time = np.sum(
                            x_data)/np.sum(np.arange(1, x_data.size+1))
                    else:
                        sample_time = (x_data[-1] - x_data[-60])/59

                    # print(sample_time)

                    if self.graphs_data_to_plot[i].get() == self.graphs_data_to_plot_options[0]:
                        # plot CO2 data
                        self.plotter.subplot_plot(x_data, y_data[:, 0].round(2), iX_lower_limit=time0, iXscale=time_scale,
                                                  iY_offset=amp_offs, iYscale=amp_scale, iAutoScale=autoscale, iSampleTime=sample_time,
                                                  iSubplot_num=i, iTitle='Koncentracija CO2', iYlable='CO2 [ppm]')
                        # change slider steps and edge values depending on what you are plotting
                        self.graph_amp_scale_sliders[i].configure(
                            from_=50, to=200)
                        self.graph_amp_scale_labels[i].configure(
                            text='Amplitudna skala [ppm]')
                        self.graph_amp_offs_labels[i].configure(
                            text='Amplitudni\npremik [ppm]')
                    elif self.graphs_data_to_plot[i].get() == self.graphs_data_to_plot_options[1]:
                        # plot Temperature data
                        self.plotter.subplot_plot(x_data, y_data[:, 1].round(2), iX_lower_limit=time0, iXscale=time_scale,
                                                  iY_offset=amp_offs, iYscale=amp_scale, iAutoScale=autoscale, iSampleTime=sample_time,
                                                  iSubplot_num=i, iTitle='Temperatura', iYlable='T [°C]')
                        # change slider steps and edge values depending on what you are plotting
                        self.graph_amp_scale_sliders[i].configure(
                            from_=1, to=50, resolution=1)
                        self.graph_amp_scale_labels[i].configure(
                            text='Amplitudna skala [°C]')
                        self.graph_amp_offs_labels[i].configure(
                            text='Amplitudni\npremik [°C]')
                    elif self.graphs_data_to_plot[i].get() == self.graphs_data_to_plot_options[2]:
                        # plot Humidity data
                        self.plotter.subplot_plot(x_data, y_data[:, 2].round(1), iX_lower_limit=time0, iXscale=time_scale,
                                                  iY_offset=amp_offs, iYscale=amp_scale, iAutoScale=autoscale, iSampleTime=sample_time,
                                                  iSubplot_num=i, iTitle='Relativna vlažnost', iYlable='H [%]')
                        # change slider steps and edge values depending on what you are plotting
                        self.graph_amp_scale_sliders[i].configure(
                            from_=1, to=50, resolution=1)
                        self.graph_amp_scale_labels[i].configure(
                            text='Amplitudna skala [%]')
                        self.graph_amp_offs_labels[i].configure(
                            text='Amplitudni\npremik [%]')
                    elif (self.graphs_data_to_plot[i].get() == self.graphs_data_to_plot_options[3]) and mic_data:
                        # plot Microphone data if there is any
                        self.plotter.subplot_plot(mic_time_data, mic_data, iX_lower_limit=time0, iXscale=time_scale,
                                                  iY_offset=amp_offs, iYscale=amp_scale, iAutoScale=autoscale, iSampleTime=sample_time,
                                                  iSubplot_num=i, iTitle='Tempo', iYlable='Tempo [bpm]')
                        # change slider steps and edge values depending on what you are plotting
                        self.graph_amp_scale_sliders[i].configure(
                            from_=1, to=50, resolution=1)
                        self.graph_amp_scale_labels[i].configure(
                            text='Amplitudna skala [bpm]')
                        self.graph_amp_offs_labels[i].configure(
                            text='Amplitudni\npremik [bpm]')

            # print measurement result
            # TODO: apply the formula for the result
            self.result = 'TODO eq.'
            self.result_log(self.result)

            self.root.update()


if __name__ == '__main__':

    app = Application(iApp_name=APP_NAME, iArduino_COM_port=COM_PORT,
                      iBaud_rate=BAUD_RATE, iTimeout=TIMEOUT)
    app.mainloop()
