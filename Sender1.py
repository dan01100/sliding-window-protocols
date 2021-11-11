# /* Daniel Williams 1835399 */

import sys
from socket import *
from helper import *
import time

#Initialize variables and socket
receiverAddress = sys.argv[1]
receiverPort = int(sys.argv[2])
filename = sys.argv[3]
senderSocket = socket(AF_INET, SOCK_DGRAM)
seqNum = 0

#Sender Loop
with open(filename, 'rb') as file:
  while True:
    chunk = file.read(1024)
    if (len(chunk) < 1024): #EOF
        packet = createPacket(chunk, seqNum, True)
        senderSocket.sendto(packet, (receiverAddress, receiverPort))
        break
    else:
        packet = createPacket(chunk, seqNum, False)
        senderSocket.sendto(packet, (receiverAddress, receiverPort))
        seqNum += 1
    #short sleep so packets arrive in order
    time.sleep(0.01)

#Close connection
senderSocket.close()