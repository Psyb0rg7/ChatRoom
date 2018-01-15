import socket
import time
import ssl
from tkinter import *
from tkinter.scrolledtext import *
from threading import Thread
from tkinter import messagebox

class NewServer(Frame):
    def createEvent(self, event):
        self.createServer()

    def createServer(self):
        if self.name.get() == '' or self.ip.get() == '':
            messagebox.showerror("ERROR", "Please fill out all fields!")
        elif not all(i == '.' or i.isnumeric() for i in self.ip.get()) or self.ip.get().count(".") != 3:
            messagebox.showerror("ERROR", "Invalid IP!")
        elif not self.port.get().isnumeric() and not self.port.get() == '':
            messagebox.showerror("ERROR", "Port must be number or empty!")
        else:
            serverFile = open("servers.txt", "a")
            serverFile.write("N=" + self.name.get() + "\n")
            serverFile.write("IP=" + self.ip.get() + ":" + (self.port.get() or "27755") + "\n")
            self.quit()

    def createWidgets(self):
        self.InputFrame = Frame(self)
        self.LabelFrame = Frame(self.InputFrame)
        self.EntryFrame = Frame(self.InputFrame)
        self.ButtonFrame = Frame(self)

        self.InputFrame.pack(side=TOP)
        self.LabelFrame.pack(side=LEFT)
        self.EntryFrame.pack(side=RIGHT)
        self.ButtonFrame.pack(side=BOTTOM)

        self.nameLabel = Label(self.LabelFrame, text="Name: ")
        self.ipLabel = Label(self.LabelFrame, text="IP: ")
        self.portLabel = Label(self.LabelFrame, text="Port (default 27755): ")

        self.nameLabel.pack()
        self.ipLabel.pack()
        self.portLabel.pack()

        self.name = Entry(self.EntryFrame)
        self.ip = Entry(self.EntryFrame)
        self.port = Entry(self.EntryFrame)

        self.name.pack()
        self.ip.pack()
        self.port.pack()

        self.name.bind("<Return>", self.createEvent)
        self.ip.bind("<Return>", self.createEvent)
        self.port.bind("<Return>", self.createEvent)

        self.CREATE = Button(self.ButtonFrame, text="CREATE", fg="blue", command=self.createServer)
        self.CANCEL = Button(self.ButtonFrame, text="CANCEL", fg="red", command=self.quit)

        self.CREATE.pack(side=LEFT)
        self.CANCEL.pack(side=RIGHT)

    def __init__(self, master=None):
        Frame.__init__(self, master)

        master.protocol("WM_DELETE_WINDOW", self.quit)

        self.pack()
        self.createWidgets()

class Chat(Frame):
    def leave(self):
        global connectionAlive, s
        connectionAlive = False
        s.send(b'C=leave')
        self.quit()

    def exit(self):
        global goBack
        self.leave()
        goBack = False

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
                if text == '/leave':
                    self.leave()
            else:
                s.send(b'M=' + bytes(text.encode('utf-8')))
        self.entryText.set('')

    def createWidgets(self):
        self.messages = ScrolledText(self, height=15, width=30)
        self.messages.config(state=DISABLED)

        self.entryText = StringVar()
        self.INP = Entry(self, textvariable = self.entryText)

        self.SEND = Button(self, text="SEND", fg="green", command=self.sendMessage)
        self.QUIT = Button(self, text="QUIT", fg="red", command=self.leave)

        self.messages.pack(side=RIGHT)
        self.INP.pack()
        self.SEND.pack(side=LEFT)
        self.QUIT.pack(side=RIGHT)

        self.INP.bind('<Return>', self.sendMessageEvent)

    def __init__(self, master=None):
        Frame.__init__(self, master)

        master.protocol("WM_DELETE_WINDOW", self.exit)

        self.pack()
        self.createWidgets()

