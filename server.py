#!/usr/bin/env python3

# Falta
# Clientes conectados solicitada na tela do servidor
# Encerrar todos os clientes ao fechar o server
# implementar chat privado
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s has connected." % client_address)
        client.send(
            bytes("Greetings from the cave! Now type your name and press enter!", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):
    isPrivate = False
    myPrivateClient = None
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Welcome %s! If you ever want to quit, type sair() to exit.' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s has joined the chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("sair()", "utf8"):
            if isPrivate:
                if msg == bytes("sairPrivado()", "utf8"):
                    client.send(bytes('Saindo da sala privada...', "utf8"))
                    myPrivateClient.send(bytes('Usuario saiu da sala privada, voce esta sozinho. Digite sairPrivado()', "utf8"))
                    isPrivate = False
                    myPrivateClient = None
                    #falta limpar dict
                else:
                    myPrivateClient.send(bytes(name+" escreveu(privado): ", "utf8")+msg)
            elif msg == bytes("{S}", "utf8"):
                isPrivate = True
                myPrivateClient = privateChats[client]
                del privateChats[client]
                myPrivateClient.send(
                    bytes("Voce esta em um chat privado", "utf8"))
                client.send(bytes("Voce esta em um chat privado", "utf8"))
            elif msg == bytes("{n}", "utf8"):
                privateChats[client].send(bytes("Usuario recusou chat privado", "utf8"))
                del privateChats[client]
            elif msg == bytes("lista()", "utf8"):
                msg = ""
                for client in clients:
                    port, ip = addresses[client]
                    infoClient = "<" + clients[client] + \
                        ", " + str(ip) + ", " + str(port) + ">"
                    msg = msg + infoClient
                broadcast(bytes(msg, "utf8"))
            elif(((msg.decode("utf8"))).find("privado(") != -1):
                isPrivate = True
                otherClientName = msg.decode("utf8")[8:].replace(')', '')
                for otherClient, userName in clients.items():
                    if(userName == otherClientName):
                        print(userName)
                        print(name)
                        otherClient.send(
                            bytes("Iniciar chat privado? {S/n}", "utf8"))
                        privateChats[otherClient] = client
                        myPrivateClient = otherClient

            elif(((msg.decode("utf8"))).find("nome(") != -1):
                newName = msg.decode("utf8")[5:].replace(')', '')
                name = newName
                clients[client] = newName
            else:
                broadcast(msg, name+" escreveu: ")
        else:
            client.send(bytes("sair()", "utf8"))
            client.close()
            del clients[client]
            del addresses[client]
            broadcast(bytes("%s has left the chat." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)


clients = {}
addresses = {}
privateChats = {}
isPrivate = {}
dNames = {}
dClientsInfo = []

HOST = ''
PORT = 12001
BUFSIZ = 1024
ADDR = (HOST, PORT)

SERVER = socket(AF_INET, SOCK_STREAM)
SERVER.bind(ADDR)

if __name__ == "__main__":
    SERVER.listen(5)
    print("Waiting for connection...")
    ACCEPT_THREAD = Thread(target=accept_incoming_connections)
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    SERVER.close()
