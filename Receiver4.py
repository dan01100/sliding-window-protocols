# /* Daniel Williams 1835399 */

import sys
import math
from helper import *
from socket import *

#Initialize socket and variables
port = int(sys.argv[1])
filename = sys.argv[2]
windowSize = int(sys.argv[3])
receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.bind(('', port))

eofSeqNum = math.inf
rcvBase = 0
window = [None] * windowSize
file = open(filename, "wb")

#Updates the window and writes chunks
def updateWindowWriteChunks(packet):
    global rcvBase
    global window

    seqNum = getSeqNum(packet)
    if (seqNum < rcvBase):
        return
    #index of packet in window
    index = seqNum - rcvBase 
    #Add packet to window
    window[index] = packet
    #Slide window forward
    while (window[0] != None):
        file.write(getChunk(window[0]))
        del window[0]
        window.append(None)
        rcvBase += 1

#Receiver Loop
while True:
    packet, senderAddress = receiverSocket.recvfrom(1027)       
    
    seqNum = getSeqNum(packet)

    #Send ACK
    if (seqNum >= rcvBase - windowSize):
        sendACK(seqNum, receiverSocket, senderAddress)

    #Update the window and write chunks
    updateWindowWriteChunks(packet)

    if isEOFPacket(packet):
        eofSeqNum = seqNum

    #If received all packets, break
    if rcvBase == eofSeqNum + 1:
        break



#Keep sending acks
#If received no packet for 1 second, assume sender finished
receiverSocket.settimeout(1)
while True:
    try:
        packet, senderAddress = receiverSocket.recvfrom(1027)       
        sendACK(getSeqNum(packet), receiverSocket, senderAddress)
    except timeout:
        break

#Close connection
file.close()
receiverSocket.close()






