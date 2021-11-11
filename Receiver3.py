# /* Daniel Williams 1835399 */

import sys
from socket import *
from helper import *

#Initialize socket and variables
port = int(sys.argv[1])
filename = sys.argv[2]
receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.bind(('', port))
expectedSeqNum = 1

#Receiver Loop
with open(filename, 'wb') as file:
    while True:
        packet, senderAddress = receiverSocket.recvfrom(1027)

        #Get seq number
        seqNum = getSeqNum(packet)

        # If expected seq num, write chunk and increment 
        if expectedSeqNum == seqNum:
            file.write(getChunk(packet))
            expectedSeqNum += 1

        #Send ACK for last received in-order packet
        sendACK(expectedSeqNum - 1, receiverSocket, senderAddress)

        #If eof and have received everything before, break
        if isEOFPacket(packet) and seqNum == expectedSeqNum - 1:
            break


#Keep sending acks for eof packet
#If received no packets for 1 second, assume sender finished
receiverSocket.settimeout(1)
while True:
    try:
        packet, senderAddress = receiverSocket.recvfrom(1027)       
        sendACK(expectedSeqNum - 1, receiverSocket, senderAddress)
    except timeout:
        break

#Close connection
receiverSocket.close()


