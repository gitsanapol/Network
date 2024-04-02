import time
import threading
import socket
import select
import errno
import sys
import datetime 
import json

hostname = socket.gethostname()
IP_host = socket.gethostbyname(hostname)
print("My IP Address:" + IP_host)
list_ip = [str(IP_host), "192.168.195.38"] #config
list_port = list(range(1024, 1100))

clients = {}
routing_table = []
routing_msg = ""
router_name = ""
router_list_name = []
sockets_list = []
array_client = []
numClient_list = []
disconnect = [] 

 
def get_router_profile():
    with open('router_profile.txt') as file:
        data = json.load(file)
    return data

router_initial = get_router_profile()

def print_routing():
    print("|  Dest. Subnet  |   Next hop   |     Cost     |")
    print("------------------------------------------------")
    for i in range(len(routing_table)):
        print("|", routing_table[i][0], "|      ", routing_table[i][1], "     |      ", routing_table[i][2], "     |")


def update_routing(message, user): 
    global routing_msg
    global routing_table
   
    message = message[:-1]
    for i in range(int(len(message)) - 1):
        arr = message[(i + 1)].split("|")
        count = 0
        for j in range(len(routing_table)):
            if routing_table[j][0] != arr[0]:
                count += 1
            elif (routing_table[j][0] == arr[0]) & (int(routing_table[j][2]) > (int(arr[2]) + 1)):
                routing_table[j][1] = str(user)
                routing_table[j][2] = str(int(arr[2]) + 1)
            if count == len(routing_table):
                if arr[0] != '':
                    routing_table.append([str(arr[0]), str(user), str(int(arr[2]) + 1)])
                else:
                    break
    routing_msg = ""
    for i in range(len(routing_table)):
        if i == (len(routing_table)) - 1:
            routing_msg += routing_table[i][0] + "|" + routing_table[i][1] + "|" + routing_table[i][2] + ":"
        else:
            routing_msg += routing_table[i][0] + "|" + routing_table[i][1] + "|" + routing_table[i][2] + ":"
    print(routing_msg)


def send_routing(message):
    global clients
    global array_client
    arr_socket = list(clients.keys())
    for socket_client in arr_socket:
        if not disconnect:
            socket_client.send(message.encode())
        else:
            if disconnect[0] != socket_client:
                socket_client.send(message.encode())
            else:
                print("disconnect[0] == socket_client")
    array_client = list(clients.values())


def edit_routing(): 
    global array_client
    global routing_table
    global routing_msg
    global router_name
    global clients
    arr = list(clients.values())
    #arr_socket = list(clients.keys())
    
    temp_routing_table = []
    count = 0
    for i in range(len(routing_table)):
        for j in range(len(arr)):
            arr_split = arr[j].split(":")
            if (routing_table[i][1] != arr_split[0]) and (routing_table[i][1] != "-"):
                temp_routing_table.append(i)
    # print(temp_routing_table)
    count = 0
    final_temp_routing_table = list(dict.fromkeys(temp_routing_table))
    for i in final_temp_routing_table:
        if count == 0:
            # print(i)
            del routing_table[i]
            count += 1
        elif (count > 0) and (count < len(final_temp_routing_table)):
            # print(i - count)
            routing_table.remove(routing_table[(i - count)])
            count += 1

    array_client = arr
    routing_msg = ""
    for l in range(len(routing_table)):
        if l == (len(routing_table)) - 1:
            routing_msg += routing_table[l][0] + "|" + routing_table[l][1] + "|" + routing_table[l][2] + ":"
        else:
            routing_msg += routing_table[l][0] + "|" + routing_table[l][1] + "|" + routing_table[l][2] + ":"
    # print_routing()
    # print(clients, array_client, routing_msg)
    if len(clients) != 0:
        message_routing = str(router_name + ":" + routing_msg)
        send_routing(message_routing)

def receive_message(client_socket):
    global message
    try:
        message = client_socket.recv(2048)

        if not len(message):
            return False

        return message.decode('utf-8')

    except:
        return False

