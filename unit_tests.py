import copy
import random
import pendulum
import config
import utility
from appointments import Patient, Appointment, AppSlot
from printer import *
from printer import gprinter
from scheduler import *

global T, LOG, SIM_RUNS, CLOCK

def get_x_to_y_time_cal_times_UNIT_TEST():
    T = pendulum.Pendulum(2017, 8, 1, 9, tzinfo='America/New_York')
    LOG = Log()
    SIM_RUNS = config.sim_runs

    pendulum.set_formatter('alternative')
    S = Schedule(T, config.days, num_slots=config.slots_per_day, duration=config.duration, density_percent=config.density)

    date1 = pendulum.Pendulum(2017, 8, 1, 10, 30, tzinfo='America/New_York')
    date2 = pendulum.Pendulum(2017, 8, 3, 12, 30, tzinfo='America/New_York')

    new_cal_times = S.get_x_to_y_time_cal_times(date1,date2)
    assert new_cal_times[0][0] == date1 and new_cal_times[-1][0] == date2, "get_x_to_y_time_cal_times_UNIT_TEST failed."

def pick_day():

    buckets = {}

    for i in range(9300):
        cancel_bucket = random.choices(config.cancel_buckets, config.weights)
        begin_day = cancel_bucket[0]['begin_day']
        if str(begin_day) not in buckets:
            buckets[str(begin_day)] = 1
        else:
            buckets[str(begin_day)] = buckets[str(begin_day)] + 1

    print(buckets)

    #return cancel_bucket

class ID:
    def __init__(self):
        self.ids = {}

    def get_new_ID(self, var):
        var_type = type(var)
        if var.ID is None:
            if var_type in self.ids:
                self.ids[var_type] += 1
            else:
                self.ids[var_type] = 0
            return self.ids[var_type]
        else:
            exit("Asking for ID that already exists")

def main():
    #get_x_to_y_time_cal_times_UNIT_TEST()
    #pick_day()
    DB = utility.ID()
    for i in range (10):
        p = Patient()
        print(p.id)
    print(p.id)
    for i in range (10):
        p = Patient()
        a = Appointment(p,10,pendulum.now())
        print(p.id)
        print(a.id)
    print(p.id)

main()