import select
import socket

class NodusDirectory:
    HEADER_LENGTH = 10
    sockets_list = []
    clients = {}

    def __init__(self, IP = "127.0.0.1", PORT = 7887):
        self.IP = IP
        self.PORT = PORT
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # allow incremental addresses to reconnect

        self.server_socket.bind((IP, PORT))
        self.sockets_list.append(self.server_socket)

    def receive_message(self, client_socket):
        try:
            message_header = client_socket.recv(self.HEADER_LENGTH)

            if not len(message_header): # if not message_header might work too
                return False

            message_length = int(message_header.decode('utf-8').strip())
            return { 
                "header": message_header, 
                "data": client_socket.recv(message_length), # may need to handle large messages differently
            }
        except:
            return False

    def run(self):
        self.server_socket.listen()

        while True:
            read_sockets, _, exception_sockets = select.select(self.sockets_list, [], self.sockets_list) #read, write, err

            for notified_socket in read_sockets:
                if notified_socket == self.server_socket:
                    client_socket, client_address = self.server_socket.accept()

                    user = self.receive_message(client_socket)
                    if user is False:
                        continue

                    self.sockets_list.append(client_socket)

                    self.clients[client_socket] = user

                    print(f"{user['data'].decode('utf-8')} ({client_address[0]}:{client_address[1]}) has joined the room.")

                else:
                    message = self.receive_message(notified_socket)

                    if message is False:
                        print(f"{self.clients[notified_socket]['data'].decode('utf-8')} has left the room.")
                        self.sockets_list.remove(notified_socket)
                        del self.clients[notified_socket]
                        continue

                    user = self.clients[notified_socket]
                    print(f"{user['data'].decode('utf-8')} says: {message['data'].decode('utf-8')}")

                    for client_socket in self.clients:
                        if client_socket != notified_socket:
                            client_socket.send(user['header'] + user['data'] + message['header'] + message['data'])

            for notified_socket in exception_sockets:
                self.sockets_list.remove(notified_socket)
                del self.clients[notified_socket]

if __name__ == "__main__":
    NDS = NodusDirectory()
    print(f'Running Nodus Directory server: {NDS.IP}:{NDS.PORT}\n{"-"*46}')
    NDS.run()