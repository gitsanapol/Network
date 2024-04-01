from socket import *
import numpy as np
import threading
import json

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

router_initial = [
        {
            "router-name": "A",
            "link": ["B", "C"],
            "server-port": 1024,
            "con-network": ["192.168.4.0/24", "192.168.4.1/24"]
        },
        {
            "router-name": "B",
            "link": ["A", "D", "C"],
            "server-port": 1025,
            "con-network": ["192.168.2.0/24"]
        },
        {
            "router-name": "C",
            "link": ["B", "F"],
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
        print("selfSubnet => " + str(routerName[0]))
        return routerName
    
  
# i = subnet | o = routing_table ---Help: selfSubnet
def update_subnet(subnet_array):
    global routing_table
    print(range(len(subnet_array)))
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
        # network, _, subnet_length = subnet.partition('/')
        routing_table.append([192, '-', 0])
    return routing_table

# i = routing_table | o = None
def print_routing():
    print("|  Dest. Subnet  |   Next hop   |     Cost     |")
    print("------------------------------------------------")
    for i in range(len(routing_table)):
        print("|", routing_table[i][0], "|      ", routing_table[i][1], "     |      ", routing_table[i][2], "     |")
    

def client(server_port, server_ip, con_network):
    client_socket = socket(AF_INET, SOCK_DGRAM)
    message = json.dumps(sendData).encode()#
    client_socket.sendto(message, (server_ip, server_port))
    client_socket.close()

def server(server_port):

    server_socket = socket(AF_INET, SOCK_DGRAM)
    server_socket.bind(('localhost', server_port))
    print(f"ServerT => Router {server_port} is ready to receive")
    
    while True:
        message, addr = server_socket.recvfrom(1024)
        print(f"ServerT => Received from Router {server_port}: {message.decode()}")
        # Assuming received message contains the routing table data in JSON format
        recvData = json.loads(message.decode())
        print_routing()
        continue

def main():
    global sendData
    onlineRouter_input = input("Main => Enter name of router: ")
    if find_router(router_initial, onlineRouter_input):
        selfSubnet(online_list)
        generate_routing_table(subnet)
        update_subnet(subnet)
        selfName(online_list)
        
        sendData = str(update_subnet(subnet)) + "|" + str(selfName(online_list))

    else:
        print("No such router in the list.")

    for router in online_list:
        server_thread = threading.Thread(target=server, args=(router["server-port"],))
        server_thread.start()
        
        client_thread = threading.Thread(target=client, args=(router["server-port"], 'localhost', router["con-network"]))
        client_thread.start()
    print("Main done")

if __name__ == "__main__":
      main()