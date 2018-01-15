import socket
import time
import ssl
import datetime
import select
from threading import Thread
from tkinter.scrolledtext import *
from tkinter import *
from tkinter import messagebox

serverOn = True
clients = []
threads = []

timeFormat = '{:%Y-%m-%d %H:%M:%S}'
class ServerGui(Frame):
    def exit(self):
        self.quit()
        self.master.destroy()
        self.exited = True
    def sendMessageEvent(self, event):
        self.sendMessage()
    def sendMessage(self):
        global clients
        sendMsgAll(clients, self.entryText.get())
        self.entryText.set('')
    def addWidgets(self):
        self.messages = ScrolledText(self, height=15, width=30)
        #self.messages.config(state=DISABLED)

        self.entryText = StringVar()
        self.INP = Entry(self, textvariable = self.entryText)

        self.SEND = Button(self, text="SEND", fg="green", command=self.sendMessage)
        self.messages.pack(side=RIGHT)
        self.INP.pack()
        self.SEND.pack(side=LEFT)

        self.INP.bind('<Return>', self.sendMessageEvent)
    def __init__(self, master=None):
        self.master = master
        Frame.__init__(self, master)
        self.pack()
        self.addWidgets()
class PortSelectionGui(Frame): 
    def exit(self, closeAll = True):
        self.quit()
        self.master.destroy()
        self.exited = closeAll
    def usePort(self):
        global port
        text = self.portText.get()
        if text.isnumeric():
            if 0 < int(text) <= 65535:
                port = int(text)
                self.exit(False) # Exit, but keep the program running
            else:
                messagebox.showinfo("ERROR", "Your port is not in range 0 - 65535")
        else:
            messagebox.showinfo("ERROR", "Your port is not numeric")
    def addWidgets(self):
        self.InputFrame = Frame(self)
        self.LabelFrame = Frame(self.InputFrame)
        self.EntryFrame = Frame(self.InputFrame)
        self.ButtonFrame = Frame(self)
        
        self.portText = StringVar()
        self.portInp = Entry(self.EntryFrame, textvariable=self.portText)
        
        self.portLabel = Label(self.LabelFrame)
        self.portLabel['text'] = 'Port to run on:'
        
        self.portButton = Button(self.ButtonFrame)
        self.portButton['text'] = 'Use Port'
        self.portButton['command'] = self.usePort
        
        self.portInp.pack()
        self.portLabel.pack()
        self.portButton.pack()
        
        self.InputFrame.pack(side=TOP)
        self.LabelFrame.pack(side=LEFT)
        self.EntryFrame.pack(side=RIGHT)
        self.ButtonFrame.pack(side=BOTTOM)
        
        self.EntryFrame.pack()
    def __init__(self, master = None):
        self.master = master
        Frame.__init__(self, master)
        self.exited = False
        self.pack()
        self.addWidgets()
        self.master.protocol("WM_DELETE_WINDOW", self.exit)
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
                    print(self.addr, self.name, ':', new[2:])
                    sendToAll(clients, "M=%s : %s" % (self.name, new[2:]))
                elif new[:2] == 'C=':
                    command = new[2:]
                    print(self.addr, self.name, ':', command)
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
    print("SEND")
    global serverGui
    serverGui.messages.insert(END, message[2:]+'\n')
    for client in clients:
        client.socket.send(bytes(message.encode('utf-8')))

def selectClients():
    global clients, keepListening, serverSocket
    while keepListening:
        time.sleep(1)
        try:
            if select.select([serverSocket],[],[]):
                c, addr = serverSocket.accept()
                print("Got connection from", addr)
        except:
            print('Error while selecting sockets')
            keepListening = False
keepListening = True
serverSocket = ssl.wrap_socket(socket.socket(), ciphers='SHA1')
host = socket.gethostname()
print("Your hostname:", host)

portTk = Tk(screenName='Server')
portTk.geometry('40x50')
portTk.title("Server %s" % host)

portGui = PortSelectionGui(master=portTk)

portGui.mainloop()

if portGui.exited: exit()

serverSocket.bind((host, port))
serverSocket.listen(5)

selectClientsThread = Thread(target=selectClients)
selectClientsThread.daemon = True
selectClientsThread.start()

serverTk = Tk(screenName='Server')
serverTk.geometry('300x400')
serverTk.title("Server %s:%s" % (host, port))

serverGui = ServerGui(master=serverTk)

serverGui.mainloop()

keepListening = False

serverSocket.close()
input("Press enter to close.")