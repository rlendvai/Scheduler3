import os
import pickle

class ID:
    def __init__(self):
        self.ids = {}

    def get_new_ID(self, var):
        var_type = type(var)
        if var_type in self.ids:
            self.ids[var_type] += 1
        else:
            self.ids[var_type] = 0
        return self.ids[var_type]

#write to file functions I decided not to use, in lieu of google
'''def save_schedule_to_disk(schedule, file_name, over_write=False):

    if os.path.isfile(file_name):
        fh = open(file_name, "wb")
        pickle.dump(schedule, fh)
        fh.close()
    else:
        print("couldn't find file")

def read_schedule_from_disk(file_name):
    fh = open("schedule.obj", "rb")
    myschedule = pickle.load(fh)
    return myschedule'''