def server_process(IP, PORT):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((IP, PORT))
    server_socket.listen()
    global clients
    global routing_msg
    global router_name
    global sockets_list
    global array_client
    sockets_list = [server_socket]

    print(f'Waiting for connection on {IP}:{PORT}...')


    while True:
        read_sockets, _, exception_sockets = select.select(sockets_list, [], sockets_list)
        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                message = receive_message(client_socket)
                if message is False:
                    continue
                message_split = message.split(":")
                sockets_list.append(client_socket)
                clients[client_socket] = message_split[0]
                print('Accepting new connection from {}:{}, username: {}'.format(*client_address, message_split[0]))
            else:
                message = receive_message(notified_socket)
                if message is False:
                    print('Connection Loss from : {}'.format(clients[notified_socket]))
                    sockets_list.remove(notified_socket)
                    del clients[notified_socket]
                    edit_routing() #แก้
                    continue
                user = clients[notified_socket]
                message_rcv = message.split(":")
                if (message_rcv[0] == "RoutingTable") | (message_rcv[0] in array_client):
                    print(f'Received message from {user}: {message}')
                    update_routing(message_rcv, user)
                    print_routing()
                    message_routing = str(router_name + ":" + routing_msg + ":")
                    send_routing(message_routing)

        for notified_socket in exception_sockets:
            sockets_list.remove(notified_socket)
            del clients[notified_socket]
            edit_routing()


def client_process(IP, PORT, user_name):
    time_send = 4
    global routing_msg
    global array_client
    global clients
    global disconnect
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((IP, PORT))
    clients[client_socket] = user_name  # ADD
    client_socket.setblocking(False)
    user_name = str(user_name + ":")
    client_socket.send(user_name.encode('utf-8'))
    time.sleep(1)
    message = "RoutingTable:" + routing_msg + ":"
    client_socket.send(message.encode('utf-8'))
    clients[client_socket] = user_name
    print("ip " + str(IP) + "PORT " + str(PORT) + "NAME " + str(user_name))

    while True:

        print("ip " + str(IP) + "PORT " + str(PORT) + "NAME " + str(user_name) + " TIME :" + str(
            time.strftime("%H:%M:%S", time.gmtime(time.time()))))
        message = routing_msg + ":"
        if message:
            message = message
            time.sleep(time_send)
            # time.sleep(5)
            try:
                client_socket.send(message.encode('utf-8'))
            except IOError as e:
                disconnect = []
                print('Reading error (Client-Send): {}'.format(str(e)))
                disconnect.append(client_socket)
                # ss = clients[client_socket]
                edit_routing()
                print_routing()
        try:
            while True:
                message = client_socket.recv(2048).decode('utf-8')
                message_split = message.split(":")
                message_split = message_split[:-1]
                final_message_split = list(dict.fromkeys(message_split))
                update_routing(final_message_split, final_message_split[0])
                print_routing()

        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error (Client-Receive): {}'.format(str(e)))
                time_send = time_send + 2
                # sys.exit()
            continue

        except Exception as e:
            print('Reading error: '.format(str(e)))
            n = len(sys.argv)
            print(n)
            print("\nName of Python script:", sys.argv[0])
            time_send = time_send + 5
            


def main():
    thread_list = []
    router = []
    numServer = 1
    global router_name
    global routing_table
    global routing_msg
    global numClient_list
    print("Initial Router (Server)\n")
    if (int(numServer) != 0):
        for i in range(int(numServer)):
            indexRouter = input("Index of Router : ")
            router = router_initial[int(indexRouter)]
            router_name = str(router["router-name"])
            router_list_name.append(router_name)
            server_port = int(router["server-port"])

            for j in range(len(router["con-network"])):
                routing_table.append([router["con-network"][j], "-", "1"])
                if j == (len(router["con-network"])) - 1:
                    routing_msg += router["con-network"][j] + "|-|1:"
                else:
                    routing_msg += router["con-network"][j] + "|-|1:"

            print(routing_table)
            print(routing_msg)
            print("Server Router name : ", router_name, " > ", list_ip[0], " port : ", server_port)
            thread = threading.Thread(target=server_process, args=(list_ip[0], server_port))
            thread_list.append(thread)

    numClient = input("Numbers of Client : ")
    numClient_list = numClient
    if (int(numClient) != 0):
        for i in range(int(numClient)):
            indexIP = input("Type of Network (0 = internal, 1 = external): ")
            while not int(indexIP) in range(0, 2):
                indexIP = input("Type of Network (0 = internal, 1 = external): ")
            indexPort = input("Index of Port : ")
            while not int(indexPort) in range(0, 100):
                indexPort = input("Index of Port: ")
            print("Client", i + 1, "Connect to ", list_ip[int(indexIP)], ":", list_port[(int(indexPort))], "\n")
            thread = threading.Thread(target=client_process,
                                      args=(list_ip[int(indexIP)], list_port[(int(indexPort))], router_name))
            thread_list.append(thread)

    for i in range((int(numClient) + int(numServer))):
        thread_list[i].start()
        time.sleep(0.5)


if __name__ == "__main__":
    main() 
       