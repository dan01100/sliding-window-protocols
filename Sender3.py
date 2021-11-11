# /* Daniel Williams 1835399 */

import sys
import math
import time
from socket import *
from helper import *
import threading

#Initialize variables and socket
receiverAddress = sys.argv[1]
receiverPort = int(sys.argv[2])
filename = sys.argv[3]
retryTimeout = int(sys.argv[4]) / 1000
windowSize = int(sys.argv[5])

senderSocket = socket(AF_INET, SOCK_DGRAM)
file = open(filename, "rb")

timer = basicTimer(retryTimeout)
lastAckReceived = False
#Start packets at 1 incase first goes missing (receiver can ack 0)
base = 1
nextSeqNum = 1
eofSeqNum = math.inf
window = []
lock = threading.Lock()

#Throughput variables
startTime = 0
fileSize = 0
throughput = 0

#####FUNCTIONS####

#Get the next packet from the file
def nextPacket():
    global fileSize

    chunk = file.read(1024)
    fileSize += len(chunk)
    if len(chunk) < 1024:
        return createPacket(chunk, nextSeqNum, True)
    return createPacket(chunk, nextSeqNum, False)

#Send the window
def sendWindow():
    for packet in window:
        senderSocket.sendto(packet, (receiverAddress, receiverPort))

#Update the window
def updateWindow(ackNum):
    global base
    global window

    slideAmount = ackNum - base + 1
    del window[:slideAmount] 
    base = ackNum + 1


####THREADS#####

#Waits for space to be available in the window 
#Sends packet and sets a timer if window previously empty
def send():
    global nextSeqNum
    global eofSeqNum
    global startTime

    while not lastAckReceived:
        lock.acquire()
        #If space in window AND more packets to send
        while nextSeqNum < base + windowSize and eofSeqNum == math.inf:
            #Get next packet
            packet = nextPacket()
            #save time if first packet
            if nextSeqNum == 1:
                startTime = time.time()
            #Add to window & send
            window.append(packet)
            senderSocket.sendto(packet, (receiverAddress, receiverPort))
            #Start timer if empty window
            if (base == nextSeqNum):
                timer.start()
            #Increment nextSeqNum
            nextSeqNum += 1

            if (isEOFPacket(packet)):
                eofSeqNum = getSeqNum(packet)


        lock.release()
        time.sleep(0.01)



#Listens for acks and updates the window
def receive():
    global lastAckReceived
    global throughput

    while not lastAckReceived:
        ack, _ = senderSocket.recvfrom(2)

        lock.acquire()
        #Extract ackNum
        ackNum = int.from_bytes(ack, "big")
        #Ignore if old, late ack
        if ackNum < base:
            lock.release()
            continue
        #Update window
        updateWindow(ackNum)
        #Stop timer if no packets in window
        if (base == nextSeqNum):
            timer.stop()
        else: #Otherwise restart it
            timer.start()

        #If Last ack received
        if (ackNum == eofSeqNum):
            lastAckReceived = True
            throughput = (fileSize/1024) / (time.time() - startTime)   
                     
        lock.release()


#Timeout for sending window
def timeout():
    while not lastAckReceived:
        lock.acquire()
        #Check for timeout and sleep
        if timer.hasTimeoutOccured():
            timer.start()
            sendWindow()
            sleepTime = retryTimeout   
        elif timer.isRunning():
            sleepTime = max(0.001, timer.startTime + retryTimeout - time.time())
        else:
            sleepTime = retryTimeout
        lock.release()
        
        time.sleep(sleepTime)

##START THREADS##
sendThread = threading.Thread(target=send)
receiveThread = threading.Thread(target=receive)
timeoutThread = threading.Thread(target=timeout)

sendThread.start()
receiveThread.start()
timeoutThread.start()

sendThread.join()
receiveThread.join()
timeoutThread.join()

#Close connection
print(throughput)
file.close()
senderSocket.close()

