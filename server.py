import socket
import time
import ssl
import datetime
from threading import Thread

serverOn = True
clients = []
threads = []

timeFormat = '{:%Y-%m-%d %H:%M:%S}'


def remove(client, *m):
    global clients
    client.connectionAlive = False
    client.socket.close()
    clients.remove(client)
    sendToAll(clients, 'M=%s left the chat.' % client.name)


def spam(client, *message):
    global clients
    for x in range(10):
        sendMsgAll(clients, client.name + ' : ' + ' '.join(message))


def birthday(client, *message):
    global clients
    sendMsgAll(clients,
               '%s: Happy birthday to you,\n%s: Happy birthday to you,\n%s: Happy birthday dear %s,\n%s: Happy birthday to you!' % (
               client.name, client.name, client.name, ' '.join(message), client.name))


def ctime(client, *a):
    client.socket.send(bytes(('M=[server] : ' + timeFormat.format(datetime.datetime.now())).encode('utf-8')))


commandMap = {'spam': spam, 'birthday': birthday, 'time': ctime, 'leave': remove}


class Client:
    def __init__(self, socket, addr):
        global threads, clients

        self.socket = socket
        self.addr = addr
        self.name = socket.recv(1024).decode('utf-8')  # receive a name
        self.connectionAlive = True
        self.thread = Thread(target=self.handle)
        threads.append(self.thread)
        self.thread.daemon = True
        self.thread.start()
        sendToAll(clients, '%s has joined the server!' % self.name)

    def handle(self):
        self.socket.send(b'?=HB')
        global clients, commandMap
        while self.connectionAlive:
            try:
                new = self.socket.recv(1024).decode('utf-8')
                if new == '?=HB':
                    time.sleep(0.2)
                    self.socket.send(b'?=HB')
                elif new[:2] == 'M=':
                    print(addr, self.name, ':', new[2:])
                    sendToAll(clients, "M=%s : %s" % (self.name, new[2:]))
                elif new[:2] == 'C=':
                    command = new[2:]
                    print(addr, self.name, ':', command)
                    csplit = command.split(' ')
                    function = csplit[0]
                    if function not in commandMap:
                        self.socket.send(b'M=[server] : That command does not exist')
                    elif len(csplit) > 1:
                        commandMap[function](self, *csplit[1:])
                    else:
                        commandMap[function](self)
            except:
                print("Connection closed:", self.addr)
                self.connectionAlive = False
                self.socket.close()
                clients.remove(self)
                sendToAll(clients, 'M=%s left the chat.' % self.name)


def sendMsgAll(clients, message):
    sendToAll(clients, 'M=' + message)


def sendToAll(clients, message):
    for client in clients:
        client.socket.send(bytes(message.encode('utf-8')))


def remove(client, *m):
	global clients
	client.connectionAlive = False
	client.socket.close()
	clients.remove(client)
	sendToAll(clients, 'M=%s left the chat.' % client.name)
def spam(client, *message):
	global clients
	for x in range(10):
		sendMsgAll(clients, client.name+' : '+' '.join(message))
def birthday(client, *message):
	global clients
	sendMsgAll(clients, '%s: Happy birthday to you,\n%s: Happy birthday to you,\n%s: Happy birthday dear %s,\n%s: Happy birthday to you!' %(client.name, client.name, client.name, ' '.join(message), client.name))
def ctime(client, *a):
	client.socket.send(bytes(('M=[server] : '+timeFormat.format(datetime.datetime.now())).encode('utf-8')))
commandMap = {'spam':spam, 'birthday':birthday, 'time':ctime, 'leave':remove}
class Client:
	def __init__(self, socket, addr):
		global threads, clients
		
		self.socket = socket
		self.addr = addr
		self.name = socket.recv(1024).decode('utf-8') # receive a name
		self.connectionAlive = True
		self.thread = Thread(target=self.handle)
		threads.append(self.thread)
		self.thread.daemon = True
		self.thread.start()
		sendToAll(clients, '%s has joined the server!' % self.name)
	def handle(self):
		self.socket.send(b'?=HB')
		global clients, commandMap
		while self.connectionAlive:
			try:
				new = self.socket.recv(1024).decode('utf-8')
				if new == '?=HB':
					time.sleep(0.2)
					self.socket.send(b'?=HB')
				elif new[:2] == 'M=':
					print(addr,self.name,':',new[2:])
					sendToAll(clients, "M=%s : %s" % (self.name, new[2:]))
				elif new[:2] == 'C=':
					command = new[2:]
					print(addr,self.name,':',command)
					csplit = command.split(' ')
					function = csplit[0]
					if function not in commandMap:
						self.socket.send(b'M=[server] : That command does not exist')
					elif len(csplit) > 1:
						commandMap[function](self, *csplit[1:])
					else:
						commandMap[function](self)
			except:
				print("Connection closed:", self.addr)
				self.connectionAlive = False
				self.socket.close()
				clients.remove(self)
				sendToAll(clients, 'M=%s left the chat.' % self.name)
def sendMsgAll(clients, message):
	sendToAll(clients, 'M=' + message)
def sendToAll(clients, message):

	for client in clients:
		client.socket.send(bytes(message.encode('utf-8')))
s = ssl.wrap_socket(socket.socket(), ciphers='SHA1')
host = socket.gethostname()
port = int(input("Port[default 25565]:") or 25565)
print("Your hostname:", host)

s.bind((host, port))
s.listen(5)

while True:
    c, addr = s.accept()
    print("Got connection from", addr)
    c.settimeout(3)
    clients.append(Client(c, addr))
    c,addr = s.accept()
    print("Got connection from",addr)
    c.settimeout(3)
    clients.append(Client(c,addr))

sendToAll(clients, "?=QUIT")
print("Everyone left, closing server...")
s.close()
input("Press enter to close.")