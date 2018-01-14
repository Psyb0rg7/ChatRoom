import socket
import time
import ssl
from tkinter import *
from tkinter.scrolledtext import *
from threading import Thread
from tkinter import messagebox

class Chat(Frame):
    def exit(self):
        global connectionAlive
        connectionAlive = False
        self.quit()

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

        self.entryText = StringVar()
        self.INP = Entry(self, textvariable = self.entryText)

        self.SEND = Button(self, text="SEND", fg="green", command=self.sendMessage)
        self.QUIT = Button(self, text="QUIT", fg="red", command=self.exit)

        self.messages.pack(side=RIGHT)
        self.INP.pack()
        self.SEND.pack(side=LEFT)
        self.QUIT.pack(side=RIGHT)

        self.INP.bind('<Return>', self.sendMessageEvent)

    def __init__(self, master=None):
        Frame.__init__(self, master)

        self.pack()
        self.createWidgets()

class Connect(Frame):
    def connectEvent(self, event):
        self.connect()

    def connect(self):
        global s, cont
        try:
            if self.ip.get() == '' or self.name.get() == '':
                messagebox.showinfo("ERROR", "Enter all fields!")
            elif self.port.get() != '' and not self.port.get().isnumeric():
                messagebox.showinfo("ERROR", "Port must be a nubmer or empty!")
            elif not all(i.isnumeric() or i == "." for i in self.ip.get()) or self.ip.get().count(".") != 3:
                messagebox.showinfo("ERROR", "Invalid IP!")
            else:
                s.connect((self.ip.get(), int(self.port.get() or 25565)))
                s.send(bytes(self.name.get().encode("utf-8")))
                cont = True
                self.quit()
        except:
            messagebox.showinfo("Failed to connect", "Could not connect to server.")

    def createWidgets(self):
        self.InputFrame = Frame(self)
        self.LabelFrame = Frame(self.InputFrame)
        self.EntryFrame = Frame(self.InputFrame)
        self.ButtonFrame = Frame(self)

        self.InputFrame.pack(side=TOP)
        self.LabelFrame.pack(side=LEFT)
        self.EntryFrame.pack(side=RIGHT)
        self.ButtonFrame.pack(side=BOTTOM)

        self.name = StringVar()
        self.NAMEINP = Entry(self.EntryFrame, textvariable=self.name)
        self.ip = StringVar()
        self.IPINP = Entry(self.EntryFrame, textvariable=self.ip)
        self.port = StringVar()
        self.PORTINP = Entry(self.EntryFrame, textvariable=self.port)

        self.NAMEINP.pack()
        self.IPINP.pack()
        self.PORTINP.pack()

        self.NAMEINP.bind("<Return>", self.connectEvent)
        self.IPINP.bind("<Return>", self.connectEvent)
        self.PORTINP.bind("<Return>", self.connectEvent)

        self.userLabel = Label(self.LabelFrame, text="Username: ")
        self.ipLabel = Label(self.LabelFrame, text="IP: ")
        self.portLabel = Label(self.LabelFrame, text="Port (Default 25565): ")

        self.userLabel.pack()
        self.ipLabel.pack()
        self.portLabel.pack()

        self.CONNECT = Button(self.ButtonFrame, text="CONNECT", fg="blue", command=self.connect)
        self.QUIT = Button(self.ButtonFrame, text="QUIT", fg="red", command=self.quit)

        self.CONNECT.pack(side=LEFT)
        self.QUIT.pack(side=RIGHT)

    def __init__(self, master = None):
        Frame.__init__(self, master)

        self.pack()
        self.createWidgets()

def receive():
    global s, connectionAlive, chat, threadOn
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
    threadOn = False

s = ssl.wrap_socket(socket.socket(), ciphers='SHA1')

s.settimeout(3)

cont = False
connectRoot = Tk(screenName="Connect")
connectRoot.title("Connect")
connect = Connect(master = connectRoot)
connect.mainloop()

if not cont:
    print("Application stopped.")
    exit()

connectRoot.destroy()

connectionAlive = True

timeFormat = '{:%Y-%m-%d %H:%M:%S}'

threadOn = True
receiverThread = Thread(target=receive)
receiverThread.daemon = True
receiverThread.start()

chatRoot = Tk(screenName='Chat')
chatRoot.title("Chat")
chatRoot.geometry('400x300')
chatRoot.protocol("WM_DELETE_WINDOW", chatRoot.quit)
chat = Chat(master=chatRoot)
chat.mainloop()

connectionAlive = False

s.close()
chatRoot.destroy()

while threadOn: # <--- REALLY BAD UNELEGANT CODE (AKA RAVIOLI CODE) ~~~ LEGOCUBER 1/14/2018
    pass
input("Press Enter to close.")