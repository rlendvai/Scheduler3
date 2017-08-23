import copy
import random
import pendulum
import config
from appointments import Patient, Appointment, AppSlot
from printer import *
from printer import gprinter

pendulum.set_to_string_format('%m/%d %I:%M%p')


#This class keeps track of time for a given schedule
class BigBen:
    def __init__(self, Schedule):
        self.now = Schedule.start_time

    def add_time(self, minutes=5):
        self.now.add(minutes)



class Updater:
    def __init__(self, Schedule):
        self.schedule = Schedule
        self.sent_offers = []

    # print report of offers made so far
    def report_offers(self):
        for slot in self.filled_slots():
            print(slot.appointment.offers_report(), sep="")

    # return all filled slots on the schedule (utility function)
    def filled_slots(self):
        #return [x for x in self.schedule.cal_times if x[1].filled_status()]
        return [x[1] for x in self.schedule.cal_times if x[1].filled_status()]

    # return all free slots on the schedule (utility function)
    def free_slots(self):
        free_slots=[]

        for cal_time in self.schedule.cal_times:
            slot = cal_time[1]
            if slot.begin_time > T and slot.filled_status() is False:
                free_slots.append(slot)
        return free_slots

    #Fill the soonest empty slots on schedule
    def reschedule(self):
        global T

        LOG.log_event("Reschedule called...")

        target_slots = self.free_slots()
        next_slot = None
        # For the next available slot in the schedule, starting at the earliest, we'll find someone willing to move to it
        for target_slot in target_slots:
            LOG.log_event("Trying to fill " + str(target_slot), False)
            #Try to findan appointment slot with someone who's willing to move
            next_slot = self.getNextSlot(target_slot)
            if next_slot is not None:
                #we couldn't find anyone to move
                break
        # We couldnt't find a willing mover or an available slot to move to
        if next_slot is None or target_slot is None:
            return False

        free_time = target_slot.begin_time
        original_time = next_slot.begin_time
        offer=Offer(next_slot, copy.deepcopy(target_slot))
        self.sent_offers.append(offer)
        self.schedule.try_move(original_time, free_time)
        return True

    #determine if a patient is eligible for a specific slot
    def isPatientEligible(self, slot_with_appt, target_slot):
        #qualified only if slot is later than the first available slot
        LOG.log_event("Evaluating eligibility for " + slot_with_appt.appointment.patient.get_name(type="short"),False )

        eligible = True
        reason = ""

        if slot_with_appt.time_diff(target_slot)< config.min_offer_delta_hours:
            reason = "Slot is closer than" + str(config.min_offer_delta_hours) + "hour(s)"
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

    # Find the next slot that we'll move a patient from, based on patient's qualifcations relative to other patients

    def getNextSlot(self, target_slot):
        candidate_slot = None
        min_offers_received = None
        #Iterate over all available patient slots
        for slot in reversed(self.filled_slots()):
            if not(self.isPatientEligible(slot, target_slot)): continue
            if min_offers_received is None or slot.appointment.totalOffersReceived() < min_offers_received:
                min_offers_received = slot.appointment.totalOffersReceived()
                candidate_slot = slot
                LOG.log_event("candidate is " + \
                                         candidate_slot.appointment.patient.get_name() + \
                                         " has seen " + str(min_offers_received) + " offers")
        return candidate_slot

    # Remove slots that fall in the specified date range, inclusive. NOT CURRENTLY USED.
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
        chance_per_slot = 100/config.slots_per_day

        # How far the appointment will be
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
                LOG.log_event("Created new appointment", True, True)
                return True #succeded in finding a slot
            scheduling_attempts += 1
            if scheduling_attempts > max_attempts:
                continue #Exceeded max attempts without being able to schedule
            max_loops += 1
            if loops > max_loops: break

        return False # We ran out of slots







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

    def remaining_cal_times(self):
        remaining_cal_times = []
        for cal_time in self.cal_times:
            if(cal_time[0]) > T:
                remaining_cal_times.append(cal_time)

        return remaining_cal_times


    #Get the cal_times between two dates, inclusive
    def get_x_to_y_time_cal_times(self, start_time, finish_time = None, filled_only = False):

        new_cal_times = []
        for cal_time in self.cal_times:
            time = cal_time[0]
            if time >= start_time and (time <= finish_time or finish_time is None):
                if filled_only and cal_time[1].filled_status() == False:
                    pass
                else:
                    new_cal_times.append(cal_time)

        return new_cal_times

    #Will execute a cancellation according to the percent probability assigned.
    #It decides only whether a cancellation should occure, not which appointment should be cancelled
    def do_daily_cancel(self, percent):
        if random.random() < percent/100:
            self.cancel_rand_appointment()

    # cancels a rand appointment, on a rand day, according to the weights assigned in config
    def cancel_rand_appointment(self):

        #dictionary that contains day range, from today, when the appointment should be cancelled
        cancel_range = random.choices(config.cancel_buckets, config.weights)[0]
        cancel_period_begin_days_from_today = cancel_range['begin_day']
        cancel_period_end_days_from_today = cancel_range['end_day']
        cancel_period_start = T.add(days = cancel_period_begin_days_from_today).start_of('day')
        cancel_period_end = T.add(days=cancel_period_end_days_from_today).end_of('day')


        cal_times = self.get_x_to_y_time_cal_times(cancel_period_start, cancel_period_end, filled_only=True)
        if len(cal_times)>0:
            cal_time_to_cancel = random.choice(cal_times)
            LOG.log_event("Cancelling " + str(cal_time_to_cancel[1]), screen_print=True)
            appt_time_to_cancel = cal_time_to_cancel[0]
            self.cancel_appointment(appt_time_to_cancel)
            return appt_time_to_cancel
        else:
            False


    def cancel_appointment(self, time):
        # unfill the slot at this time in the schedule

        dict(self.cal_times)[time].unfill()


    def show(self):
        self.cal_times_printer(self.cal_times)


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

    # Return True if there is an appointment at the given time. False otherwise.
    def is_filled(self, time):
        cal_times_dictionary = dict(self.cal_times)
        if time in cal_times_dictionary:
            return cal_times_dictionary[time]
        else:
            return False

def SimRunner(schedule, sim_runs):
    global T
    offer_maker = Updater(schedule)
    time_last_app_created = T
    #for i in range (sim_runs):
    # f.schedule_new()
    #    schedule.show()
    for i in range (config.sim_runs):
        LOG.log_event("It's now " + str(T), True, True)
        #Is it the beginning of an appointment? If so, let's make a new one, and let's cancel one.
        if(schedule.is_filled(T)):
            schedule.do_daily_cancel(config.overall_cancellation_rate)
            offer_maker.schedule_new()
            offer_maker.reschedule()
        #print("Not showing schedule")
        #schedule.show()
        T = T.add(minutes= 10)



    offer_maker.report_offers()
    LOG.log_event("All done!")
    LOG.gprint_log(verbose=True, everything=True)

    return True

def main():


    global T, LOG, SIM_RUNS, CLOCK

    T = pendulum.Pendulum(2017, 8, 1, 9, tzinfo='America/New_York')
    SIM_RUNS = config.sim_runs
    LOG = Log()

    gprinter("", "", "clear") # Clear the sheet screen



    pendulum.set_formatter('alternative')
    S = Schedule(T, config.days, num_slots = config.slots_per_day, duration=config.duration, density_percent=config.density)
    clock = BigBen(S)
    # This is where the monkey jumps into the water!
    SimRunner(S, SIM_RUNS)

