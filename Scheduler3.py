import names
import copy
import random
from pendulum import *
import pendulum
import pickle
import gspread

pendulum.set_to_string_format('%m/%d %I:%M%p')

class Appointment():
    def __init__(self, patient, duration, time):
        self.patient = patient
        self.duration = duration
        self.time = time
        self.offers = []
        self.id = self.make_id()

    def offers_report(self):

        string=""
        if(len(self.offers)>0):
            for offer in self.offers:
                string += self.patient.get_name(type="short") + ": "
                string += str(offer[0])
                if offer[1]:
                    string += ": accepted"
                else:
                    string += ": rejected"
                string += "\n"
        else:
            string = self.patient.get_name(type="short") + ": No offers.\n"

        return string


    def make_id(self):

        id = random.randint(1,1000000000000)
        return id

    def seenIt(self, appt_slot):
        counter = 0
        #print("Asking if", self.patient, "has seen", appt_slot)
        for offer in self.offers:
            if offer[0] == appt_slot:
                counter+=1
        #print(self.patient, "has been offered", str(appt_slot), counter, "times before...")
        return counter

    def totalOffersReceived(self):
        return len(self.offers)

    def change_time(self,time):
        self.time = time

    def try_change(self, time, apptslot):


        #self.offers.append([time, True])

        print("\n#", len(self.offers)+1, ": Trying ", self.patient.get_name(type="short"), " > ", end="", sep="")

        if (random.random()<.1):
            print("Ok")
            self.offers.append([copy.deepcopy(apptslot), True])
            return True
        else:
            print("REFUSED")
            self.offers.append([copy.deepcopy(apptslot), False])
            return False

    def __str__(self):
        return "(" + str(self.time).lower() + " " + str(self.patient.get_name(type="short") + ")")

class Patient:
    def __init__(self):
        self.first_name = names.get_first_name()
        self.last_name = names.get_last_name()
        self.id = self.make_id()

    def make_id(self):

        id = random.randint(1, 1000000000000)
        return id

    def get_name(self, type=None):
        if type == "short":
            return self.first_name + " " + self.last_name[0] + "."
        else:
            return self.first_name + " " + self.last_name

    def __str__(self):
        return self.get_name()


class AppSlot:
    def __init__(self, begin_time, length):
        self.appointment = None
        self.type = "General"
        self.begin_time = begin_time
        self.length = length

        if length > 0:
            self.fill(Appointment(Patient(), length, begin_time))

    def __eq__(self, other):
        if(self.begin_time == other.begin_time and \
                self.type == other.type and \
                self.length == other.length):
            return True
        else:
            False

    def __gt__(self, other):

        if(self.begin_time > other.begin_time):
            return True
        else:
            return False

    def time_diff(self, appt_slot):
        #returns hours difference, rounding down. E.g. 59 minutes is 0 hours diff, 61 min is 2 hours difference

        return self.begin_time.diff(appt_slot.begin_time).in_hours()


    def __str__(self):
        if self.appointment != None:
            return "[" + str(self.begin_time).lower() + "(" + str(self.length) + "): " + str(self.appointment) + "]"
        else:
            return "[" + str(self.begin_time).lower() + "(" + str(self.length) + "): <None>]"
            #return "[" + str(self.begin_time) + "(", self.length, "): <FREE>]"

    def fill(self, appointment, force=True):

        if self.appointment is None:
            if force == True:
                self.appointment = appointment
                appointment.change_time(self.begin_time)
                return True
            elif appointment.try_change(self.begin_time, self):
                self.appointment = appointment
                self.appointment.change_time(self.begin_time)
                return True
            else:
                return False
        else:
            sys.exit("You can not fill an already filled slot!")

    def unfill(self):
        self.appointment = None

    def status_string(self):

        #status_string = self.begin_time.format('MM/DD HH:mm') + ' '
        status_string = str(self.begin_time).lower() + " "

        if self.appointment != None:
            status_string = status_string + self.appointment.patient.get_name(type="short")
        else:
            status_string = status_string + '    <FREE>    '

        return status_string

    def getName(self):
        if self.appointment is None:
            return "No associated patient."
        else:
            return self.appointment.patient.get_name()

    def filled_status(self):
        if self.appointment == None:
            return False
        else:
            return True

    def __lt__(self, other):
        pass

        # def filled_slots(self):


