# /* Daniel Williams 1835399 */

import time
import math

def isEOFPacket(packet):
    return int.from_bytes(packet[2:3], "big") == 1

def getChunk(packet):
    return packet[3:]

def getSeqNum(packet):
    return int.from_bytes(packet[0:2], "big")

#Sends an ACK for packet with seq_num using socket to destination
def sendACK(seqNum, socket, destination):
    seqNumBytes = (seqNum).to_bytes(2, byteorder="big")
    socket.sendto(seqNumBytes, destination)

def createPacket(chunk, seqNum, isEOF):
    seqNumBytes = (seqNum).to_bytes(2, byteorder="big")
    if isEOF:
        EOFbyte = (1).to_bytes(1, byteorder="big")
    else:
        EOFbyte = (0).to_bytes(1, byteorder="big")
        
    return b''.join([seqNumBytes, EOFbyte, chunk])


class basicTimer:
    def __init__(self, retryTimeout):
        self.startTime = math.inf
        self.retryTimeout = retryTimeout

    def start(self):
        self.startTime = time.time()

    def stop(self):
        self.startTime = math.inf

    def hasTimeoutOccured(self):
            return time.time() > self.startTime + self.retryTimeout

    def isRunning(self):
        return self.startTime != math.inf

