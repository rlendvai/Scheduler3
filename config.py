#import pendulum


sim_runs = 50 #number of times simulator should loop overall

days = 5 # number of days of schedule to create
slots_per_day = 3 # number of appointment slots each day should have
duration = 30 #duration of appointments
total_entries = slots_per_day * days
density = 50 # density of initially created schedule as percent
offer_wait_time = 5 #in minutes
schedule_display_range_initial = "A1:B" + str(total_entries)
schedule_display_range_secondary = "B1:B" + str(total_entries)
log_range = "Log!a1:B1000000"
dashboard_start_row = total_entries + 2