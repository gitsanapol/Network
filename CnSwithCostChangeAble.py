from socket import *
import numpy as np
import threading
import json
import time
import ast
import random



hostname = gethostname()
IP_host = gethostbyname(hostname)
print("My IP Address:" + IP_host)
list_ip = [str(IP_host), "192.168.1.225"]

online_list = []
nexthop = []
cost = []
routing_table = []
subnet =[]
subnet_array = []
routerName = []
flattened_list = []
sendData=""
recvData=""

sleep_time = random.uniform(0.1, 2.5)

# router_initial = [ #   **** need to input in a-z order ****
#         {
#             "router-name": "A",
#             "link": ["B", "D"],
#             "cost-link": [1, 1],
#             "connection": [0, 0], # 0 for internal, 1 for external
#             "server-port": 1024,
#             "con-network": ["192.168.1.0/24", "192.168.4.0/24"]
#         },
#         {
#             "router-name": "B",
#             "link": ["A", "C", "D"],
#             "cost-link": [1, 1, 1],
#             "connection": [0, 0, 0], # 0 for internal, 1 for external
#             "server-port": 1025,
#             "con-network": ["192.168.2.0/24"]
#         },
#         {
#             "router-name": "C",
#             "link": ["B", "F"],
#             "cost-link": [1, 1],
#             "connection": [0, 0], # 0 for internal, 1 for external
#             "server-port": 1026,
#             "con-network": ["192.168.3.0/24"]
#         },
#         {
#             "router-name": "D",
#             "link": ["A", "B", "E"],
#             "cost-link": [1, 1, 1],
#             "connection": [0, 0, 0], # 0 for internal, 1 for external
#             "server-port": 1027,
#             "con-network": ["192.168.4.0/24"]
#         },
#         {
#             "router-name": "E",
#             "link": ["D", "F"],
#             "cost-link": [1, 1],
#             "connection": [0, 0], # 0 for internal, 1 for external
#             "server-port": 1028,
#             "con-network": ["192.168.6.0/24"]
#         },
#         {
#             "router-name": "F",
#             "link": ["C", "E"],
#             "cost-link": [1, 1],
#             "connection": [0, 0], # 0 for internal, 1 for external
#             "server-port": 1029,
#             "con-network": ["192.168.5.0/24"]
#         }
#     ]

def getConnection(dicts):
    ConnList = dicts[0]["connection"]
    return ConnList

# i = dict, string | o = boolean ---Help: Main
def find_router(router_dict, router_name):
    global online_list
    for router in router_dict:
        if router["router-name"] == router_name:
            online_list.append(router)
            return True
    return False

# i = dict | o = list
def selfSubnet(router_dict):
    global subnet
    for router in router_dict:
        subnet.append(router["con-network"])
        flattenList(subnet)
        subnet = flattened_list
        print("selfSubnet => " + str(subnet[0]))
        return subnet
    
# i = dict | o = list
def selfName(router_dict):
    global routerName
    global flattened_list
    for router in router_dict:
        flattened_list = []
        routerName.append(router["router-name"])
        flattenList(routerName)
        routerName = flattened_list
        # print("selfSubnet => " + str(routerName[0]))
        return routerName
    
# i = subnet | o = routing_table ---Help: selfSubnet
def update_subnet(subnet_array):
    global routing_table
    for i in range(len(subnet_array)):
        routing_table[i][0] = subnet_array[i]
    return routing_table

def flattenList(nested_list):
    global flattened_list
    for sublist in nested_list:
        for item in sublist:
            flattened_list.append(item)
        return flattenList

def generate_routing_table(subnet_array):
    global routing_table
    for subnet in subnet_array:
        routing_table.append([192, '-', 1])
    return routing_table

# i = routing_table | o = None
def print_routing():
    print("|  Dest. Subnet  |   Next hop   |     Cost     |")
    print("------------------------------------------------")
    for i in range(len(routing_table)):
        print("|", routing_table[i][0], "|      ", routing_table[i][1], "     |      ", routing_table[i][2], "     |")
    
def client(clientIP, clientPort, con_network):
    global sendData
    while True:
        client_socket = socket(AF_INET, SOCK_DGRAM)
        message = json.dumps(sendData).encode()
        client_socket.sendto(message, (clientIP, clientPort))
        print(f"ClientT => msg to {clientIP} at {clientPort}")
        client_socket.close()
        time.sleep(1.5)


def findLinkName(lists):
    for list in lists:
        return list["link"]

