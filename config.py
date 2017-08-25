#import pendulum


sim_runs = 3 #number of times simulator should loop overall

days = 5 # number of days of schedule to create
slots_per_day = 6 # number of appointment slots each day should have
duration = 30 #duration of appointments
total_entries = slots_per_day * days
density = 50 # density of initially created schedule as percent
offer_wait_time = 5 #in minutes
schedule_display_range_initial = "A1:B" + str(total_entries)
schedule_display_range_secondary = "B1:B" + str(total_entries)
log_range = "Log!a1:B1000000"
dashboard_start_row = total_entries + 2
min_offer_delta_hours = 12
chance_patient_accepts_offer = 80
chance_of_new_appt_per_5_mins = 100 * (duration/5)
max_days_ahead = 31 #max days ahead to do operations
overall_cancellation_rate = 100
# Set up probabilities for cancellation, and create an according array holding the weights of each (for input into rand)
cancel_buckets = [
                    {'begin_day': 0, 'end_day': 0, 'weight': 37},
                    {'begin_day': 1, 'end_day': 1, 'weight': 13},
                    {'begin_day': 2, 'end_day': 2, 'weight': 6},
                    {'begin_day': 3, 'end_day': 3, 'weight': 4},
                    {'begin_day': 4, 'end_day': 4, 'weight': 3},
                    {'begin_day': 5, 'end_day': 5, 'weight': 2},
                    {'begin_day': 6, 'end_day': 6, 'weight': 2},
                    {'begin_day': 7, 'end_day': 7, 'weight': 3},
                    {'begin_day': 8, 'end_day': 14, 'weight': 8},
                    {'begin_day': 15, 'end_day': 21, 'weight': 4},
                    {'begin_day': 22, 'end_day': 60, 'weight': 11}
                 ]
weights = []
for bucket in cancel_buckets:
    weights.append(bucket['weight'])
# Govern how different event types should be printed
#c == console, g == google
event_print_types = dict(
                appointment_creation=[],
                appointment_fill=[],
                cancel=[],
                general=[],
                eligibility = [],
                logging = [],
                offer_making = [],
                offer_report = [],
                offer_response = [],
                rescheduling = [],
                scheduling=[],
                schedule = [],
                simulator = [],
                utility = []
                )

