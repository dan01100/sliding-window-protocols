# /* Daniel Williams 1835399 */

import sys
from socket import *
from helper import *

#Initialize socket and variables
port = int(sys.argv[1])
filename = sys.argv[2]
receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.bind(('', port))
expectedSeqNum = 0

#Receiver Loop
with open(filename, 'wb') as file:
    while True:
        packet, senderAddress = receiverSocket.recvfrom(1027)

        #Get seq number
        seqNum = getSeqNum(packet)

        #If expected seq number, write chunk and increment 
        if expectedSeqNum == seqNum:
            file.write(getChunk(packet))
            expectedSeqNum += 1

        #Send ACK
        sendACK(seqNum, receiverSocket, senderAddress)

        #Send 10 acks for last packet so sender closes their connection
        if isEOFPacket(packet):
            for _ in range(10):
                sendACK(seqNum, receiverSocket, senderAddress)
            break

#Close connection
receiverSocket.close()

