import os, sys
import argparse
import hashlib, base64, binascii
from socket import *

parser = argparse.ArgumentParser()
parser.add_argument('serverIPAddr', type=str, help='ip address of the machine where server application is running')
parser.add_argument('serverPort', type=int, help='the port the server application is using')
args = parser.parse_args()

class Client():
    def __init__(self,serverName,serverPort):
        self.serverName = serverName
        self.serverPort = serverPort

    def create_socket(self):
        clientSocket = socket(AF_INET, SOCK_DGRAM)
        while True:
            try:
                userInput = input("\nPlease enter the command:\n\n- get [file_name]\n- put [file_name]\n- rename "
                           "[old_file_name] [new_file_name]\n- list\n- exit\n\n").split()
                cmd = userInput[0]
                clientSocket.sendto(bytes(cmd, encoding='utf-8'), (self.serverName, self.serverPort))
                if cmd == 'get':
                    try:
                        fileName = userInput[1]
                        self.getFile(fileName, clientSocket)
                    except IndexError:
                        print("Incorrect input. [Usage: get [file_name]")
                elif cmd == 'put':
                    try:
                        fileName = userInput[1]
                        self.putFile(fileName, clientSocket)
                    except IndexError:
                        print("Incorrect input. [Usage: put [file_name]")
                elif cmd == 'rename':
                    try:
                        oldFileName = userInput[1]
                        newFileName = userInput[2]
                        self.renameFile(oldFileName, newFileName, clientSocket)
                    except IndexError:
                        print("Incorrect input. [Usage: rename [old_filename] [new_filename]")
                elif cmd == 'list':
                    if len(userInput)==1:               #indicates only the command name 'list' is given
                        self.listFiles(clientSocket)
                    else:
                        print("Incorrect input. [Usage: list]")
                elif cmd == 'exit':
                    if len(userInput)==1:               #indicates only the command name 'exit' is given
                        self.exit()
                    else:
                        print("Incorrect input. [Usage: exit]")
                else:
                    msg = self.recvMsgAndPrintToConsole(clientSocket)
            except KeyboardInterrupt:
                clientSocket.close()
                sys.exit()

    def getFile(self, fileName, clientSocket):
        clientSocket.sendto(bytes(fileName, encoding='utf-8'), (self.serverName, self.serverPort))
        fileExistence = self.recvMsgAndPrintToConsole(clientSocket)
        if 'not' not in fileExistence:
            fileSize, serverAddress = clientSocket.recvfrom(1024)
            hashList = []       #a list to keep track of arrived packets
            with open("Received_" + fileName, 'wb') as f:
                totalRecv = 0
                while totalRecv < int(fileSize.decode('utf-8')):
                    try:
                        encodedData, serverAddress = clientSocket.recvfrom(1500)
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
                        clientSocket.sendto(b"ACK", (self.serverName, self.serverPort))
                    elif recvHashedData == generatedHashedData and dupFlag ==1:
                        #a duplicate packet was received because ACK was lost, so we need not write the data, but send ACK again
                        clientSocket.sendto(b"ACK", (self.serverName, self.serverPort))
                    print("{0:.2f}% Done".format((totalRecv)/float(fileSize) * 100))
            downloadMessage = self.recvMsgAndPrintToConsole(clientSocket)

    def putFile(self, fileName, clientSocket):
        clientSocket.settimeout(1)
        clientSocket.sendto(bytes(fileName, encoding='utf-8'), (self.serverName, self.serverPort))
        if os.path.isfile(fileName):
            print("File {} exists! Sending to the server...".format(fileName))
            clientSocket.sendto(b"Requested file found! Starting upload...", (self.serverName, self.serverPort))
            clientSocket.sendto(bytes(str(os.path.getsize(fileName)), encoding='utf-8'), (self.serverName, self.serverPort))
            with open(fileName, 'rb') as f:
                bytesToSend = f.read(1024)
                ackMessage = b"ACK"  # non-empty ACK, to start sending the first packet
                while bytesToSend and ackMessage:
                    hashedData = self.getHashedData(bytesToSend)
                    clientSocket.sendto(base64.b64encode(bytesToSend) + b"||||" + hashedData, (self.serverName, self.serverPort))
                    #joining encoded data and its hashed content by "||||", to send the combined data together
                    try:
                        ackMessage, serverAddress = clientSocket.recvfrom(1024)
                        #print(ackMessage)              #debug_print_statement
                        bytesToSend = f.read(1024)
                    except:
                        #print("ACK not received. Sending data again...")           #debug_print_statement
                        continue
            print("File sent successfully!")
            clientSocket.sendto(b"Download complete!", (self.serverName, self.serverPort))
        else:
            print("File {} not found!".format(fileName))
            clientSocket.sendto(b"Requested file not found!", (self.serverName, self.serverPort))

    def renameFile(self, oldFileName, newFileName, clientSocket):
        clientSocket.sendto(bytes(oldFileName, encoding='utf-8'), (self.serverName, self.serverPort))
        clientSocket.sendto(bytes(newFileName, encoding='utf-8'), (self.serverName, self.serverPort))
        if os.path.isfile(oldFileName):
            print("File {} exists! Renaming it...".format(oldFileName))
            clientSocket.sendto(b"File found! Renaming it...", (self.serverName, self.serverPort))
            os.rename(oldFileName, newFileName)
        else:
            print("File {} not found!".format(oldFileName))
            clientSocket.sendto(b"File not found!", (self.serverName, self.serverPort))
        message, serverAddress = clientSocket.recvfrom(1024)
        print(message.decode('utf-8'))

    def listFiles(self, clientSocket):
        print("\nFiles present on the server :\n")
        data, serverAddress = clientSocket.recvfrom(1024)
        numberOfFiles = int(data.decode('utf-8'))
        while numberOfFiles > 0:
            fileName, serverAddress = clientSocket.recvfrom(1024)
            print(fileName.decode('utf-8'))
            numberOfFiles -= 1

    def exit(self):
        print("Sending exit command to the server...")

    def getHashedData(self, data):
        m = hashlib.sha256()
        m.update(data)
        return m.digest()

    def recvMsgAndPrintToConsole(self, socket):
        message, serverAddress = socket.recvfrom(1500)
        print(message.decode('utf-8'))
        return message.decode('utf-8')

if __name__=='__main__':
    client = Client(args.serverIPAddr, args.serverPort)
    client.create_socket()