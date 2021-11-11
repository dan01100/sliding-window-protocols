# /* Daniel Williams 1835399 */

import sys
from socket import *
from helper import *

#Initialize variables and socket
receiverAddress = sys.argv[1]
receiverPort = int(sys.argv[2])
filename = sys.argv[3]
retryTimeout = int(sys.argv[4]) / 1000
senderSocket = socket(AF_INET, SOCK_DGRAM)

seqNum = 0

#Retranmissions & throughput
retransmissions = 0
startTime = 0
fileSize = 0
throughput = 0

senderSocket.settimeout(retryTimeout)

#Functions
def waitForAck(packet):
    global retransmissions
    
    while True:
        try:
            ack, _ = senderSocket.recvfrom(2)
            ackNum = int.from_bytes(ack, "big")
            if ackNum == getSeqNum(packet):
                return
        except timeout: #resend
                retransmissions += 1
                senderSocket.sendto(packet, (receiverAddress, receiverPort))

#Sender loop
with open(filename, 'rb') as file: 
  while True:
    #Send packet and start transfer time timer if first packet
    chunk = file.read(1024)
    fileSize += len(chunk)

    if seqNum == 0:
        startTime = time.time()

    if (len(chunk) < 1024): #EOF packet
        packet = createPacket(chunk, seqNum, True)
        senderSocket.sendto(packet, (receiverAddress, receiverPort))
    else:
        packet = createPacket(chunk, seqNum, False)
        senderSocket.sendto(packet, (receiverAddress, receiverPort))

    #Wait for ack
    waitForAck(packet)

    #Increment seqNum
    seqNum += 1

    #Last packet, break
    if (isEOFPacket(packet)):
        throughput = (fileSize/1024) / ( time.time() - startTime )
        break


#Close connection
print(str(retransmissions) + " " + str(throughput))
senderSocket.close()

