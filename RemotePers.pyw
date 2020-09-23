from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from tkinter import messagebox
from ftplib import FTP
import telnetlib
import threading
filename = str(NONE)

def get_filename():
    global filename
    global filenameTK
    filename = filedialog.askopenfilename()
    filenameTK.set(filename)

def ftp_thread():
    threading.Thread.daemon = True
    a = threading.Thread(target=ftp_checklist)
    if threading.active_count() == 1:
        outputlines.set("Attempting to connect")
        a.start()
    else:
        outputlines.set("Please wait for script to finish")
def ftp_checklist():
    if personality_check() == 0:
        outputlines.set("Personality file needs to be a .SFT file type")
    if IP_check() == 0:
        outputlines.set("Check IP Address for errors")
    if personality_check() == 1 and IP_check() == 1:
        ftp_connection()

def personality_check():
    p_check = filename[-3:]
    p_check = p_check.lower()
    if p_check == "sft":
        return(1)
    else:
        return (0)

def IP_check():
    IP = ipstring.get()
    IP = IP.split(".")
    if len(IP) != 4:
        return (0)
    for x in IP:
        if not x.isdigit():
            return (0)
        i = int(x)
        if i < 0 or i > 255:
            return (0)
    return (1)


def ftp_connection():
    try:
        ftp = FTP(ipstring.get())
        ftp.set_debuglevel(1)
        ftp.set_pasv(0)
        outputlines.set("Connection successful")
        ftp_login(ftp)
    except:
        outputlines.set("Failed to connect")

def ftp_login(ftp):
    try:
        ftp.login("super", "user")
        outputlines.set("Login successful")
        ftp_pers_download(ftp)
    except:
        outputlines.set("Login failed")

def ftp_pers_download(ftp):
    try:
        ftp.cwd("/r2")
        outputlines.set("Downloading Personality")
        file = open(filename, 'rb')
        ftp.storbinary('STOR pers', file)
        outputlines.set("Download Completed")
        ftp.quit()
        telnet_move_pers()
    except:
        outputlines.set("Personality download failed")

def telnet_move_pers():
    try:
        outputlines.set("Moving Personality to /f0")
        HOST = ipstring.get()
        tn = telnetlib.Telnet(HOST)
        tn.set_debuglevel(1)
        tn.read_until(b"name?: ", timeout = 3)
        tn.write(b"super\n")
        tn.read_until(b"Password: ", timeout = 3)
        tn.write(b"user\n")
        tn.read_until(b"$ ", timeout = 3)
        tn.write(b'chd /r2\n')
        tn.read_until(b"$ ", timeout = 3)
        tn.write(b'copy * /f0\n')
        tn.read_until(b"quit)? ", timeout = 3)
        tn.write(b'a\n')
        tn.read_until(b"a\r\n", timeout = 3)
        if archperscheck.get() == 1:
            outputlines.set("Moving Personality to /r0")
            tn.write(b'rename * archpers\n')
            tn.read_until(b"$ ", timeout=3)
            tn.write(b'copy * /r0\n')
            tn.read_until(b"quit)? ", timeout=3)
            tn.write(b'a\n')
            tn.read_until(b"a\r\n", timeout=3)
        else:
            print ("naw")
        outputlines.set("Personality stored sucessfully!!!")
    except:
        outputlines.set("Personality failed to move to /f0")

def reboot_thread():
    threading.Thread.daemon = True
    b = threading.Thread(target=telnet_reboot)
    if threading.active_count() == 1:
        outputlines.set("Attempting to reboot")
        b.start()
    else:
        outputlines.set("Please wait for script to finish")

def telnet_reboot():
    if IP_check() == 1:
        try:
            HOST = ipstring.get()
            tn = telnetlib.Telnet(HOST)
            tn.set_debuglevel(1)
            tn.read_until(b"name?: ", timeout=3)
            tn.write(b"super\n")
            tn.read_until(b"Password: ", timeout = 3)
            tn.write(b"user\n")
            tn.read_until(b"$ ", timeout = 3)
            tn.write(b'break\n')
            tn.read_until(b"to resume.)", timeout = 3)
            outputlines.set("Reboot sucessful!!!")
        except:
            outputlines.set("Reboot failed")
    if IP_check() == 0:
        outputlines.set("Check IP Address for errors")


def popup():
    response = messagebox.askquestion("Warning", "Are you sure you want to download the personality?", icon='warning')
    if response == "yes":
        ftp_thread()
    else:
        return

def popup2():
    response = messagebox.askquestion("Warning", "Are you sure you want reboot the controller?", icon='warning')
    if response == "yes":
        reboot_thread()
    else:
        return

root = Tk()
root.title("Remote Personality Downloader")
filenameTK = StringVar()
ipstring = StringVar()
outputlines = StringVar()
archperscheck = IntVar()
MainFrame = ttk.Frame(root)
MainFrame.grid(column=0, row=0)
outputframe = ttk.Frame(root)
outputframe.grid(column=0, row=1)
PERSONALITY = Message(MainFrame, text="Personality", width=100)
PATH = Message(MainFrame, text="Path" , width=100)
IP = Message(MainFrame, text="Controller IP", width=100)
SEND = Message(MainFrame, text="Send Personality", width=100)
REBOOT = Message(MainFrame, text="Controller Reboot", width=100)
PERSONALITY.grid(column=0, row=0, sticky="E")
PATH.grid(column=0, row=1, sticky="E")
IP.grid(column=0, row=2, sticky="E")
SEND.grid(column=0, row=3, sticky="E")
REBOOT.grid(column=0, row=4, sticky="E")
Get_Filename_Button = Button(MainFrame, text="File", command=get_filename).grid(column=1, row=0, sticky="W")
Filename_Message = Message(MainFrame, textvariable=filenameTK, foreground="green", width=1000).grid(column=1, columnspan=20, row=1, sticky="W")
Entry(MainFrame, textvariable=ipstring).grid(column=1, row=2, columnspan=10,sticky="W")
StartFTP = Button(MainFrame, text="Send", command=popup).grid(column=1, row=3, sticky="W")
ArchPers = Checkbutton(MainFrame, text="Arch Pers", variable=archperscheck).grid(column=2, row=3, sticky="W")
RebootController = Button(MainFrame, text="REBOOT", command=popup2).grid(column=1, row=4, sticky="W")
label = Label(outputframe, textvariable=outputlines, foreground="green")
label.grid(column=0, row=0, sticky="E")
root.mainloop()
