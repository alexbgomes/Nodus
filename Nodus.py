import errno
import select
import socket
import sys

class Nodus:
    HEADER_LENGTH = 10
    IP = "127.0.0.1" # server's IP, this will change
    PORT = 7887 # server's port, this should not change

    def __init__(self, nickname):
        self.nickname = nickname
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((self.IP, self.PORT))
        self.client_socket.setblocking(False) # recv won't be blocking

        client = nickname.encode('utf-8')
        client_header = f"{len(client):<{self.HEADER_LENGTH}}".encode('utf-8')
        self.client_socket.send(client_header + client) # let server know user wants to connect

    def run(self):
        # allow querying to directory here
        while True:
            # this is thread blocking, cannot see new messages until we send empty message to recycle message pulls from server
            message = input(f"{self.nickname} > ")

            if message:
                message = message.encode('utf-8')
                message_header = f"{len(message):<{self.HEADER_LENGTH}}".encode('utf-8')
                self.client_socket.send(message_header + message)

            try:
                while True:
                    # receive messages from server until err
                    nickname_header = self.client_socket.recv(self.HEADER_LENGTH)
                    if not len(nickname_header): # if not nickname_header might work as well
                        print('Connection closed by the host.')
                        sys.exit()

                    nickname_length = int(nickname_header.decode('utf-8').strip())
                    nickname = self.client_socket.recv(nickname_length).decode('utf-8')

                    message_header = self.client_socket.recv(self.HEADER_LENGTH)
                    message_length = int(message_header.decode('utf-8').strip())
                    message = self.client_socket.recv(message_length).decode('utf-8')

                    print(f"{nickname} > {message}")
            except IOError as e:
                if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK: # when there are no more messages to recv
                    print(f"Read error {e}")
                    sys.exit()
                continue
            except Exception as e:
                print(f"Unexpected error {e}")
                sys.exit()

if __name__ == "__main__":
    nickname = input('Enter your nickname: ')
    App = Nodus(nickname)
    print(f'Nodus | Connected to: {App.IP}:{App.PORT}\n{"-"*36}')
    App.run()