class Connect(Frame):
    def clear_servers(self):
        if messagebox.askokcancel("Clear Servers", "Are you sure you want to clear all the servers (Cannot be undone)"):
            serverFile = open("servers.txt", "w")
            self.updateServers(0)

    def new_server(self):
        newServerRoot = Tk(screenName="New Server")
        newServerRoot.title("New Server")
        newServer = NewServer(master=newServerRoot)
        newServer.mainloop()
        newServerRoot.destroy()
        self.updateServers(-1)

    def updateServers(self, index=None):
        serverFile = open("servers.txt", "r")
        lines = serverFile.readlines()
        self.servers = ["Enter Manually"]
        self.serverIPs = {}
        for l in range(len(lines)):
            line = lines[l].rstrip()
            if line[:2] == "N=":
                self.servers.append(line[2:])
                self.serverIPs[line[2:]] = lines[l + 1][3:]
        serverMenu = self.serverDropdown["menu"]
        serverMenu.delete(0, "end")
        for server in self.servers:
            serverMenu.add_command(label=server, command=lambda value=server:self.server.set(value))

        if index is not None:
            self.server.set(self.servers[index])

    def connectEvent(self, event):
        self.connect()

    def connect(self):
        global s, cont
        if self.server.get() == "Enter Manually":
            try:
                if self.ip.get() == '' or self.name.get() == '':
                    messagebox.showerror("ERROR", "Enter all fields!")
                elif self.port.get() != '' and not self.port.get().isnumeric():
                    messagebox.showerror("ERROR", "Port must be a nubmer or empty!")
                elif not all(i.isnumeric() or i == "." for i in self.ip.get()) or self.ip.get().count(".") != 3:
                    messagebox.showerror("ERROR", "Invalid IP!")
                else:
                    s.connect((self.ip.get(), int(self.port.get() or 27755)))
                    s.send(bytes(self.name.get().encode("utf-8")))
                    cont = True
                    self.quit()
            except:
                messagebox.showerror("Failed to connect", "Could not connect to server.")
        else:
            try:
                if self.name.get() == '':
                    messagebox.showerror("ERROR", "Please enter a username!")
                else:
                    ip, port = self.serverIPs[self.server.get()].split(":")
                    port = int(port)
                    s.connect((ip, port))
                    s.send(bytes(self.name.get().encode('utf-8')))
                    cont = True
                    self.quit()
            except:
                messagebox.showerror("Failed to connect", "Could not connecto to server.")

    def createWidgets(self):
        self.InputFrame = Frame(self)
        self.LabelFrame = Frame(self.InputFrame)
        self.EntryFrame = Frame(self.InputFrame)
        self.ServerFrame = Frame(self)
        self.ButtonFrame = Frame(self)

        self.InputFrame.pack(side=TOP)
        self.LabelFrame.pack(side=LEFT)
        self.EntryFrame.pack(side=RIGHT)
        self.ButtonFrame.pack(side=BOTTOM)
        self.ServerFrame.pack(side=BOTTOM)

        self.name = Entry(self.EntryFrame)
        self.ip = Entry(self.EntryFrame)
        self.port = Entry(self.EntryFrame)

        self.name.pack()
        self.ip.pack()
        self.port.pack()

        self.name.bind("<Return>", self.connectEvent)
        self.ip.bind("<Return>", self.connectEvent)
        self.port.bind("<Return>", self.connectEvent)

        self.userLabel = Label(self.LabelFrame, text="Username: ")
        self.ipLabel = Label(self.LabelFrame, text="IP: ")
        self.portLabel = Label(self.LabelFrame, text="Port (Default 27755): ")

        self.userLabel.pack()
        self.ipLabel.pack()
        self.portLabel.pack()

        self.CONNECT = Button(self.ButtonFrame, text="CONNECT", fg="blue", command=self.connect)
        self.QUIT = Button(self.ButtonFrame, text="QUIT", fg="red", command=self.quit)

        self.CONNECT.pack(side=LEFT)
        self.QUIT.pack(side=RIGHT)

        self.server = StringVar()
        self.serverDropdown = OptionMenu(self.ServerFrame, self.server, ())
        self.serverDropdown.pack(side=LEFT)
        self.updateServers(0)

        self.NEW_SERVER = Button(self.ServerFrame, text="NEW SERVER", command=self.new_server)
        self.CLEAR_SERVERS = Button(self.ServerFrame, text="CLEAR SERVERS", command=self.clear_servers)

        self.CLEAR_SERVERS.pack(side=RIGHT)
        self.NEW_SERVER.pack(side=RIGHT)

    def __init__(self, master = None):
        Frame.__init__(self, master)

        self.pack()
        self.createWidgets()

def receive():
    global s, connectionAlive, chat
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
    print("Connection closed.")

connectRoot = connect = chatRoot = chat = None
def connectWindow():
    global connectRoot, connect
    connectRoot = Tk(screenName="Connect")
    connectRoot.title("Connect")
    connectRoot.geometry('350x150')
    connect = Connect(master = connectRoot)
    connect.mainloop()

def chatWindow():
    global chatRoot, chat
    chatRoot = Tk(screenName='Chat')
    chatRoot.title("Chat")
    chatRoot.geometry('400x300')
    chat = Chat(master=chatRoot)
    chat.mainloop()

goBack = True
while goBack:
    s = ssl.wrap_socket(socket.socket(), ciphers='SHA1')

    s.settimeout(3)
    cont = False

    connectWindow()
    if not cont:
        print("Application stopped.")
        exit()

    connectRoot.destroy()

    connectionAlive = True

    timeFormat = '{:%Y-%m-%d %H:%M:%S}'

    receiverThread = Thread(target=receive)
    receiverThread.daemon = True
    receiverThread.start()

    chatWindow()

    connectionAlive = False

    s.close()
    chatRoot.destroy()

    receiverThread.join()
input("Press Enter to close.")