from importlib.util import source_hash
from threading import Thread, Lock, Condition
import socket as sock
import random as rd
import time

class Server:
    def __init__(self, members):
        self.__ip = None                                 # Host's ip address: Local(Private) ip that host machine is currently running on.
        self.__data = None
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

    def start_server(self):
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
                        client_thread = Thread(target=self.handle_client, args=(client, address))
                        client_thread.start()

    def handle_client(self, client_socket: sock.socket, client_address):
        with client_socket:
            print(f"Connection established with {sock.getfqdn(client_address[0])} from {client_address[0]}")
            while True:
                data = client_socket.recv(1024).decode(encoding="utf-8")
                if not data:
                    print(f"Connection Closed by client{client_address}")
                    time.sleep(0.5)
                    continue
                with self.lock:
                    self.data = data
                    self.condition.notify_all()
    # TODO:NOT FINISHED YET
    def get_command(self):
        with self.condition:
            while self.data is None:
                self.condition.wait()
            data = self.data
            self.data = None
        return data

# s = Server(1, ip="192.168.146.158")
# s.start_server()
# while True:
#     mamad = s.get_command()
#     print(mamad)