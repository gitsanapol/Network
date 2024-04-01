from socket import *

def server():
    serverPort = 1024
    serverSocket = socket(AF_INET, SOCK_STREAM)
    serverSocket.bind(('', serverPort))
    serverSocket.listen(1)
    print("The server is ready to receive")
    while True:
        connectionSocket, addr = serverSocket.accept()
        sentence = connectionSocket.recv(1024).decode()
        capitalizedSentence = sentence.upper()
        print("Server sent: " + capitalizedSentence)
        connectionSocket.send(capitalizedSentence.encode())
        connectionSocket.close()

def client():
    serverName = 'localhost'
    serverPort = 1024
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    sentence = input("Input lowercase sentence:")
    clientSocket.send(sentence.encode())
    modifiedSentence = clientSocket.recv(1024)
    print("From Server:", modifiedSentence.decode())
    clientSocket.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2 or sys.argv[1] not in ['client', 'server']:
        print("Usage: python combined_server_client.py [client|server]")
        sys.exit(1)

    if sys.argv[1] == 'client':
        client()
    else:
        server()