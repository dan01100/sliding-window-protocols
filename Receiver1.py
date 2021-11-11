# /* Daniel Williams 1835399 */

import sys
from socket import *
from helper import *

#Initialize socket and variables
port = int(sys.argv[1])
filename = sys.argv[2]
receiverSocket = socket(AF_INET, SOCK_DGRAM)
receiverSocket.bind(('', port))

#Receiver Loop
with open(filename, 'wb') as file:
    while True:
        packet, senderAddress = receiverSocket.recvfrom(1027)
        file.write(getChunk(packet))
        if isEOFPacket(packet):
            break

#Close connection
receiverSocket.close()