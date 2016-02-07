from Tkinter import *
import smbus
from functools import partial
from operator import xor

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
        
        self.mode = IntVar()
        self.mode1 = Radiobutton(buttonFrame, text="Isolate", variable=self.mode, value="Iso", command = partial(self.buttonPress, "Iso")).grid(column=0, row=3, sticky=W+N+SW)
        self.mode2 = Radiobutton(buttonFrame, text="Loopback", variable=self.mode, value="Lpk", command = partial(self.buttonPress, "Lbk")).grid(column=0, row=4, sticky=W+N+SW)
        self.mode3 = Radiobutton(buttonFrame, text="Normal", variable=self.mode, value="Nml", command = partial(self.buttonPress, "Nml")).grid(column=0, row=5, sticky=W+N+SW)

        self.speed = IntVar()
        self.tenBT = Radiobutton(buttonFrame, text="10B-T", variable=self.speed, value=10, command = partial(self.buttonPress, "Lsp")).grid(column=1, row=3, sticky=W+E+N+S)
        self.hunBT = Radiobutton(buttonFrame, text="100B-T", variable=self.speed, value=100, command = partial(self.buttonPress, "Hsp")).grid(column=1, row=4, sticky=W+E+N+S)

        self.ctlFrame = Frame(buttonFrame, bg="yellow")
        self.ctlFrame.grid(row = 9, column = 0, rowspan = 1, columnspan = 2, sticky = W+E+N+S)
        self.ctrlCanvas = Canvas(self.ctlFrame, width=120, height=120)
        self.ctrlCanvas.pack(expand=YES, fill=BOTH) 
         
        self.led1 = self.ctrlCanvas.create_oval(8,16,20,28, fill="red")
        self.led2 = self.ctrlCanvas.create_oval(8,40,20,52, fill="red")
        self.led3 = self.ctrlCanvas.create_oval(8,64,20,76, fill="red")
        self.led4 = self.ctrlCanvas.create_oval(8,88,20,100, fill="red")
        self.powerOn = Label(self.ctrlCanvas, text='Power On')
        self.powerOn.pack()
        self.ctrlCanvas.create_window(56, 22, window=self.powerOn)
        self.linkUp = Label(self.ctrlCanvas, text='Link Up')
        self.linkUp.pack()
        self.ctrlCanvas.create_window(52, 46, window=self.linkUp)
        self.remoteFault = Label(self.ctrlCanvas, text='Remote Fault')
        self.remoteFault.pack()
        self.ctrlCanvas.create_window(68, 70, window=self.remoteFault)
        self.autoNeg = Label(self.ctrlCanvas, text='Auto Negotiation')
        self.autoNeg.pack()
        self.ctrlCanvas.create_window(78, 94, window=self.autoNeg)

        self.pwdButton = Button(buttonFrame, text="PwDn", command=partial(self.buttonPress, "Pwr"), width = 10).grid(column=0, row=0, sticky=W+E+N+S)
        self.rstButton = Button(buttonFrame, text="Reset", command=partial(self.buttonPress, "Rst"), width = 10).grid(column=1, row=0, sticky=W+E+N+S)
        self.rfsButton = Button(buttonFrame, text="Refresh", command=partial(self.buttonPress, "Rfs"), width = 10).grid(column=0, row=1, sticky=W+E+N+S)
        self.rttButton = Button(buttonFrame, text="Restart", command=partial(self.buttonPress, "Rtt"), width = 10).grid(column=1, row=1, sticky=W+E+N+S)

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

        self.i2cWrite(1, 0x62, 0x80, [0x01, 0x01])
        self.mode.set("Nml")
        self.speed.set(100)
        self.tick()
                    
    def getRegisterValues(self):
        print("Getting all registers...")
        value = [1, 1]
        for r in range(4):
            for c in range(8):
                #if registers[r*8+c] != "RES":
                    value = self.i2cRead(1, 0x62, ((r*8+c)*2), 2)
                    self.setRegValue((r*8+c), value)            
        
    def setRegValue(self, reg, value):
        intVal = value[1]*256+value[0]
        regValues[reg].set(hex(intVal))
        regValues[reg].set("0x" + '{:04x}'.format(intVal))

    def setLEDs(self):
        values = self.i2cRead(1, 0x62, 0, 2)
        print("Setting LEDs...", format(int(values[1]), '#04X'))
        if values[1] & 0x08:
            self.ctrlCanvas.itemconfigure(self.led1, fill="red")
        else:
            self.ctrlCanvas.itemconfigure(self.led1, fill="green")
        values = self.i2cRead(1, 0x62, 2, 2)
        print("Setting LEDs...", format(int(values[0]), '#04X'))
        if values[0] & 0x04:
            self.ctrlCanvas.itemconfigure(self.led2, fill="green")
        else:
            self.ctrlCanvas.itemconfigure(self.led2, fill="red")
        if values[0] & 0x10:
            self.ctrlCanvas.itemconfigure(self.led3, fill="red")
        else:
            self.ctrlCanvas.itemconfigure(self.led3, fill="green")
        if values[0] & 0x20:
            self.ctrlCanvas.itemconfigure(self.led4, fill="green")
        else:
            self.ctrlCanvas.itemconfigure(self.led4, fill="red")
 
    def i2cWrite(self, busNr, devAddr, regAddr, values):
        bus = smbus.SMBus(busNr)
        bus.write_i2c_block_data(devAddr, regAddr, values)
        print("Writing ", format(int(values[0]), '#04X'), format(int(values[1]), '#04X'))
           
    def i2cRead(self, busNr, devAddr, regAddr, numBytes):
        bus = smbus.SMBus(busNr)
        values = bus.read_i2c_block_data(devAddr, regAddr, numBytes)
        print ("Read ", format(int(values[0]), '#04X'), format(int(values[1]), '#04X'))
        return values
    
    def buttonPress(self, command):
        values = self.i2cRead(1, 0x62, 0, 2)
        if command == "Pwr":
            print("Power Down Pressed! setting BCM register bit 11 to ?")
            values[1] = (values[1] ^ 0x08)
        elif command == "Lbk":
            print("Loopback selected setting BCM register bit 14 to '1'")
            values[1] = (values[1] | 0x40)
        elif command == "Iso":
            print("Isolate selected setting BCM register bit 10 to '1'")
            values[1] = (values[1] | 0x04)
        elif command == "Rst":
            print("Reset pressed setting BCM register bit 15 to '1'")
            self.mode.set("Nml")
            values[1] = (values[1] | 0x80)
        elif command == "Nml":
            print("Normal selected setting BCM register bits 14 & 10 to '0'")
            values[1] = (values[1] & 0xBB)
        elif command == "Rtt":
            print("Restart pressed setting BCM register bit 9 to '1'")
            values[1] = (values[1] | 0x02)
        elif command == "Rfs":
            print("Refresh pressed!")
            self.getRegisterValues()
        elif command == "Lsp":
            print("Low Speed selected setting BCM register bit 13 to '0'")
            values[1] = (values[1] & 0xDF)
        elif command == "Hsp":
            print("High speed selected setting BCM register bit 13 to '1'")
            values[1] = (values[1] | 0x20)
        else:
            print("Command not recognised", command)
        self.i2cWrite(1, 0x62, 0, values)
        
    def tick(self):
        self.setLEDs()
        self.getRegisterValues()
        self.ctlFrame.after(1000, self.tick)

root = Tk()
root.geometry("760x245+200+200")
app = Application(master=root)
app.mainloop()
