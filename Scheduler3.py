from turtle import *

import names
import random
from pendulum import *
import pendulum
import pickle


class Appointment():
    def __init__(self, patient, duration, time):
        self.patient = patient
        self.duration = duration
        self.time = time


class Patient:
    def __init__(self):
        self.name = names.get_full_name()


class Slot:
    def __init__(self, begin_time, length):
        self.appointment = None
        self.type = "General"
        self.begin_time = begin_time
        if length > 0:
            self.fill(Appointment(Patient(), length, begin_time))

    def fill(self, appointment):
        if self.appointment == None:
            self.appointment = appointment
            return True
        else:
            sys.exit("You can not fill an already filled slot!")

    def unfill(self):
        self.appointment = None

    def status_string(self):

        status_string = self.begin_time.format('MM/DD HH:mm') + ' '

        if self.appointment != None:
            status_string = status_string + self.appointment.patient.name
        else:
            status_string = status_string + '    <FREE>    '

        return status_string

    def filled_status(self):
        if self.appointment == None:
            return False
        else:
            return True

    def __lt__(self, other):
        pass

        # def filled_slots(self):


class Schedule:
    def __init__(self, start_time, num_days=3, num_slots=3, duration=30, density_percent=80):

        self.start_time = start_time
        self.cal_times = []

        # the two loops are used to increment the start time by days and hours, to create the desired schedule
        for i in range(num_days):
            for n in range(num_slots):
                    slot_time = self.start_time.add(days=i)
                    slot_time = slot_time.add(minutes=(n * duration))
                    if random.random() <= density_percent / 100:
                        self.cal_times.append((slot_time, Slot(slot_time, duration)))
                    else:
                        self.cal_times.append((slot_time, Slot(slot_time, 0)))



    def makeQ(self):
        Q=[x for x in self.cal_times if x[1]!=None]
        return Q

    def showQ(self):
        self.show()



    def show(self):

        last_seen_day = None
        print("\n**** SCHEDULE STARTING: ", self.start_time.format('MM/DD'), " ***\n")
        for cal_time in self.cal_times:
            if last_seen_day != cal_time[0].format('MM/DD'):
                print("--------", cal_time[0].format('MM/DD'), "-------")
            print(cal_time[1].status_string())
            last_seen_day = cal_time[0].format('MM/DD')

    def cancel_appointment(self, time):

        id = self.find_slot_id(time)
        self.cal_times[id][1].unfill()

    def find_slot_id(self, time):
        for i in range(len(self.cal_times)):
            if self.cal_times[i][0] == time:
                return i
        return False





def main():
    '''
        FRESH = False
        DAYS = 2
        SLOTS = 4
        DURATION = 30

        if FRESH:
            myschedule = Schedule(DAYS, SLOTS, DURATION)
        else:
            fh = open("schedule.obj", "rb")
            myschedule = pickle.load(fh)



        fh = open("schedule.obj", "wb")
        pickle.dump(myschedule, fh)
        fh.close()
    '''

    pendulum.set_formatter('alternative')

    start_time = Pendulum(2017, 8, 1, 9, tzinfo='America/New_York')
    S = Schedule(start_time)
    S.show()
    seek_time = Pendulum(2017, 8, 1, 9, 30, tzinfo='America/New_York')
    S.cancel_appointment(seek_time)
    S.show()
    S.showQ()


main()
