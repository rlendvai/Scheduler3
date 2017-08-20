import copy
import random
import pendulum
import config
from appointments import Patient, Appointment, AppSlot
from printer import *
from printer import gprinter

pendulum.set_to_string_format('%m/%d %I:%M%p')


class MakeOffers:
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
        global T


        LOG.log_event("Reschedule called...")


        target_slots = self.free_slots()
        next_slot = None
        for target_slot in target_slots:
            LOG.log_event("Trying to fill " + str(target_slot))
            next_slot = self.getNextSlot(target_slot)
            if next_slot is not None:
                break
        if next_slot is None or target_slot is None:
            return False

        if len(self.free_slots())>0 and len(self.filled_slots())>0 and target_slot.begin_time < next_slot.begin_time:
            free_time = target_slot.begin_time
            original_time = next_slot.begin_time
            offer=Offer(next_slot, copy.deepcopy(target_slot))
            self.sent_offers.append(offer)
            self.schedule.try_move(original_time, free_time)
            T = T.add(minutes=config.offer_wait_time)
            return True

    def isEligible(self, slot_with_appt, target_slot, hour_limit=1):
        #qualified only if slot is later than the first available slot
        LOG.log_event("Evaluating eligibility for " + slot_with_appt.appointment.patient.get_name(type="short"),False )

        eligible = True
        reason = ""

        if slot_with_appt.time_diff(target_slot)< hour_limit:
            reason = "Slot is closer than" + str(hour_limit) + "hour(s)"
            eligible = False

        if slot_with_appt.appointment.seenIt(target_slot):
            reason = "Slot was previously rejected."
            eligible = False

        if target_slot > slot_with_appt or target_slot == slot_with_appt:
            reason = "Target slot is not earlier than original."
            eligible = False


        if not(eligible): reason = "FAILED: " + reason
        else: reason = "OK."

        LOG.log_event("Eligibility check for " + slot_with_appt.appointment.patient.get_name(type="short") + ": " + reason, False)

        return eligible

    # Find the next eligible slot

    def getNextSlot(self, target_slot):
        candidate_slot = None
        min_offers_received = None
        for slot in reversed(self.filled_slots()):
            if not(self.isEligible(slot, target_slot, 1)): continue
            if min_offers_received is None or slot.appointment.totalOffersReceived() < min_offers_received:
                min_offers_received = slot.appointment.totalOffersReceived()
                candidate_slot = slot
                log_line = "candidate is " + candidate_slot.appointment.patient.get_name() + " has seen " + str(min_offers_received) + " offers"
                LOG.log_event(log_line)
        return candidate_slot

    # Remove slots that fall in the specified date range, inclusive
    def remove_between_dates(self, date1, date2, appt_slots):
        remaining_slots = [slot for slot in appt_slots if slot.between_dates(date1, date2) ]
        return remaining_slots



    def schedule_new(self):
        global T, slots_per_day
        distance_probability = [0] # with n days distance, this is my probability of accepting an appointment
        min_days = 1
        drop_off_factor = .3
        max_loops = 2
        max_attempts = 1
        chance_per_slot = 100/slots_per_day

        for i in range(1,31):
            distance_probability.append((10-(drop_off_factor*i))**2)

        eligible_slots = [slot for slot in self.free_slots() if slot.begin_time > T.add(days=min_days)]

        scheduling_attempts = 0
        loops = 0
        for slot in eligible_slots:
            delta = T.diff(slot.begin_time).in_days()
            chance = distance_probability[delta]*chance_per_slot/100
            if(random.uniform(1,100) < chance):
                slot.fill(Appointment(Patient(), slot.length, slot.begin_time))
                return True #succeded in finding a slot
            scheduling_attempts += 1
            if scheduling_attempts > max_attempts:
                continue #Exceeded max attempts without being able to schedule
            max_loops += 1
            if loops > max_loops: break

        LOG.gprint_log(verbose=True, everything=True)
        return False # We ran out of slots




def Scheduler(Schedule, sim_runs):
    global T
    offer_maker = MakeOffers(Schedule)

    #for i in range (sim_runs):
    # f.schedule_new()
    #    Schedule.show()

    while(1):
        if offer_maker.reschedule() == False:
            break
        Schedule.show()

    Schedule.show()
    offer_maker.report_offers()
    LOG.gprint_log(verbose=True, everything=True)

    return True



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



class Schedule:
    def __init__(self, start_time, num_days=1, num_slots=1, duration=30, density_percent=80):

        self.start_time = start_time
        self.cal_times = []
        self.last_printed = []


        # the two loops are used to increment the start time by days and hours, to create the desired schedule
        for i in range(num_days):
            for n in range(num_slots):
                slot_time = self.start_time.add(days=i)
                slot_time = slot_time.add(minutes=(n * duration))
                if random.randrange(1,100) <= density_percent:
                    self.cal_times.append((slot_time, AppSlot(slot_time, duration)))
                else:
                    self.cal_times.append((slot_time, AppSlot(slot_time, 0)))

    def cal_times_printer(self, cal_times):

        schedule_entries = []
        for cal_time in cal_times:
            schedule_entries.append(cal_time[1].status_printer()['array'])

        LOG.scheduleDisplay(schedule_entries)


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

        LOG.log_event("\nMoving " + dict(self.cal_times)[from_time].getName() + " from " + from_time + " to " + to_time)
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

    global T, LOG, SIM_RUNS

    T = pendulum.Pendulum(2017, 8, 1, 9, tzinfo='America/New_York')

    #LOG= Log(config.days*config.slots_per_day + 1) # figure out total slots so we can write the log below it
    LOG= Log() # figure out total slots so we can write the log below it

    SIM_RUNS = config.sim_runs

    pendulum.set_formatter('alternative')
    S = Schedule(T, config.days, num_slots = config.slots_per_day, duration=config.duration, density_percent=config.density)

    # This is where the monkey jumps into the water!
    Scheduler(S, SIM_RUNS)

main()