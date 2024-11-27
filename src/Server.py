from threading import Thread, Lock, Condition
import socket as sock

class Server:
    def __init__(self, members):
        self.__ip = None                                 # Host's ip address: Local(Private) ip that host machine is currently running on.
        self.__received_data = None
        self.__port = 9353                               # Host's port: Integer value that need to be more than 1023 and less than 65535.
        self.__members = members                          # Number of participants of the game.
        self.__clients = {}                               # A dict to store connected clients.
        self.__lock = Lock()
        self.__condition = Condition(self.__lock)

    def __len__(self) -> int:
        return len(self.__clients)

    def __repr__(self) -> str:
        return f"Host Server is running on {sock.getfqdn(self.__ip[0])} at {self.__ip}:{self.__port}"

    def __set_ip(self) -> None:
        """
        Checks if passed ip address is valid or not.
        args: None
        returns: None
        """
        try:
            # Try a simple ping connection to 1.1.1.1 to get the private ip address
            with sock.socket(sock.AF_INET, sock.SOCK_DGRAM) as connection:
                connection.settimeout(2)
                connection.connect(("1.1.1.1", 80))
                ip = connection.getsockname()
                if ip[0].startswith("127"):
                    raise OSError
                # Assigning new valid ip address
                self.__ip = ip[0]
        except OSError as e:
            print(f"Function \"ip_check\" throws an Exception:\t{e}")
        except Exception as e:
            print(f"Crashed due unhandled Exception:\t{e}")

    def run(self):
        """
        Starts the server at given ip address and port.
        args: None
        returns: None
        """

        self.__set_ip()

        with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as socket:
            socket.bind((self.__ip, self.__port))
            socket.listen(self.__members)
            print(self)

            while len(self) < self.__members:
                client_socket, client_address = socket.accept()
                self.__clients[client_socket] = client_address

                if not len(self) == self.__members:
                    print(f"Waiting for {self.__members - len(self)} other client to join!")

                if len(self) == self.__members:
                    for client,address in self.__clients.items():
                        client_thread = Thread(target=self.__handle_client, args=(client, address))
                        client_thread.start()

    def __handle_client(self, client_socket, client_address):
        with client_socket:
            print(f"Connection established with {sock.getfqdn(client_address[0])} from {client_address[0]}")
            while True:
                received_data = client_socket.recv(1024).decode(encoding="utf-8")
                if not received_data:
                    continue
                with self.__lock:
                    self.send_data(client_socket, f"Received {received_data}")
                    self.__received_data = received_data
                    self.__condition.notify_all()

    def receive_data(self):
        with self.__condition:
            while self.__received_data is None:
                self.__condition.wait()
            received = self.__received_data
            self.__received_data = None
        return received

    def send_data(self, client_socket, message):
        client_socket.sendall(message.encode("utf-8"))
        print(f"Message: {message} Sent to {client_socket.getfqdn(client_socket[0])}")

s= Server(1)
s.run()
