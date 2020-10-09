from tkinter import *
from tkinter import ttk
import seaborn as sns
import threading
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.font_manager import FontProperties
fontP = FontProperties()
fontP.set_size('small')
sns.set()


EDMONTON_TEMP = pd.read_csv("Edmonton Year Long Temperature.csv")
MONTH_DICT = {'January': "01",
              'February': "02",
              'March': "03",
              'April': "04",
              'May': "05",
              'June': "06",
              'July': "07",
              'August': "08",
              'September': "09",
              'October': "10",
              'November': "11",
              'December': "12"}


# Date is a list in the form [Year, Month, Day, Hhour]
def convert_date(date):
    year, month, day, hour = date
    cvt_month = MONTH_DICT[month]
    cvt_day = str(day).zfill(2)
    cvt_hour = str(hour).zfill(2)
    return str(year) + "-" + cvt_month + "-" + cvt_day + " " + cvt_hour + ":00:00 MDT"


def get_date_index(date):
    cvt_date = convert_date(date)
    index = EDMONTON_TEMP.index
    condition = EDMONTON_TEMP["Date"] == cvt_date
    return index[condition].tolist()[0]


class Root(Tk):
    def __init__(self):
        global progress_bar_value, progress_bar_text, update_plot, is_thread_running, cancel_calibrate, cancel_sim
        super(Root, self).__init__()
        self.title("Temperature Simulator")
        self.minsize(800, 675)

        update_plot = True
        is_thread_running = False
        cancel_calibrate = False
        cancel_sim = False
        self.fig = plt.figure(figsize=(8, 6), dpi=100)
        self.canvas = FigureCanvasTkAgg(figure=self.fig, master=self)
        self.canvas.get_tk_widget().grid(column=1,
                                         columnspan=2,
                                         row=2,
                                         rowspan=5,
                                         padx=20,
                                         pady=20)
        self.toolbar = NavigationToolbar2Tk(self.canvas, self, pack_toolbar=False)
        self.toolbar.update()
        self.toolbar.grid(column=2,
                          columnspan=1,
                          row=6)

        # User Selected Variables
        self.K = StringVar()
        self.K.set(30)
        self.tau = StringVar()
        self.tau.set(3600)
        self.step_size = StringVar()
        self.step_size.set(1)
        self.initial_temp = StringVar()
        self.initial_temp.set(20)
        self.start_year = StringVar()
        self.start_year.set(2019)
        self.end_year = StringVar()
        self.end_year.set(2020)
        self.start_month = StringVar()
        self.start_month.set("October")
        self.end_month = StringVar()
        self.end_month.set("October")
        self.start_day = StringVar()
        self.start_day.set(6)
        self.end_day = StringVar()
        self.end_day.set(5)
        self.start_hour = StringVar()
        self.start_hour.set(0)
        self.end_hour = StringVar()
        self.end_hour.set(23)
        self.num_sensors = StringVar()
        self.num_sensors.set(5)
        self.measure_freq = StringVar()
        self.measure_freq.set(15)
        self.use_weighted_mean = BooleanVar()
        self.use_weighted_mean.set(False)
        self.P = StringVar()
        self.P.set(1)
        self.I = StringVar()
        self.I.set(0)
        self.D = StringVar()
        self.D.set(0)
        self.control_freq = StringVar()
        self.control_freq.set(60)
        self.ref = StringVar()
        self.ref.set("20,15,20")
        self.plot_room = BooleanVar()
        self.plot_room.set(True)
        self.plot_outside = BooleanVar()
        self.plot_outside.set(False)
        self.plot_ref = BooleanVar()
        self.plot_ref.set(True)
        self.plot_measure = BooleanVar()
        self.plot_measure.set(False)
        self.status = StringVar()
        self.status.set("None")
        self.csv_path = StringVar()
        self.csv_path.set("Temperature_Data.csv")
        progress_bar_value = 0
        progress_bar_text = ""

        self.time = [1]
        self.r_temp = [0]
        self.o_temp = [0]
        self.ref_temp = [0]
        self.m_temp = [0]
        self.u = [0]

        # Simulation Parameters Frame
        self.sim_parameter_frame = ttk.LabelFrame(self,
                                                  text="Sim Parameters")
        self.sim_parameter_frame.grid(column=0,
                                      row=0,
                                      rowspan=2,
                                      padx=20,
                                      pady=20)
        self.populate_sim_parameter_frame()

        # Date and Time Frame
        self.date_frame = ttk.LabelFrame(self,
                                         text="Date and Time [Year, Month, Day, Hour]")
        self.date_frame.grid(column=1,
                             row=0,
                             padx=20,
                             pady=10)
        self.populate_data_frame()

        # Run Simulation
        self.run_sim_button = Button(self,
                                     text="Run Simulation",
                                     command=self.run_sim)
        self.run_sim_button.grid(column=0,
                                 row=2,
                                 padx=20,
                                 pady=20)
        self.is_run_sim_button_cancel = False

        # Calibrate P, I, D
        self.calibrate_button = Button(self,
                                       text="Calibrate",
                                       command=self.calibrate)
        self.calibrate_button.grid(column=0,
                                   row=3,
                                   padx=20,
                                   pady=20)
        self.is_calibrate_button_cancel = False

        # Save Data to .csv File
        self.csv_button = Button(self,
                                 text="Save Data",
                                 command=self.save_data)
        self.csv_button.grid(column=0,
                             row=5,
                             padx=20,
                             pady=20)

        # Sensor Parameters
        self.sensor_frame = ttk.LabelFrame(self,
                                           text="Sensor Parameters")
        self.sensor_frame.grid(column=1,
                               row=1,
                               padx=20,
                               pady=10)
        self.populate_sensor_frame()

        # Control Parameters
        self.control_frame = ttk.LabelFrame(self,
                                            text="Control Parameters")
        self.control_frame.grid(column=2,
                                row=0,
                                rowspan=2,
                                padx=20,
                                pady=20)
        self.populate_control_frame()

        # Status Selection
        self.status_frame = ttk.LabelFrame(self,
                                           text="Sensor Status")
        self.status_frame.grid(column=0,
                               row=4)
        self.status_menu = OptionMenu(self.status_frame,
                                      self.status,
                                      *["None", "Short", "Faulty Connection", "Overheated"])
        self.status_menu.grid(column=0,
                              row=0)

        # Plot Parameters
        self.plot_frame = ttk.LabelFrame(self,
                                         text='Plot')
        self.plot_frame.grid(column=0,
                             row=6,
                             padx=20,
                             pady=20)

        self.populate_plot_frame()

        self.progress_bar = ttk.Progressbar(self,
                                            orient=HORIZONTAL,
                                            length=500,
                                            mode='determinate')
        self.progress_bar.grid(column=1,
                               columnspan=2,
                               row=8)
        self.progress_bar['value'] = progress_bar_value
        self.progress_bar_label = Label(self)
        self.progress_bar_label['text'] = progress_bar_text
        self.progress_bar_label.grid(column=1,
                                     columnspan=2,
                                     row=7)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)


    def populate_sim_parameter_frame(self):
        self.K_label = Label(self.sim_parameter_frame,
                             text="K [°C]")
        self.K_label.grid(column=0,
                          row=0,
                          padx=5,
                          pady=5)
        self.K_entry = Entry(self.sim_parameter_frame,
                             textvariable=self.K,
                             width=10,
                             justify="center")
        self.K_entry.grid(column=1,
                          row=0)

        self.tau_label = Label(self.sim_parameter_frame,
                               text="τ [s]")
        self.tau_label.grid(column=0,
                            row=1,
                            padx=5,
                            pady=5)
        self.tau_entry = Entry(self.sim_parameter_frame,
                               textvariable=self.tau,
                               width=10,
                               justify="center")
        self.tau_entry.grid(column=1,
                            row=1)

        self.step_size_label = Label(self.sim_parameter_frame,
                                     text="step size [s]")
        self.step_size_label.grid(column=0,
                                  row=2,
                                  padx=5,
                                  pady=5)
        self.step_size_entry = Entry(self.sim_parameter_frame,
                                     textvariable=self.step_size,
                                     width=10,
                                     justify="center")
        self.step_size_entry.grid(column=1,
                                  row=2)

        self.initial_temp_label = Label(self.sim_parameter_frame,
                                        text="initial temperature [°C]")
        self.initial_temp_label.grid(column=0,
                                     row=3,
                                     padx=5,
                                     pady=5)
        self.initial_temp_entry = Entry(self.sim_parameter_frame,
                                        textvariable=self.initial_temp,
                                        width=10,
                                        justify="center")
        self.initial_temp_entry.grid(column=1,
                                     row=3)

    def populate_data_frame(self):
        self.start_date_label = Label(self.date_frame,
                                      text="start")
        self.start_date_label.grid(column=0,
                                   row=0,
                                   padx=5,
                                   pady=5)

        self.end_date_label = Label(self.date_frame,
                                    text="end")
        self.end_date_label.grid(column=0,
                                 row=1,
                                 padx=5,
                                 pady=5)

        self.start_year_menu = OptionMenu(self.date_frame,
                                          self.start_year,
                                          *[2019, 2020])
        self.start_year_menu.grid(column=1,
                                  row=0)

        self.end_year_menu = OptionMenu(self.date_frame,
                                        self.end_year,
                                        *[2019, 2020])
        self.end_year_menu.grid(column=1,
                                row=1)

        self.start_month_menu = OptionMenu(self.date_frame,
                                           self.start_month,
                                           *["January", "February", "March", "April", "May", "June",
                                             "July", "August", "September", "October", "November",
                                             "December"])
        self.start_month_menu.grid(column=2,
                                   row=0)

        self.end_month_menu = OptionMenu(self.date_frame,
                                         self.end_month,
                                         *["January", "February", "March", "April", "May", "June",
                                           "July", "August", "September", "October", "November",
                                           "December"])
        self.end_month_menu.grid(column=2,
                                 row=1)

        self.start_day_entry = Entry(self.date_frame,
                                     textvariable=self.start_day,
                                     width=4,
                                     justify="center")
        self.start_day_entry.grid(column=3,
                                  row=0)

        self.end_day_entry = Entry(self.date_frame,
                                   textvariable=self.end_day,
                                   width=4,
                                   justify="center")
        self.end_day_entry.grid(column=3,
                                row=1)

        self.start_hour_entry = Entry(self.date_frame,
                                      textvariable=self.start_hour,
                                      width=4,
                                      justify="center")
        self.start_hour_entry.grid(column=4,
                                   row=0)

        self.end_hour_entry = Entry(self.date_frame,
                                    textvariable=self.end_hour,
                                    width=4,
                                    justify="center")
        self.end_hour_entry.grid(column=4,
                                 row=1)

    def populate_sensor_frame(self):
        self.num_sensor_label = Label(self.sensor_frame,
                                      text="number of sensors")
        self.num_sensor_label.grid(column=0,
                                   row=0,
                                   padx=5,
                                   pady=5)
        self.num_sensor_entry = Entry(self.sensor_frame,
                                      textvariable=self.num_sensors,
                                      width=10,
                                      justify="center")
        self.num_sensor_entry.grid(column=1,
                                   row=0)

        self.measure_freq_label = Label(self.sensor_frame,
                                        text="measurement frequency [s]")
        self.measure_freq_label.grid(column=0,
                                     row=1,
                                     padx=5,
                                     pady=5)
        self.measure_freq_entry = Entry(self.sensor_frame,
                                        textvariable=self.measure_freq,
                                        width=10,
                                        justify="center")
        self.measure_freq_entry.grid(column=1,
                                     row=1)

        self.weighted_mean_check = Checkbutton(self.sensor_frame,
                                               text="use weighted mean",
                                               variable=self.use_weighted_mean)
        self.weighted_mean_check.grid(column=0,
                                      columnspan=2,
                                      row=2)

    def populate_control_frame(self):
        self.P_label = Label(self.control_frame,
                             text="P")
        self.P_label.grid(column=0,
                          row=0,
                          padx=5,
                          pady=5)
        self.P_entry = Entry(self.control_frame,
                             textvariable=self.P,
                             width=10,
                             justify="center")
        self.P_entry.grid(column=1,
                          row=0)

        self.I_label = Label(self.control_frame,
                             text="I")
        self.I_label.grid(column=0,
                          row=1,
                          padx=5,
                          pady=5)
        self.I_entry = Entry(self.control_frame,
                             textvariable=self.I,
                             width=10,
                             justify="center")
        self.I_entry.grid(column=1,
                          row=1)

        self.D_label = Label(self.control_frame,
                             text="D")
        self.D_label.grid(column=0,
                          row=2,
                          padx=5,
                          pady=5)
        self.D_entry = Entry(self.control_frame,
                             textvariable=self.D,
                             width=10,
                             justify="center")
        self.D_entry.grid(column=1,
                          row=2)

        self.control_freq_label = Label(self.control_frame,
                                        text="control frequency [s]")
        self.control_freq_label.grid(column=0,
                                     row=3,
                                     padx=5,
                                     pady=5)
        self.control_freq_entry = Entry(self.control_frame,
                                        textvariable=self.control_freq,
                                        width=10,
                                        justify="center")
        self.control_freq_entry.grid(column=1,
                                     row=3)

        self.ref_label = Label(self.control_frame,
                               text="reference temperature [°C]")
        self.ref_label.grid(column=0,
                            row=4,
                            padx=5,
                            pady=5)
        self.ref_entry = Entry(self.control_frame,
                               textvariable=self.ref,
                               width=10,
                               justify="center")
        self.ref_entry.grid(column=1,
                            row=4)

    def populate_plot_frame(self):
        self.room_check = Checkbutton(self.plot_frame,
                                      text="room",
                                      variable=self.plot_room)
        self.room_check.grid(column=0,
                             columnspan=2,
                             row=0)
        self.outside_check = Checkbutton(self.plot_frame,
                                         text="outside",
                                         variable=self.plot_outside)
        self.outside_check.grid(column=0,
                                columnspan=2,
                                row=2)
        self.ref_check = Checkbutton(self.plot_frame,
                                      text="reference",
                                      variable=self.plot_ref)
        self.ref_check.grid(column=0,
                            columnspan=2,
                            row=1)
        self.measure_check = Checkbutton(self.plot_frame,
                                         text="measured",
                                         variable=self.plot_measure)
        self.measure_check.grid(column=0,
                                columnspan=2,
                                row=3)
        self.csv_label = Label(self.plot_frame,
                               text="save data path")
        self.csv_label.grid(column=0,
                            row=5)
        self.csv_entry = Entry(self.plot_frame,
                               textvariable=self.csv_path,
                               width=25,
                               justify="center")
        self.csv_entry.grid(column=1,
                            row=5)

    def run_sim(self):
        global is_thread_running, cancel_sim
        if self.is_run_sim_button_cancel:
            cancel_sim = True
        elif not is_thread_running:
            start_date = [int(self.start_year.get()), self.start_month.get(),
                          int(self.start_day.get()), int(self.start_hour.get())]
            end_date = [int(self.end_year.get()), self.end_month.get(),
                        int(self.end_day.get()), int(self.end_hour.get())]

            ref_str = self.ref.get().split(",")
            ref = [float(i) for i in ref_str]

            sim = Simulation(start_date=start_date, end_date=end_date,
                             K=float(self.K.get()), tau=float(self.tau.get()),
                             step_size=float(self.step_size.get()),
                             P=float(self.P.get()), I=float(self.I.get()),
                             D=float(self.D.get()), ref=ref,
                             use_weighted_mean=self.use_weighted_mean.get(),
                             status=self.status.get())
            t = threading.Thread(target=self.run_sim_thread,
                             args=(sim,
                                   float(self.initial_temp.get()),
                                   int(self.measure_freq.get()),
                                   int(self.control_freq.get()),),
                             daemon=True)
            t.start()

    def run_sim_thread(self, sim, initial_temp, measure_freq, control_freq):
        global update_plot, is_thread_running, cancel_sim
        is_thread_running = True
        self.run_sim_button['text'] = "Cancel"
        self.is_run_sim_button_cancel = True

        self.time, self.r_temp, self.o_temp, self.ref_temp, \
        self.m_temp, self.u = sim.run_sim(initial_temp=initial_temp,
                                          measure_freq=measure_freq,
                                          control_freq=control_freq)

        self.run_sim_button['text'] = "Run Simulation"
        self.is_run_sim_button_cancel = False
        is_thread_running = False
        cancel_sim = False
        update_plot = True

    def calibrate(self):
        global is_thread_running, cancel_calibrate
        if self.is_calibrate_button_cancel:
            cancel_calibrate = True
        elif not is_thread_running:
            sim = Simulation(K=float(self.K.get()), tau=float(self.tau.get()),
                             step_size=float(self.step_size.get()),
                             P=float(self.P.get()), I=float(self.I.get()),
                             D=float(self.D.get()))
            t = threading.Thread(target=self.calibrate_thread,
                                 args=(sim, int(self.control_freq.get()),),
                                 daemon=True)
            t.start()

    def calibrate_thread(self, sim, control_freq):
        global is_thread_running, cancel_calibrate
        is_thread_running = True
        self.calibrate_button['text'] = "Cancel"
        self.is_calibrate_button_cancel = True

        pid = sim.calibrate(control_freq)
        self.P.set(round(pid[0], 6))
        self.I.set(round(pid[1], 6))
        self.D.set(round(pid[2], 6))

        self.calibrate_button['text'] = "Calibrate"
        self.is_calibrate_button_cancel = False
        is_thread_running = False
        cancel_calibrate = False


    def plot_data(self, time, temp, b_temp, r_temp, m_temp):
        global update_plot
        plt.cla()
        if self.plot_outside.get():
            plt.plot(time, b_temp, 'k', label='Outside', linestyle='--')
        if self.plot_ref.get():
            plt.plot(time, r_temp, 'r', label='Reference', linewidth=2, linestyle=':')
        if self.plot_measure.get():
            plt.plot(time, m_temp, 'g', label='Measured', linewidth=0.75, linestyle='-.')
        if self.plot_room.get():
            plt.plot(time, temp, 'b', label='Room', linewidth=0.5)
        plt.xlim(0, time[-1])
        plt.xlabel('Time [h]')
        plt.ylabel('Temperature [°C]')
        plt.legend(bbox_to_anchor=(0.5, 1.1), loc='upper center', ncol=4, prop=fontP)
        self.canvas.draw()
        update_plot = False

    def save_data(self):
        data_dict = {
            'Time [h]': self.time,
            'Room Temperature [°C]': self.r_temp,
            'Reference Temperature [°C]': self.ref_temp,
            'Outside Temperature [°C]': self.o_temp,
            'Measured Temperature [°C]': self.m_temp,
            'Heater State [On/Off]': self.u
        }
        df = pd.DataFrame(data_dict)
        df.to_csv(self.csv_path.get(), index=False)

    def update_ui(self):
        global progress_bar_value, progress_bar_text, update_plot
        self.progress_bar['value'] = progress_bar_value
        self.progress_bar_label['text'] = progress_bar_text
        if update_plot:
            self.plot_data(self.time, self.r_temp, self.o_temp, self.ref_temp, self.m_temp)
        root.after(100, self.update_ui)


