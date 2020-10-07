import pandas as pd
import numpy as np


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
            temp = np.sum(weights * measurements)
        else:
            temp = np.mean(measurements)
        self.temp_buffer.append(temp)

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
        time = []
        outside_temperature = []
        room_temperature = []
        reference_temperature = []
        measured_temperature = []
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
        return time, room_temperature, outside_temperature, reference_temperature, measured_temperature

    def calibrate(self, control_freq):
        pid = [0, 0, 0]
        best_pid = pid
        smallest_err = np.inf

        for i in range(100):

            # Errors
            int_err = 0
            past_err = 0
            tracking_err = 0

            # Gradients
            grads = [0, 0, 0]
            grad_sum = 0
            past_grad = 0
            err_grads = [0, 0, 0]

            temp = 15
            step_range = int(5 * self.tau / self.step_size)
            #dt = self.step_size
            dt = 1
            ref = 20

            for s in range(step_range):
                err = ref - temp
                int_err += err * dt

                if s % control_freq == 0:
                    der = (err - past_err) / dt
                    g = pid[0] * err + pid[1] * int_err + pid[2] * der
                    u = np.clip(g, 0, 1)
                    if u > 0.5:
                        self.heater = 1
                    else:
                        self.heater = 0

                grad_sum += grads[1]
                P_dy = (1 - dt / self.tau) * grads[0]
                I_dy = (1 - dt / self.tau) * grads[1]
                D_dy = (1 - dt / self.tau) * grads[2]

                if g > 1 or g < 0:
                    P_du = 0
                    I_du = 0
                    D_du = 0
                else:
                    P_du = self.K * dt * (err - pid[0] * grads[0]) / self.tau
                    I_du = self.K * dt * (int_err - dt * pid[1] * grad_sum) / self.tau
                    D_du = self.K * (err - past_err - pid[2] * grads[2] + pid[2] * past_grad) / self.tau

                grads[0] = P_dy + P_du
                grads[1] = I_dy + I_du
                grads[2] = D_dy + D_du

                past_err = err
                past_grad = grads[2]

                tracking_err += abs(err)
                if np.random.random() > 0.1:
                    err_grads[0] = err_grads[0] + err * grads[0] / np.sqrt(1 + err ** 2)
                    err_grads[1] = err_grads[1] + err * grads[1] / np.sqrt(1 + err ** 2)
                    err_grads[2] = err_grads[2] + err * grads[2] / np.sqrt(1 + err ** 2)

                b_temp = 10 + np.random.normal(0, 0.2)
                temp = self.update_temp(temp, b_temp)

            # Update pids
            new_pid = [0, 0, 0]
            new_pid[0] = np.clip(pid[0] + 5e-3 * err_grads[0] / step_range, pid[0] - 1, pid[0] + 1)
            new_pid[1] = np.clip(pid[1] + 1e-9  * err_grads[1] / step_range, pid[1] - 1, pid[1] + 1)
            new_pid[2] = np.clip(pid[2] + 1e-1 * err_grads[2] / step_range, pid[2] - 1, pid[2] + 1)
            pid = new_pid
            if tracking_err < smallest_err:
                best_pid = pid
                smallest_err = tracking_err
        return best_pid