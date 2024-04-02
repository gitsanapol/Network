import threading
import time

def reset_routing_table():
    global routing_table
    routing_table = []  # Resetting the routing table
    print("Resettttttttttttttttt")
    t = threading.Timer(10, reset_routing_table)  # Restart the timer for the next reset
    t.start()

# Initialize the routing table
routing_table = [['192.168.1.1', 'A', 1], ['192.168.1.2', 'B', 2], ['192.168.1.3', 'C', 3]]

# Start the timer for resetting the routing table
reset_routing_table()

while True:
    print("Hello")
    time.sleep(0.5)