# i = dicts, lists | O = List of port
def findListPort(dicts, lists):
    port_numbers = []
    for list in dicts:
        for name in lists:
            if list["router-name"] == name:
                port_numbers.append(list["server-port"])
    return port_numbers

# i = list, list | o = routing_table
# def pullSelfSubnet(subnet, cost):

def reset_routing_table():
    global routing_table
    routing_table = []  # Resetting the routing table
    threading.Timer(60, reset_routing_table).start()  # Restart the timer for the next reset
    print("Routing table reset Routing table reset Routing table reset Routing table reset Routing table reset")

    

def server(serverIP, clientPort):
    global routing_table
    global sendData
    global onlineRouter_input
    thisRouter = []

    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind((serverIP, clientPort))
    print(f"ServerT => Router {clientPort} is ready to receive")
    reset_routing_table()
    
    while True:
        global routerSubnet
        message, addr = server_socket.recvfrom(1024)
        print(f"ServerT => Received from Router {clientPort}: {message.decode()}")

        # Splitting the text by '|'
        sentence = json.loads(message.decode())
        network_list, network_name = sentence.split('|')

        #Transfer string -> list
        network_list = ast.literal_eval(network_list)
        network_name = ast.literal_eval(network_name)
        # print(f"serverT => {network_list}")
        # print(f"serverT => {network_name}")

        print_routing()
        
        #reset
        # time.sleep(sleep_time)
        

        #put subnet own subnet in
        for r in router_initial:
            # print(r["router-name"])
            if r["router-name"] == onlineRouter_input:
                thisRouter.append(r)
                # print(thisRouter)
        
        for router in thisRouter:
            for i in router["con-network"]:
                subnet = i
                next_hop = "-"
                cost = 1
                new_item = [subnet, next_hop, cost]
                routing_table.append(new_item)
        
        #put subnet from friend in
        for j in network_list:
            #fix count to infinity
            if j[1] is not onlineRouter_input:
                subnet_friend = j[0]
                next_hop_friend = network_name[0]
                cost_friend = j[2] + 1
                new_item_friend = [subnet_friend, next_hop_friend, cost_friend]
                routing_table.append(new_item_friend)

        #delete Duplicated subnet
        data_tuples = [tuple(row) for row in routing_table]
        unique_data_tuples = set(data_tuples)
        routing_table = [list(row) for row in unique_data_tuples]
        routing_table.sort(key=lambda x: x[2])

        #delete higher cost
        lowest_cost = {}
        for row in routing_table:
            dest_subnet = row[0]
            cost = row[2]
            if dest_subnet not in lowest_cost:
                lowest_cost[dest_subnet] = cost
            else:
                lowest_cost[dest_subnet] = min(lowest_cost[dest_subnet], cost)
        routing_table = [row for row in routing_table if row[2] == lowest_cost[row[0]]]
        
        #subnet same, cost same => delete one of them
        unique_combinations = set()
        for item in routing_table:
            item_tuple = (item[0], item[2])# Convert the relevant elements to a tuple
            
            if item_tuple in unique_combinations: # If the tuple is already in the set, remove the item
                routing_table.remove(item)
            else:
                unique_combinations.add(item_tuple) # Add the tuple to the set
        
        for route in routing_table:
            if route[2] > 15:
                routing_table.remove(route)

        # print(routing_table)

        # print(f"serverT => {routing_table} | {selfName(online_list)}")
        sendData = str(routing_table) + "|" + str(selfName(online_list))  
        continue
    
def main():
    global sendData
    global routing_table
    global routerSubnet
    global onlineRouter_input
    onlineRouter_input = input("Main => Enter name of router: ")
    if find_router(router_initial, onlineRouter_input):
        routerSubnet = selfSubnet(online_list)
        generate_routing_table(routerSubnet)
        update_subnet(routerSubnet)
        selfName(online_list)

        nameList = findLinkName(online_list)
        linked_ports = findListPort(router_initial, nameList) #find port of link, use used in Client

        connectionList = getConnection(online_list)
        
        # print(f"main => {routing_table} | {selfName(online_list)}")
        sendData = str(routing_table) + "|" + str(selfName(online_list))  
    else:
        print("No such router in the list.")
    for router in online_list:
        server_thread = threading.Thread(target=server, args=(IP_host, router["server-port"],))
        server_thread.start()

        time.sleep(sleep_time)
        
        for conn, port in zip(connectionList, linked_ports):
            conn = int(conn)
            client_thread = threading.Thread(target=client, args=(list_ip[conn] ,port, router["con-network"]))
            client_thread.start()


if __name__ == "__main__":
      main()