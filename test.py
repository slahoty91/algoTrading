from datetime import datetime, time

current_time = datetime.now().time()
start_time = time(9, 15)
end_time = time(9, 20)
if start_time <= current_time <= end_time:
    print("The current time is between 20:00 and 20:05.")
else:
    print("The current time is not between 20:00 and 20:05.",start_time,end_time,current_time)