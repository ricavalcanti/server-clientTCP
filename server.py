#!/usr/bin/env python3

# Falta
# Clientes conectados solicitada na tela do servidor
# Encerrar todos os clientes ao fechar o server
# Corrigir bugs
# Implementar protocolo
"""Server for multithreaded (asynchronous) chat application."""
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread


def accept_incoming_connections():
    while True:
        client, client_address = SERVER.accept()
        print("%s:%s se conectou." % client_address)
        client.send(
            bytes("Digite seu nome e aperte enter.", "utf8"))
        addresses[client] = client_address
        Thread(target=handle_client, args=(client,)).start()


def handle_client(client):
    isPrivate = False
    myPrivateClient = None
    name = client.recv(BUFSIZ).decode("utf8")
    welcome = 'Bem vindo %s!' % name
    client.send(bytes(welcome, "utf8"))
    msg = "%s se juntou ao chat!" % name
    broadcast(bytes(msg, "utf8"))
    clients[client] = name

    while True:
        msg = client.recv(BUFSIZ)
        if msg != bytes("sair()", "utf8"):
            if isPrivate:
                if msg == bytes("sairPrivado()", "utf8"):
                    if len(privateChats) == 0:
                        isPrivate = False
                        myPrivateClient = None
                    else:
                        client.send(bytes('Saindo da sala privada...', "utf8"))
                        myPrivateClient.send(bytes(
                            'Usuario saiu da sala privada', "utf8"))
                        isPrivate = False
                        myPrivateClient = None
                        del privateChats[client]
                else:
                    myPrivateClient.send(
                        bytes(name+" escreveu(privado): ", "utf8")+msg)
            elif msg == bytes("{S}", "utf8"):
                isPrivate = True
                myPrivateClient = privateChats[client]
                myPrivateClient.send(
                    bytes("Voce esta em um chat privado", "utf8"))
                client.send(bytes("Voce esta em um chat privado", "utf8"))
            elif msg == bytes("{n}", "utf8"):
                privateChats[client].send(
                    bytes("Usuario recusou chat privado", "utf8"))
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
            broadcast(bytes("%s saiu da sala." % name, "utf8"))
            break


def broadcast(msg, prefix=""):  # prefix is for name identification.
    for sock in clients:
        sock.send(bytes(prefix, "utf8")+msg)


clients = {}
addresses = {}
privateChats = {}

HOST = ''
PORT = 12000
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
