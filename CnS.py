from socket import *
import numpy as np
import threading
import json
import time
import ast


hostname = gethostname()
IP_host = gethostbyname(hostname)
print("My IP Address:" + IP_host)
list_ip = [str(IP_host), "192.168.195.38"]

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

# List Con-network
listConNetwork = []
# RouterName
tempRouterName = ""

router_initial = [
        {
            "router-name": "A",
            "link": ["B", "C"],
            "cost-link": [1, 1],
            "server-port": 1024,
            "con-network": ["192.168.4.0/24", "192.168.4.1/24"]
        },
        {
            "router-name": "B",
            "link": ["A", "D", "C"],
            "cost-link": [1, 1, 1],
            "server-port": 1025,
            "con-network": ["192.168.2.0/24"]
        },
        {
            "router-name": "C",
            "link": ["B", "F"],
            "cost-link": [1, 1],
            "server-port": 1026,
            "con-network": ["192.168.3.0/24"]
        }
    ]

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
    while True:
        client_socket = socket(AF_INET, SOCK_DGRAM)
        message = json.dumps(sendData).encode()
        client_socket.sendto(message, (clientIP, clientPort))
        # print(f"ClientT => {message} to {clientIP} at {clientPort}")
        client_socket.close()
        time.sleep(5)

    # def splitMsg(massage):

def findLinkName(lists):
    for list in lists:
        return list["link"]

# i = dicts, lists | O = List of port
def findListPort(dicts, lists):
    port_numbers = []
    for list in dicts:
        if list["router-name"] in lists:
            port_numbers.append(list["server-port"])
    return port_numbers

# i = list, list | o = routing_table
# def pullSelfSubnet(subnet, cost):
    

def server(serverIP, clientPort):
    global tempRouterName
    global listConNetwork

    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind((serverIP, clientPort))
    print(f"ServerT => Router {clientPort} is ready to receive")
    
    while True:
        global routing_table
        listConNetwork = []
        message, addr = server_socket.recvfrom(1024)
        print(f"ServerT => Received from Router {clientPort}: {message.decode()}")

        # Splitting the text by '|'
        sentence = (message.decode())
        network_list, network_name = sentence.split('|')
        network_list = network_list[1:]
        network_name = network_name[:-1]

        #Transfer string -> list
        network_list = ast.literal_eval(network_list)
        network_name = ast.literal_eval(network_name)
        print(f"serverT => {network_list[0]}")
        print(f"serverT => {network_name}")

        # routing_table = []
        # pullSelfRouting(routerSubnet, )
        # pullFriendRouting()

        # Add info from other router to routing_table+
        # for list in listConNetwork:
        #     newRoutingInfo = list
        #     routing_table.append(newRoutingInfo)

        # Assuming received message contains the routing table data in JSON format
        recvData = json.loads(message.decode())
        print_routing()
        continue

def main():
    global sendData
    global routing_table
    onlineRouter_input = input("Main => Enter name of router: ")
    if find_router(router_initial, onlineRouter_input):
        routerSubnet = selfSubnet(online_list)
        generate_routing_table(routerSubnet)
        update_subnet(routerSubnet)
        selfName(online_list)

        nameList = findLinkName(online_list)
        linked_ports = findListPort(router_initial, nameList) #find port of link, use used in Client
        
        print(f"main => {routing_table} | {selfName(online_list)}")
        sendData = str(routing_table) + "|" + str(selfName(online_list))
        

    else:
        print("No such router in the list.")

    for router in online_list:
        server_thread = threading.Thread(target=server, args=(IP_host, router["server-port"],))
        server_thread.start()

        time.sleep(1)
        
        for port in linked_ports:
            client_thread = threading.Thread(target=client, args=(IP_host ,port, router["con-network"]))
            client_thread.start()

if __name__ == "__main__":
      main()