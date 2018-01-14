import socket
import time
import ssl
from tkinter import *
from tkinter.scrolledtext import *
from threading import Thread

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
            if text[0] == "/":
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
		
        self.pack()
        self.createWidgets()

class Connect(Frame):
    def createWidgets(self):
        self.IPFrame = Frame(self)
        self.IPFrame.pack()

        self.PortFrame = Frame(self)
        self.PortFrame.pack()

        self.ButtonFrame = Frame(self)
        self.ButtonFrame.pack()

        self.ipLabel = Label(self.IPFrame)
        self.ipLabel['text'] = "IP: "

        self.ip = StringVar()
        self.ipEntry = Entry(self.IPFrame, var = self.ip)

name = input("Name: ")
host = input("Host: ")
port = int(input("Port (default 25565): ") or 25565)

s = ssl.wrap_socket(socket.socket(), ciphers='SHA1')

s.settimeout(3)
try:
    s.connect((host, port))
except:
    print("Could not connect to server.")
	
connectionAlive = True

s.send(bytes(name.encode('utf-8'))) # send name

timeFormat = '{:%Y-%m-%d %H:%M:%S}'

def receive():
    global s, connectionAlive, chat, tk
    print(connectionAlive)
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
    tk.destroy()
    print("Connection closed")

receiverThread = Thread(target=receive)
receiverThread.daemon = True
receiverThread.start()

tk = Tk(screenName='Chat')
tk.geometry('400x300')
chat = Chat(master=tk)
chat.mainloop()
try:
    tk.destroy()
except: pass
connectionAlive = False

s.close()
input("Press enter to close.")