class Simulation:
    def __init__(self, start_date=None, end_date=None, num_sensors=5, K=25, tau=15,
                 step_size=15, use_weighted_mean=False, P=1, I=0, D=0, ref=None, status="None"):

        # Simulation Parameters
        self.K = K
        self.tau = tau
        self.step_size = step_size
        self.heater = 0

        # Control Parameters
        self.P = P
        self.I = I
        self.D = D
        if ref is None:
            self.ref = [20]
        else:
            self.ref = ref

        # Ambient Temperature
        if start_date is None:
            start_date = [2019, 'October', 6, 0]
        if end_date is None:
            end_date = [2020, 'October', 5, 23]
        start_index = get_date_index(start_date)
        end_index = get_date_index(end_date)
        self.ambient_temp = np.flip(EDMONTON_TEMP["Temperature"].to_numpy()[end_index : start_index + 1])

        # Sensor Array Setup
        self.num_sensors = num_sensors
        self.use_weighted_mean = use_weighted_mean
        self.status = status

    def get_background_temp(self, t):
        floor_idx = np.floor(t).astype(int)
        ceil_idx = np.ceil(t).astype(int)
        fraction = (t - floor_idx) * (self.ambient_temp[ceil_idx] - self.ambient_temp[floor_idx])
        return self.ambient_temp[floor_idx] + fraction

    def update_temp(self, temp, background_temp):
        d_temp = self.step_size * (-temp + self.K * self.heater + background_temp) / self.tau
        return temp + d_temp

    def measure_temp(self, temp):
        # The TMP116 sensors have an accuracy of +-0.2°C
        measurements = np.random.normal(temp, 0.2, self.num_sensors)
        if self.status == "Short":
            measurements[0] = 0
        elif self.status == "Faulty Connection" and np.random.random() < 0.5:
            measurements[0] = measurements[0] + 5 * np.random.random()
        elif self.status == "Overheated":
            measurements[0] = measurements[0] + np.random.normal(5, 1)
        if self.use_weighted_mean and len(measurements) > 1:
            weights = []
            for i in range(len(measurements)):
                weight = 0
                for j in range(len(measurements)):
                    if i != j:
                        weight += abs(measurements[i] - measurements[j])
                weights.append(weight ** -2)
            weights = np.array(weights) / np.sum(weights)
            m_temp = np.sum(weights * measurements)
        else:
            m_temp = np.mean(measurements)
        self.temp_buffer.append(m_temp)

    def control(self, ref):
        self.m_temp = np.mean(self.temp_buffer)
        err = ref - self.m_temp
        self.int_err += err * self.control_freq
        der_err = (err - self.past_err) / self.control_freq
        g = self.P * err + self.I * self.int_err + self.D * der_err
        u = np.clip(g, 0, 1)

        if u > 0.5:
            self.heater = 1
        else:
            self.heater = 0

        self.past_err = err
        self.temp_buffer = []

    def run_sim(self, initial_temp, measure_freq, control_freq):
        global progress_bar_value, progress_bar_text, cancel_sim
        progress_bar_text = "Simulating..."
        progress_bar_value = 0

        time = []
        outside_temperature = []
        room_temperature = []
        reference_temperature = []
        measured_temperature = []
        heater_state = []

        temp = initial_temp
        self.m_temp = initial_temp

        self.control_freq = control_freq
        self.temp_buffer = []
        self.int_err = 0
        self.past_err = 0

        step_range = int(3600 / self.step_size)
        sim_len = step_range * (len(self.ambient_temp) - 1) + 1
        ref_freq = int(np.ceil(sim_len / len(self.ref)))
        r_idx = 0
        ref = self.ref[r_idx]

        for s in range(sim_len):
            t = s / step_range

            background_temp = self.get_background_temp(t)
            temp = self.update_temp(temp, background_temp)

            if s % measure_freq == 0:
                self.measure_temp(temp)
            if s % control_freq == 0:
                self.control(ref)
            if s % ref_freq == 0 and s != 0:
                r_idx += 1
                ref = self.ref[r_idx]

            time.append(t)
            room_temperature.append(temp)
            outside_temperature.append(background_temp)
            reference_temperature.append(ref)
            measured_temperature.append(self.m_temp)
            heater_state.append(self.heater)
            progress_bar_value = int(100 * (s + 1) / sim_len)
            if s % sim_len / 4 == 0:
                print("")
            if cancel_sim:
                break
        progress_bar_value = 0
        progress_bar_text = ""
        return time, room_temperature, outside_temperature, reference_temperature, \
               measured_temperature, heater_state

    def calibrate(self, control_freq):
        global progress_bar_value, progress_bar_text, cancel_calibrate
        progress_bar_text = "Calibrating..."
        progress_bar_value = 0

        pid = np.array([1.0, 0.0, 0.0])
        best_pid = pid
        smallest_err = np.inf

        ref = 20
        itau = 1 / self.tau
        sim_len = 4
        outside_temp = 10

        for i in range(100):
            temp = 15
            u = 0

            int_err = 0
            past_err = 0
            tracking_err = 0

            grads = np.array([0.0, 0.0, 0.0])
            grad_sum = 0
            past_grad = 0
            err_grads = np.array([0.0, 0.0, 0.0])

            P_du = 0
            I_du = 0
            D_du = 0

            for t in range(sim_len * int(self.tau)):

                # Controller
                if t % control_freq == 0:
                    err = ref - temp
                    int_err += err * control_freq
                    der_err = (err - past_err) / control_freq
                    g = pid[0] * err + pid[1] * int_err + pid[2] * der_err
                    past_err = err
                    u = np.clip(g, 0, 1)

                    grad_sum += grads[1]
                    if g > 1 or g < 0:
                        P_du = err - pid[0] * grads[0]
                        I_du = int_err - pid[1] * control_freq * grad_sum
                        D_du = der_err + pid[2] * (past_grad - grads[2]) / control_freq
                    else:
                        P_du = 0
                        I_du = 0
                        D_du = 0

                temp += itau * (-temp + self.K * u + outside_temp)

                grads[0] = (1 - itau) * grads[0] + (self.K * itau) * P_du
                grads[1] = (1 - itau) * grads[1] + (self.K * itau) * I_du
                grads[2] = (1 - itau) * grads[2] + (self.K * itau) * D_du

                if t % control_freq == 0:
                    past_grad = grads[2]

                t_err = ref - temp
                tracking_err += abs(t_err)
                jt = t_err / np.sqrt(1 + t_err ** 2)

                err_grads[0] = err_grads[0] + 1e-2 * jt * grads[0]
                err_grads[1] = err_grads[1] + 1e-8 * jt * grads[1]
                err_grads[2] = err_grads[2] + 1e-1 * jt * grads[2]

            if tracking_err < smallest_err:
                best_pid = pid
                smallest_err = tracking_err

            new_pid = np.array([0.0, 0.0, 0.0])
            new_pid[0] = pid[0] + itau * err_grads[0] / sim_len
            new_pid[1] = pid[1] + itau * err_grads[1] / sim_len
            new_pid[2] = pid[2] + itau * err_grads[2] / sim_len
            pid = np.clip(new_pid, pid - 1, pid + 1)
            progress_bar_value = i + 1
            if cancel_calibrate:
                break
        progress_bar_value = 0
        progress_bar_text = ""
        return best_pid


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = Root()
    root.after(0, root.update_ui)
    root.mainloop()
    root.quit()

