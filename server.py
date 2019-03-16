import argparse
import sys, os
import socket
from socket import *
import hashlib, base64, binascii

parser = argparse.ArgumentParser()
parser.add_argument('serverPort', type=int, help='the port the server application is using [should be > 5000]')
args = parser.parse_args()

class Server():
    def __init__(self,serverPort):
        self.serverPort = serverPort

    def create_socket(self):
        serverSocket = socket(AF_INET, SOCK_DGRAM)
        serverSocket.bind(('', self.serverPort))
        print('The server is ready to receive at port', self.serverPort)
        while True:
            try:
                cmd, clientAddress = serverSocket.recvfrom(1024)
            except:
                continue
            if (cmd.decode('utf-8')) == 'get':
                fileName, clientAddress = serverSocket.recvfrom(1024)
                self.sendFileToClient(serverSocket, fileName.decode('utf-8'), clientAddress)
            elif (cmd.decode('utf-8')) == 'put':
                fileName, clientAddress = serverSocket.recvfrom(1024)
                self.getFileFromClient(serverSocket, fileName.decode('utf-8'), clientAddress)
            elif (cmd.decode('utf-8')) == 'rename':
                try:
                    fileName, clientAddress = serverSocket.recvfrom(1024)
                    newFileName, clientAddress = serverSocket.recvfrom(1024)
                except:
                    continue
                self.renameFile(serverSocket, fileName.decode('utf-8'), newFileName.decode('utf-8'))
            elif (cmd.decode('utf-8')) == 'list':
                self.sendListOfFiles(serverSocket, clientAddress)
            elif (cmd.decode('utf-8')) == 'exit':
                self.exit(serverSocket, clientAddress)
            else:
                serverSocket.sendto(cmd + b"- Unknown command. Not understood by the server!", clientAddress)

    def sendFileToClient(self, serverSocket, fileName, clientAddress):
        serverSocket.settimeout(1)
        if os.path.isfile(fileName):
            print("File {} exists! Sending to the client...".format(fileName))
            serverSocket.sendto(b"Requested file found! Starting download...", clientAddress)
            serverSocket.sendto(bytes(str(os.path.getsize(fileName)), encoding='utf-8'),clientAddress)
            with open(fileName, 'rb') as f:
                bytesToSend = f.read(1024)
                ackMessage = b"ACK"     #non-empty ACK, to start sending the first packet
                while bytesToSend and ackMessage:
                    hashedData = self.getHashedData(bytesToSend)
                    serverSocket.sendto(base64.b64encode(bytesToSend) + b"||||" + hashedData, clientAddress)
                    #joining encoded data and its hashed content by "||||", to send the combined data together
                    try:
                        ackMessage, clientAddress = serverSocket.recvfrom(1024)
                        #print(ackMessage)          #debug_print_statement
                        bytesToSend = f.read(1024)
                    except:
                        #print("ACK not received. Sending data again...")       #debug_print_statement
                        continue
            print("File sent successfully!")
            serverSocket.sendto(b"Download complete!", clientAddress)
        else:
            print("File {} not found!".format(fileName))
            serverSocket.sendto(b"Requested file not found!", clientAddress)

    def getFileFromClient(self, serverSocket, fileName, clientAddress):
        fileExistence = self.recvMsgAndPrintToConsole(serverSocket)
        if 'not' not in fileExistence:
            fileSize, clientAddress = serverSocket.recvfrom(1024)
            hashList = []  # a list to keep track of arrived packets
            with open("Received_" + fileName, 'wb') as f:
                totalRecv = 0
                while totalRecv < int(fileSize.decode('utf-8')):
                    try:
                        encodedData, clientAddress = serverSocket.recvfrom(1500)
                    except:
                        continue
                    data = base64.b64decode(encodedData.split(b"||||")[0])
                    recvHashedData = encodedData.split(b"||||")[1]
                    if recvHashedData not in hashList:
                        hashList.append(recvHashedData)
                        dupFlag = 0         #Not a duplicate packet, hence appended to the list
                    else:
                        dupFlag = 1         #flag for keeping track of a duplicate packet
                    generatedHashedData = self.getHashedData(data)
                    if recvHashedData == generatedHashedData and dupFlag == 0:
                        f.write(data)
                        totalRecv += len(data)
                        serverSocket.sendto(b"ACK", clientAddress)
                    elif recvHashedData == generatedHashedData and dupFlag == 1:
                        #a duplicate packet was received because ACK was lost, so we need not write the data, but send ACK again
                        serverSocket.sendto(b"ACK", clientAddress)
                    print("{0:.2f}% Done".format((totalRecv) / float(fileSize) * 100))
            downloadMessage = self.recvMsgAndPrintToConsole(serverSocket)

    def renameFile(self, serverSocket, fileName, newFilename):
        fileExistence, clientAddress = serverSocket.recvfrom(1024)
        if b'not' not in fileExistence:
            serverSocket.sendto(b"File renamed successfully!", clientAddress)
        else:
            serverSocket.sendto(b"File doesn't exist!", clientAddress)

    def sendListOfFiles(self, serverSocket, clientAddress):
        files = [f for f in os.listdir('.') if os.path.isfile(f)]
        serverSocket.sendto(bytes(str(len(files)), encoding='utf-8'), clientAddress)
        for file in files:
            serverSocket.sendto(bytes(file, encoding='utf-8'), clientAddress)

    def exit(self, serverSocket, clientAddress):
        serverSocket.sendto(b"Server closed successfuly", clientAddress)
        serverSocket.close()
        print("Server closed successfully")
        sys.exit()

    def getHashedData(self, data):
        m = hashlib.sha256()
        m.update(data)
        return m.digest()

    def recvMsgAndPrintToConsole(self, socket):
        message, clientAddress = socket.recvfrom(1500)
        print(message.decode('utf-8'))
        return message.decode('utf-8')

if __name__=='__main__':
    if int(args.serverPort) > 5000:
        server=Server(args.serverPort)
        server.create_socket()
    else:
        print("Incorrect port number. You should select port numbers > 5000")
