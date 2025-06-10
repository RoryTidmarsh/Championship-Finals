import champ_placement as chp
import sys
import warnings
import time
import threading

warnings.filterwarnings("ignore")

#initialise the class
show = chp.plaza()

if len(sys.argv) > 1:
    height = sys.argv[1].capitalize()
    
else:
    height = input("Enter Height 'Sml', 'Med', 'Int' or 'Lge': ")

height = height.capitalize()

#
heights = ['Sml', 'Med', 'Int', 'Lge']
assert height in heights

# Variable to control the loop
stop_thread = False

# Shared variable to control the number of rows to display
num_rows = 30
num_rows_lock = threading.Lock()

def refreshes(height, index):
    global stop_thread, num_rows

    while not stop_thread:
        # Fetch and display results
        with num_rows_lock:
            current_num_rows = num_rows
        print("\nShowing max of top", current_num_rows)
        print(show.overall_results(height)[index].head(current_num_rows))
        print("\nType 'stop' then enter to stop the refresh at any point \n Type and integer and enter to set the max number of places shown in the next refresh")
        # New line after the results
        # print()

        # Countdown timer (2 minutes = 120 seconds)
        time_limit = 120
        for remaining in range(time_limit, 0, -1):
            if stop_thread:
                break
            sys.stdout.write(f"\rNext refresh in {remaining:3} seconds ")
            sys.stdout.flush()
            time.sleep(1)
        
        if stop_thread:
            print("\nStopping the refresh loop.")
            break

def check_stop():
    global stop_thread, num_rows
    while not stop_thread:
        user_input = input("Type 'stop' to end the loop or enter a new number to change the row count: ")
        if user_input.lower() == 'stop':
            stop_thread = True
        else:
            try:
                new_num_rows = int(user_input)
                if new_num_rows > 0:
                    with num_rows_lock:
                        num_rows = new_num_rows
                else:
                    print("Please enter a positive integer.")
            except ValueError:
                print("Invalid input. Please enter a valid number or 'stop'.")

# get the top 20 by calling index 0
# get the overall results by index = 1
index = 1

# Start the thread that listens for 'stop'
threading.Thread(target=check_stop, daemon=True).start()

# Start the refresh loop
refreshes(height, index)

