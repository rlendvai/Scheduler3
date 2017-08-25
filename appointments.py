import copy
import random
import config
import names
from utility import ID
from printer import Log, LOG

id_db = ID()
class Patient:
    def __init__(self):
        self.first_name = names.get_first_name()
        self.last_name = names.get_last_name()
        self.id = id_db.get_new_ID(self)


    def get_name(self, type=None):
        if type == "short":
            return self.first_name + " " + self.last_name[0] + "."
        else:
            return self.first_name + " " + self.last_name

    def __str__(self):
        return self.get_name()


class Appointment:
    def __init__(self, patient, duration, time):
        self.patient = patient
        self.duration = duration
        self.time = time
        self.offers = []
        self.id = id_db.get_new_ID(self)

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

    def seenIt(self, appt_slot):
        counter = 0
        log_string = ("Asking if " + str(self.patient) + " has seen " + str(appt_slot))
        LOG.log(log_string, 'offer_making')
        for offer in self.offers:
            if offer[0] == appt_slot:
                counter+=1
        log_string=(str(self.patient) + "has been offered " + str(appt_slot) + " " + str(counter) + " times before...")
        LOG.log(log_string, 'offer_making')
        return counter

    def totalOffersReceived(self):
        return len(self.offers)

    def change_time(self,time):
        self.time = time

    def try_change(self, apptslot):

        log_string = "#" + str(len(self.offers)+1) + ": Trying " + self.patient.get_name(type="short") + " > "
        LOG.log(log_string, 'offer_response')

        if random.random()<config.chance_patient_accepts_offer/100:
            LOG.log("Offer accepted", 'offer_response')
            self.offers.append([copy.deepcopy(apptslot), True])
            return True
        else:
            LOG.log("Offer REFUSED", 'offer_response')
            self.offers.append([copy.deepcopy(apptslot), False])
            return False

    def __str__(self):
        return "(" + str(self.time).lower() + " " + str(self.patient.get_name(type="short") + ")")


class AppSlot:
    def __init__(self, begin_time, length):
        self.appointment = None
        self.type = "General"
        self.begin_time = begin_time
        self.length = length
        self.id = id_db.get_new_ID(self)

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

    # Is the appointment between the two dates, inclusive
    def between_dates(self, date1, date2):
        if self.begin_time.between(date1, date2):
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

    def status_printer(self):

        status_string = ""
        status_array = []
        time = str(self.begin_time).lower()

        if self.appointment != None:
            name = self.appointment.patient.get_name()
        else:
            name = '    <FREE>    '

        status_string = time + ' ' + name
        status_array = [time, name]

        return {"string" : status_string, "array" : status_array}

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


