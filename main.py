import Simulator
from tkinter import *
from tkinter import ttk
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import (
    FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.font_manager import FontProperties
fontP = FontProperties()
fontP.set_size('small')
sns.set()


class Root(Tk):
    def __init__(self):
        super(Root, self).__init__()
        self.title("Temperature Simulator")
        #self.minsize(1024, 600)

        # User Selected Variables
        self.K = StringVar()
        self.K.set(35)
        self.tau = StringVar()
        self.tau.set(900)
        self.step_size = StringVar()
        self.step_size.set(5)
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

        # Calibrate P, I, D
        self.calibrate_button = Button(self,
                                       text="Calibrate",
                                       command=self.calibrate)
        self.calibrate_button.grid(column=0,
                                   row=3,
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
                             row=5,
                             padx=20,
                             pady=20)
        self.populate_plot_frame()



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
                             row=0)
        self.outside_check = Checkbutton(self.plot_frame,
                                         text="outside",
                                         variable=self.plot_outside)
        self.outside_check.grid(column=0,
                                row=2)
        self.ref_check = Checkbutton(self.plot_frame,
                                      text="reference",
                                      variable=self.plot_ref)
        self.ref_check.grid(column=0,
                            row=1)
        self.measure_check = Checkbutton(self.plot_frame,
                                         text="measured",
                                         variable=self.plot_measure)
        self.measure_check.grid(column=0,
                                row=3)

    def run_sim(self):
        start_date = [int(self.start_year.get()), self.start_month.get(),
                      int(self.start_day.get()), int(self.start_hour.get())]
        end_date = [int(self.end_year.get()), self.end_month.get(),
                    int(self.end_day.get()), int(self.end_hour.get())]

        ref_str = self.ref.get().split(",")
        ref = [float(i) for i in ref_str]

        sim = Simulator.Simulation(start_date=start_date, end_date=end_date,
                                   K=float(self.K.get()), tau=float(self.tau.get()),
                                   step_size=float(self.step_size.get()),
                                   P=float(self.P.get()), I=float(self.I.get()),
                                   D=float(self.D.get()), ref=ref,
                                   use_weighted_mean=self.use_weighted_mean.get(),
                                   status=self.status.get())
        t, r_temp, o_temp, ref_temp, m_temp = sim.run_sim(initial_temp=float(self.initial_temp.get()),
                                                          measure_freq=int(self.measure_freq.get()),
                                                          control_freq=int(self.control_freq.get()))
        self.plot_data(t, r_temp, o_temp, ref_temp, m_temp)

    def calibrate(self):
        sim = Simulator.Simulation(K=float(self.K.get()), tau=float(self.tau.get()),
                                   step_size=float(self.step_size.get()),
                                   P=float(self.P.get()), I=float(self.I.get()),
                                   D=float(self.D.get()))
        pid = sim.calibrate(control_freq=int(self.control_freq.get()))

        self.P.set(round(pid[0], 6))
        self.I.set(round(pid[1], 6))
        self.D.set(round(pid[2], 6))

    def plot_data(self, time, temp, b_temp, r_temp, m_temp):
        plt.cla()
        fig = plt.figure(figsize=(5, 4), dpi=100)
        if self.plot_outside.get():
            plt.plot(time, b_temp, 'k', label='Outside', linestyle='--')
        if self.plot_ref.get():
            plt.plot(time, r_temp, 'r', label='Reference', linewidth=2, linestyle=':')
        if self.plot_measure.get():
            plt.plot(time, m_temp, 'g', label='Measured', linewidth=0.75, linestyle='-.')
        if self.plot_room.get():
            plt.plot(time, temp, 'b', label='Room', linewidth=0.5)
        plt.xlim(0, time[-1])
        plt.xlabel('Hour [h]')
        plt.ylabel('Temperature [°C]')
        plt.legend(bbox_to_anchor=(0.5, 1.1), loc='upper center', ncol=4, prop=fontP)
        canvas = FigureCanvasTkAgg(figure=fig, master=self)
        canvas.draw()
        canvas.get_tk_widget().grid(column=1,
                                    columnspan=2,
                                    row=2,
                                    rowspan=4,
                                    padx=20,
                                    pady=20)

        toolbar = NavigationToolbar2Tk(canvas, self, pack_toolbar=False)
        toolbar.update()
        toolbar.grid(column=1,
                     columnspan=2,
                     row=5)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    root = Root()
    root.mainloop()
    root.quit()

