from Tkinter import *
import smbus
from functools import partial

registers = ["BMC", "BMS", "ID#1", "ID#2", "ANA", "ANL", "ANE", "ANN",
                     "RES", "RES", "RES", "RES", "RES", "RES", "RES", "RES", 
                     "PHYS", "MIC", "MIS", "RES", "FCS", "REC", "PCS", "RB",
                     "LED", "PHYC", "10BT", "CDC", "RES", "EDC", "RES", "RES"]

regValues = ["BMC", "BMS", "ID#1", "ID#2", "ANA", "ANL", "ANE", "ANN",
                     "RES", "RES", "RES", "RES", "RES", "RES", "RES", "RES", 
                     "PHYS", "MIC", "MIS", "RES", "FCS", "REC", "PCS", "RB",
                     "LED", "PHYC", "10BT", "CDC", "RES", "EDC", "RES", "RES"]


        
class Application(Frame):


    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.master.title("DP83848 Phy")
        

        for r in range(4):
            for c in range(8):
                regValues[r*8+c]=StringVar()
                
        
            
        buttonFrame = Frame(master, bg="", bd=10, height=100)
        buttonFrame.grid(row = 0, column = 0, rowspan = 9, columnspan = 2, sticky = W+N)
        
        mode = IntVar()
        self.mode1 = Radiobutton(buttonFrame, text="Isolate", variable=mode, value=1, command = self.isolate).grid(column=0, row=3, sticky=W+N+SW)
        self.mode2 = Radiobutton(buttonFrame, text="Loopback", variable=mode, value=2, command = self.loopback).grid(column=0, row=4, sticky=W+N+SW)
        self.mode3 = Radiobutton(buttonFrame, text="Normal", variable=mode, value=3, command = self.normal).grid(column=0, row=5, sticky=W+N+SW)

        speed = IntVar()
        self.tenBT = Radiobutton(buttonFrame, text="10B-T", variable=speed, value=10, command = self.tenBT).grid(column=1, row=3, sticky=W+E+N+S)
        self.hunBT = Radiobutton(buttonFrame, text="100B-T", variable=speed, value=100, command = self.hunBT).grid(column=1, row=4, sticky=W+E+N+S)

        self.ctlFrame = Frame(buttonFrame, bg="yellow")
        self.ctlFrame.grid(row = 9, column = 0, rowspan = 1, columnspan = 2, sticky = W+E+N+S)
        self.ctrlCanvas = Canvas(self.ctlFrame, width=120, height=120)
        self.ctrlCanvas.pack(expand=YES, fill=BOTH) 
         
        self.led1 = self.ctrlCanvas.create_oval(8,16,20,28, fill="red")
        self.led2 = self.ctrlCanvas.create_oval(8,40,20,52, fill="red")
        self.led3 = self.ctrlCanvas.create_oval(8,64,20,76, fill="red")
        self.led4 = self.ctrlCanvas.create_oval(8,88,20,100, fill="red")
        self.powerOn = Label(self.ctrlCanvas, text='Power On')#, fg='white', bg='black')
        self.powerOn.pack()
        self.ctrlCanvas.create_window(56, 22, window=self.powerOn)
        self.linkUp = Label(self.ctrlCanvas, text='Link Up')#, fg='white', bg='black')
        self.linkUp.pack()
        self.ctrlCanvas.create_window(52, 46, window=self.linkUp)
        self.remoteFault = Label(self.ctrlCanvas, text='Remote Fault')#, fg='white', bg='black')
        self.remoteFault.pack()
        self.ctrlCanvas.create_window(68, 70, window=self.remoteFault)
        self.autoNeg = Label(self.ctrlCanvas, text='Auto Negotiation')#, fg='white', bg='black')
        self.autoNeg.pack()
        self.ctrlCanvas.create_window(78, 94, window=self.autoNeg)


        self.pwdButton = Button(buttonFrame, text="PwDn", command=self.PwDn, width = 10).grid(column=0, row=0, sticky=W+E+N+S)
        self.rstButton = Button(buttonFrame, text="Reset", command=self.Reset, width = 10).grid(column=1, row=0, sticky=W+E+N+S)
        self.rfsButton = Button(buttonFrame, text="Refresh", command=self.getRegisterValues, width = 10).grid(column=0, row=1, sticky=W+E+N+S)
        self.rttButton = Button(buttonFrame, text="Restart", command=self.Refresh, width = 10).grid(column=1, row=1, sticky=W+E+N+S)


        blankFrame = Frame(master, bg="")
        blankFrame.grid(row = 0, column = 2, rowspan = 8, columnspan = 1, sticky = W+E+N+S)

        registerFrame = Frame(master, bg="")
        registerFrame.grid(row = 0, column = 4, rowspan = 8, columnspan = 8, sticky = E)

        self.regButton = list()
        for r in range(4):
            for c in range(8):
                #if registers[r*8+c] != "RES":
                    self.regButton.append(Button(registerFrame, text=registers[r*8+c], command=partial(self.i2cRead, 1, 0x62, ((r*8+c)*2), 2), width = 4).grid(column=c, row=r*2, sticky=W+N))
                    Entry(registerFrame, textvariable=regValues[r*8+c], width=6).grid(column=c, row=r*2+1, sticky=W+N)
                    
    def getRegisterValues(self):
        value = [1, 1]
        for r in range(4):
            for c in range(8):
                #if registers[r*8+c] != "RES":
                    value = self.i2cRead(1, 0x62, ((r*8+c)*2), 2)
                    self.setRegValue((r*8+c), value)            
        value = self.setLEDs()

    def setRegValue(self, reg, value):
        intVal = value[1]*256+value[0]
        regValues[reg].set(hex(intVal))
        regValues[reg].set("0x" + '{:04x}'.format(intVal))

    def setLEDs(self):
        tempVal = int(regValues[1].get(), 16)
        self.ctrlCanvas.itemconfigure(self.led1, fill="red")
        return -1

    def i2cWrite(self, busNr, devAddr, regAddr, values):
        bus = smbus.SMBus(busNr)
        bus.write_i2c_block_data(devAddr, regAddr, values)
    
    def i2cRead(self, busNr, devAddr, regAddr, numBytes):
        bus = smbus.SMBus(busNr)
        values = bus.read_i2c_block_data(devAddr, regAddr, numBytes)
        print ("reg Addr ", regAddr, " value ", values)
        self.setRegValue((regAddr/2), values)
        return values

    def openI2CDevice(busNr):
        value = smbus.SMBus(busNr)
        return value

    def PwDn(self):
        values = self.i2cRead(1, 0x62, 0, 2)
        self.i2cWrite(1, 0x62, 0, values)
        self.ctrlCanvas.itemconfigure(self.led2, fill="green")
        
    def Reset(self):
        self.ctrlCanvas.itemconfigure(self.led3, fill="red")
        
    def Refresh(self):
        self.ctrlCanvas.itemconfigure(self.led3, fill="green")
        
    def isolate(self):
        print("isolate")

    def loopback(self):
        print("Loopback")

    def normal(self):
        print("Normal")

    def tenBT(self):
        print("10BT")

    def hunBT(self):
        print("100BT")


root = Tk()
root.geometry("760x245+200+200")
app = Application(master=root)
app.mainloop()
