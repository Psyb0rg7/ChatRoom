import socket
import time
import ssl
from tkinter import *
from tkinter.scrolledtext import *
from threading import Thread

timeFormat = '{:%Y-%m-%d %H:%M:%S}'
class ConnectWindow(Frame):
	def connect(self):
		global s, connectionAlive, chat, tk
		s = ssl.wrap_socket(socket.socket(), ciphers='SHA1')
		s.settimeout(3)
		host = self.ipText.get()
		port = int(self.portText.get())
		
		try:
			s.connect((host, port))
		except:
			print("Could not connect to server.")
		
		connectionAlive = True
		s.send(bytes(self.name.get().encode('utf-8')))
		tk.quit()
		chat.tkraise()
	def createWidgets(self):
		self.ipText = StringVar()
		self.ipInput = Entry(self, textvariable = self.ipText)
		self.ipText.set('173.66.160.91')
		self.ipInput.pack()
		
		self.portText = StringVar()
		self.portInput = Entry(self, textvariable = self.portText)
		self.portText.set('25565')
		self.portInput.pack()
		
		self.name = StringVar()
		self.nameInput = Entry(self, textvariable = self.name)
		self.nameInput.pack()
		
		self.connectButton = Button(self)
		self.connectButton['text'] = 'Connect'
		self.connectButton['fg'] = 'green'
		self.connectButton['command'] = self.connect
		self.connectButton.pack()
	def __init__(self, master=None):
		Frame.__init__(self, master)
		master.title("Connect to chatroom")
		
class Chat(Frame):
	def addMessage(self, text):
		self.messages.config(state=NORMAL)
		self.messages.insert(END, text)
		self.messages.config(state=DISABLED)
		self.messages.see('end')
	def sendMessageEvent(self, event):
		self.sendMessage()
	def sendMessage(self):
		global s
		text = self.entryText.get()
		if len(text) > 0:
			if text[0] == '/':
				print(b'C=' + bytes(text[1:].encode('utf-8')))
				s.send(b'C=' + bytes(text[1:].encode('utf-8')))
			else:
				s.send(b'M=' + bytes(text.encode('utf-8')))
		self.entryText.set('')
	def createWidgets(self):
		
		self.messages = ScrolledText(self, height=15, width=30)
		self.messages.config(state=DISABLED)
		self.messages.pack({'side':'right'})
		
		self.entryText = StringVar()
		self.INP = Entry(self, textvariable = self.entryText)
		self.INP.pack()
		self.INP.bind('<Return>', self.sendMessageEvent)
		
		self.SEND = Button(self)
		self.SEND['text'] = 'SEND'
		self.SEND['fg'] = 'green'
		self.SEND['command'] = self.sendMessage
		self.SEND.pack({'side':'left'})
		
		self.QUIT = Button(self)
		self.QUIT['text'] = 'QUIT'
		self.QUIT['fg'] = 'red'
		self.QUIT['command'] = self.quit
		self.QUIT.pack({'side':'right'})
		
	def __init__(self, master=None):
		Frame.__init__(self, master)
		master.title("Chat")
def receive():
	global s, connectionAlive, chat
	while connectionAlive:
		try:
			new = s.recv(1024).decode('utf-8') # received message
			if new == '?=HB': # if heartbeat message:
				time.sleep(0.2)
				s.send(b'?=HB')
			elif new == '?=QUIT':
				connectionAlive = False
				s.close()
			elif new[:2] == 'M=':
				chat.addMessage(new[2:] + "\n")
		except:
			connectionAlive = False
			s.close()
			try:
				tk.destroy()
			except: pass
	print("Connection closed")

tk = Tk(screenName='Chat')
tk.geometry('400x400')
connect = ConnectWindow(master=tk)
chat = Chat(master=tk)
connect.tkraise()
connect.pack()
connect.createWidgets()
connect.mainloop()

receiverThread = Thread(target=receive)
receiverThread.daemon = True
receiverThread.start()

chat.pack()
chat.createWidgets()
chat.mainloop()
try:
	tk.destroy()
except: pass
connectionAlive = False

s.close()
input("Press enter to close.")