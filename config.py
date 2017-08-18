import pendulum


t = pendulum.Pendulum(2017, 8, 1, 9, tzinfo='America/New_York')
sim_runs = 10 #number of times simulator should loop overall

days = 10 # number of days of schedule to create
slots_per_day = 3 # number of appointment slots each day should have
duration = 30 #duration of appointments
density = 50 # density of initially created schedule as percent
offer_wait_time = 5 #in minutes
dashboard_height = 10 # number of lines
