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

Prerequisites:
- Python 3.6.2
- a text editor, for opening/viewing foo1.txt
- an image viewer, for opening/viewing foo2.jpg
- a pdf viewer, for opening/viewing foo3.pdf

Testing:
- tested all the commands by running the client.py and server.py on different directories
- additionally, simulated a scenario with 1% packet loss, and tested all the commands 
- File transfers of upto 10 - 500 MB were successfully verified (with and without packet loss)
