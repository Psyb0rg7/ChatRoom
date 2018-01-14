import socket
import time
import ssl
from threading import Thread

serverOn = True
clients = []
threads = []

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
		global clients
		while self.connectionAlive:
			try:
				new = self.socket.recv(1024).decode('utf-8')
				if new == '?=HB':
					time.sleep(0.2)
					self.socket.send(b'?=HB')
				elif new[:2] == 'M=':
					sendToAll(clients, "M=%s : %s" % (self.name, new[2:]))
			except:
				print("Connection closed:", self.addr)
				self.connectionAlive = False
				self.socket.close()
				clients.remove(self)
				sendToAll(clients, 'M=%s left the chat.' % self.name)
def sendToAll(clients, message):
	for client in clients:
		client.socket.send(bytes(message.encode('utf-8')))
s = ssl.wrap_socket(socket.socket(), ciphers='SHA1')
host = socket.gethostname()
port = int(input("Port[default 25565]:"))
print("Your hostname:", host)

s.bind((host, port))
s.listen(5)

while True:
	c,addr = s.accept()
	print("Got connection from",addr)
	c.settimeout(3)
	clients.append(Client(c,addr))
sendToAll(clients, "?=QUIT")
print("Everyone left, closing server...")
s.close()
input("Press enter to close.")