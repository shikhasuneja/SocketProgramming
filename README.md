# SocketProgramming

Project Title: Client-Server Application using UDP Socket Programming in Python

Built With: Python 3.6.2

Author: Shikha Suneja

Description:
- File server.py needs to be run on the command line along with the port number, where the server is running, as an arugment. For example, python server.py 5500
- File client.py needs to be run on the command line along with two arguments, the ip address of the machine where server is running, and the port number it is using. For example, python client.py 127.0.0.1 5500
- On the client side, the user needs to enter a command to get the appropriate output.
- The commands need to be entered in the following manner:
[Assumption: fileName should include extension as well]
	(a) get fileName, for example, get foo1.txt
	(b) put fileName, for example, put foo2.jpg
	(c) rename old-fileName new-fileName, for example, rename foo1.txt foo5.txt
	(d) list
	(e) exit
- If any other command is entered, an error saying "Command not found" is displayed on STDOUT.
- for data encryption during transit, "base64.b64encode()" is used to encrypt the data before sending and "base64.b64decode()" is used to decrypt the data once it is received.
- for checking data authenticity and to avoid scenarios of packet loss/corruption, "hashData" is created using hashlib sha256 algorithm
- In client.py, 
	- argparse is used to get the required command-line arguments
	- it is being run on an infinite loop using "while True" statement, unless a KeyboardInterrupt occurs (like Ctrl+C)
	- it asks for userinput to proceed to the next statement
	- the function "getFile" is used to get the required file from the server
		- "fileName" is sent to the server
		- file's existence is checked, and if the file exists, only then fileSize is taken from the server
		- a list called hashList is used to keep track of arrived data
		- [encoded data + hashed data] is received from the server
		- encoded data is decoded and then a new hashed data is generated using this decoded data
		- if the received hashed data and the generated hashed data are same, that implies, the data is not corrupted, and so then it is written in the file
		- if the received hashed data is not present in the hashList, it is added to the list. If it is present, that implies, that the same data had already arrived, and there's a possibility that ACK was lost during transmission, and as a result, this data was retransmitted and hence duplicated. So, in this case, we need to send an ACK, and need not write the data, as it was already written 
	- the function "putFile" is used to put the file on the server
		- "fileName" is sent to the server
		- file's existence is checked, and if the file exists, only then fileSize is sent to the server
		- client starts sending encoded data along with a hashData in chunks
		- if the sent data is received successfully on the server, it sends an ACK, only then the client sends the next chunk of data
		- if "ACK" is not received, the client resends the same chunk of data, and waits for an ACK again.
		- incase, "ACK" was lost but server had received the data, it will discard the retransmitted chunk of data i.e., it won't write the same data again to a file, however, it would send an ACK again.
	- the function "renameFile" is used to rename a file
		- both the filenames are sent to the server
		- file's existence status is also sent to the server
		- the file is renamed if it exists
		- the server responds accordingly
	- the function "listFiles" is used to list all the files present of the server
		- the total number of files and the list of files are received from the server
		- names of the files are displayed on client side
	- the function "exit" just prints that the command "exit" is sent to the server
	- the function "getHashedData" returns hashData using hashlib sha256 algorithm
	- the function "recvMsgAndPrintToConsole" receives the message from the server and prints on the console	
- In server.py,
	- argparse is used to get the required command-line arguments
	- the function "sendFileToClient" is used to send the file that the client has requested
	- an ACK is received from the client after sending each chunk of data. If ACK is received, only then the next set of bytes is sent.
	- the function "getFileFromClient" is used to get a requested file (the one which the user writes in "put" command) from the client
	- the function "renameFile" just sends the status if the file was found and renamed or not
	- the function "sendListOfFiles" sends the total numberof files present in the server and their names to the client
	- the function "exit" gracefully closes the serverSocket and the program exits
	- the function "getHashedData" returns hashData using hashlib sha256 algorithm
	- the function "recvMsgAndPrintToConsole" receives the message from the server and prints on the console

Prerequisites:
- Python 3.6.2
- a text editor, for opening/viewing foo1.txt
- an image viewer, for opening/viewing foo2.jpg
- a pdf viewer, for opening/viewing foo3.pdf

Testing:
- tested all the commands by running the client.py and server.py on different directories
- additionally, simulated a scenario with 1% packet loss, and tested all the commands 
- File transfers of upto 10 - 15 MB were successfully verified (with and without packet loss)