class Schedule:
    def __init__(self, start_time, num_days=1, num_slots=1, duration=30, density_percent=80):

        self.start_time = start_time
        self.cal_times = []


        # the two loops are used to increment the start time by days and hours, to create the desired schedule
        for i in range(num_days):
            for n in range(num_slots):
                    slot_time = self.start_time.add(days=i)
                    slot_time = slot_time.add(minutes=(n * duration))
                    if random.random() <= density_percent / 100:
                        self.cal_times.append((slot_time, AppSlot(slot_time, duration)))
                    else:
                        self.cal_times.append((slot_time, AppSlot(slot_time, 0)))

    def cal_times_printer(self, cal_times):

        last_seen_day = None
        start_time = cal_times[0][0]

        print("\n**** SCHEDULE STARTING: ", start_time.format('MM/DD'), " ***\n")
        for cal_time in cal_times:
            if last_seen_day != cal_time[0].format('MM/DD'):
                print("--------", cal_time[0].format('MM/DD'), "-------")
            print(cal_time[1].status_string())
            last_seen_day = cal_time[0].format('MM/DD')


    def show(self):
        self.cal_times_printer(self.cal_times)


    def cancel_appointment(self, time):
    # unfill the slot at this time in the schedule

        dict(self.cal_times)[time].unfill()

    def fill_appointment(self, time, appointment, force = True):
        if force == True:
            return dict(self.cal_times)[time].fill(appointment)
        else:
            return dict(self.cal_times)[time].fill(appointment, force = False)

    def find_slot_id(self, time):
        for i in range(len(self.cal_times)):
            if self.cal_times[i][0] == time:
                return i
        return False

    #get the time of a time in an appointment
    def get_time(self, slot):
        pass

    def move(self, from_time, to_time):

        print("\nMoving", dict(self.cal_times)[from_time].getName(), "from", from_time.format("MM/DD HH:mm"), "to", to_time.format("MM/DD HH:mm"))
        self.fill_appointment(to_time, dict(self.cal_times)[from_time].appointment)
        #self.show()
        self.cancel_appointment(from_time)

    def try_move(self, from_time, to_time):

        #print("\nTrying to move", dict(self.cal_times)[from_time].getName(), "from", from_time.format("MM/DD HH:mm"), "to", to_time.format("MM/DD HH:mm"))


        if(self.fill_appointment(to_time, dict(self.cal_times)[from_time].appointment, force=False)):
            print("\nMoving", dict(self.cal_times)[from_time].getName(), "from", from_time.format("MM/DD HH:mm"), "to", to_time.format("MM/DD HH:mm"))
            self.cancel_appointment(from_time)
        else:
            print("\nCouldn't move", dict(self.cal_times)[from_time].getName(), "from", from_time.format("MM/DD HH:mm"), "to",to_time.format("MM/DD HH:mm"))


class Offer:
    def __init__(self, original_appt, proposed_appt_slot, time_sent = None):
        self.original_appt = original_appt
        self.proposed_slot = proposed_appt_slot
        self.time_sent = time_sent

    def __str__(self):
        string = str(self.original_appt) + " ==> "
        string += self.proposed_slot.__str__()
        #+ " ==> "
        #+ print(self.proposed_slot)
        return string
        #+ self.proposed_slot.__str__()

class Filler:
    def __init__(self, Schedule):
        self.schedule = Schedule
        self.sent_offers = []

    def report_offers(self):
        for slot in self.filled_slots():
            print(slot.appointment.offers_report(), sep="")

    def filled_slots(self):
        #return [x for x in self.schedule.cal_times if x[1].filled_status()]
        return [x[1] for x in self.schedule.cal_times if x[1].filled_status()]

    def free_slots(self):
        return [x[1] for x in self.schedule.cal_times if not(x[1].filled_status())]

    def reschedule(self):

        target_slot = self.free_slots()[0]
        next_slot = self.getNextSlot(target_slot)
        if self.getNextSlot(self.free_slots()[0]) is None:
            return False
        if len(self.free_slots())>0 and len(self.filled_slots())>0 and self.free_slots()[0].begin_time < next_slot.begin_time:
            free_time = target_slot.begin_time
            original_time = next_slot.begin_time
            offer=Offer(next_slot, copy.deepcopy(target_slot))
            self.sent_offers.append(offer)
            self.schedule.try_move(original_time, free_time)

    def isEligible(self, slot_with_appt, target_slot, hour_limit=1):
        #qualified only if slot is later than the first available slot
        print("Evaluating eligibility for", str(slot_with_appt))

        if slot_with_appt.time_diff(self.free_slots()[0])< hour_limit:
            print(slot_with_appt.appointment.patient.get_name(), "is not eligible is closer than", hour_limit, "hour(s)")
            return False

        if slot_with_appt.appointment.seenIt(target_slot):
            print(slot_with_appt.appointment.patient.get_name(), "is not eligible because it was already rejected")

            return False

        return True

    # Find the next eligible slot

    def getNextSlot(self, target_slot):
        candidate_slot = None
        min_offers_received = None
        for slot in reversed(self.filled_slots()):
            if not(self.isEligible(slot, target_slot, 1)): continue
            if min_offers_received is None or slot.appointment.totalOffersReceived() < min_offers_received:
                min_offers_received = slot.appointment.totalOffersReceived()
                candidate_slot = slot
                print("candidate is", candidate_slot.appointment.patient.get_name(), "seen", min_offers_received, "offers")
        return candidate_slot

def diff(old_schedule, new_schedule):

    for old_time_slot, new_time_slot in zip(old_schedule.cal_times, new_schedule.cal_times):
        old_appt_slot = old_time_slot[1]
        new_appt_slot = new_time_slot[1]
        if old_appt_slot.getName() != new_appt_slot.getName():
            print("Changed:", old_appt_slot.status_string())
            print("To:", new_appt_slot.status_string())
        else:
            pass
            #print(True)

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

    slots = 20
    rand = 40
    start_time = Pendulum(2017, 8, 1, 9, tzinfo='America/New_York')
    S = Schedule(start_time, num_days=1, num_slots = slots, duration=30, density_percent=rand)
    Z = copy.deepcopy(S)

    #seek_time = Pendulum(2017, 8, 1, 9, 00, tzinfo='America/New_York')

    #S.cancel_appointment(seek_time)

    f = Filler(S)

    for i in range(slots):
        S.show()
        print("\n")
        if f.reschedule() == False:
            break

    f.report_offers()

    #print("\n", '\n'.join([str(item) for item in f.sent_offers]), sep="")


    '''
    
    GLOBAL TIME
    
    While TIME + 5(
    
        random_cancel
        go(time)
            S.docancellations()
            S.refills
            
    refills(
        Scheduler(schedule)
            internal Scheduler.findopenings(schedule)
            internal Sheduler.make_waitlist()
            return Schedule
            
    
    
    '''



main()
