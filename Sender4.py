# /* Daniel Williams 1835399 */

import sys
import math
import time
from socket import *
from helper import *
import threading


#Initialize variables and socket
receiverAddress =  sys.argv[1]
receiverPort = int(sys.argv[2])
filename = sys.argv[3]
retryTimeout = int(sys.argv[4]) / 1000
windowSize = int(sys.argv[5])

senderSocket = socket(AF_INET, SOCK_DGRAM)
file = open(filename, "rb")

base = 0
nextSeqNum = 0
eofSeqNum = math.inf

window = [None] * windowSize
windowAcks = [False] * windowSize
lock = threading.Lock()

#Throughput variables
startTime = 0
fileSize = 0
throughput = 0

####FUNCTIONS####

#Get the next packet from the file
def nextPacket():
    global fileSize

    chunk = file.read(1024)
    fileSize += len(chunk)
    if len(chunk) < 1024:
        return createPacket(chunk, nextSeqNum, True)
    return createPacket(chunk, nextSeqNum, False)


#Updates the window
def updateWindow(ackNum):
    global window
    global windowAcks
    global base

    if (ackNum < base):
        return
    #index of packet in window
    index = ackNum - base 
    windowAcks[index] = True
    #Slide window forward
    while (windowAcks[0] == True):
        del window[0]
        window.append(None)
        del windowAcks[0]
        windowAcks.append(False)
        base += 1


####THREADS####

#Waits for space to be available in the window 
#Sends the packet and sets a timer when space is available
def send():
    global nextSeqNum
    global eofSeqNum
    global window
    global startTime

    while True:
        lock.acquire()
        while nextSeqNum < base + windowSize:

            packet = nextPacket()
            #save time if first packet
            if nextSeqNum == 0:
                startTime = time.time()
            
            #add packet to window
            index =  nextSeqNum - base
            window[index] = packet

            #send packet
            senderSocket.sendto(packet, (receiverAddress, receiverPort))

            #create timer
            timer = threading.Timer(retryTimeout, timeout, args=(nextSeqNum,))
            timer.start()

            nextSeqNum += 1

            if (isEOFPacket(packet)):
                eofSeqNum = getSeqNum(packet)
                lock.release()
                return

        lock.release()
        time.sleep(0.01)




#Listens for acks and updates the window
def receive():
    global throughput

    while True:

        ack, _ = senderSocket.recvfrom(2)

        lock.acquire()
        ackNum = int.from_bytes(ack, "big")
        updateWindow(ackNum)
        
        #Received all acks
        if (base > eofSeqNum):
            throughput = (fileSize/1024) / ( time.time() - startTime )
            lock.release()
            return
        lock.release()



#Sets a timer for packet with seqNum 
def timeout(seqNum):
    lock.acquire()
    #End thread if seqNum has been acked
    if base > seqNum or windowAcks[seqNum-base]:
        lock.release()
        return
    #Otherwise restart timer & resend packet
    senderSocket.sendto(window[seqNum-base], (receiverAddress, receiverPort))
    timer = threading.Timer(retryTimeout, timeout, args=(seqNum,))
    timer.start()
    lock.release()


#Start Threads
sendThread = threading.Thread(target=send)
receiveThread = threading.Thread(target=receive)

sendThread.start()
receiveThread.start()

sendThread.join()
receiveThread.join()

#Close connection
print(str(throughput))
file.close()
senderSocket.close()

