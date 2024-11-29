import threading
import time
from threading import Thread, Lock, Condition
import socket as sock

class Server:
    def __init__(self, members):
        self.__ip = self.__set_ip()                                 # Host's ip address: Local(Private) ip that host machine is currently running on.
        self.__received_data = None                      # Received data from Client.
        self.found = False                               # Stores a conditional variable(is host founded by clients or not)
        self.__port = 9353                               # Host's port.
        self.__members = members                         # Number of participants of the game.
        self.__clients = {}                              # A dict{socket object:client ip} to store connected clients.
        self.__lock = Lock()                             # For thread Syncing.
        self.__condition = Condition(self.__lock)        # For thread locking.

    def __len__(self) -> int:
        return len(self.__clients)

    def __repr__(self) -> str:
        return f"Host Server is running on {self.__ip}:{self.__port}"

    def __set_ip(self) -> None:
        """
        Sets the ip address of the Host server.
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
            print(f"Function \"ip_check\" throws an Exception:\n{e}")
        except Exception as e:
            print(f"Crashed due unhandled Exception:\n{e}")

    # Handles the communication between host and clients.
    def __handle_client(self, client_socket, client_address) -> None:
        """
         Handles the communication between host and clients.
         Args: socket object, socket address
         returns: None
        """
        try:
            with client_socket:
                print(f"Connection established with {sock.getfqdn(client_address[0])} from {client_address[0]}")
                # Waiting for data from client.
                while True:
                    received_data = client_socket.recv(1024).decode()
                    if not received_data:
                        continue
                    # Notifies receive_data method if there is any received data from client.
                    with self.__lock:
                        self.send_data(client_socket, f"Received {received_data}")
                        self.__received_data = received_data
                        self.__condition.notify_all()
        finally:
            self.close()

    def __broadcast_message(self):
        with sock.socket(sock.AF_INET, sock.SOCK_DGRAM) as broadcaster:
            try:
                broadcaster.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
                broadcaster.setsockopt(sock.SOL_SOCKET, sock.SO_BROADCAST, 1)
                broadcaster.bind(("", self.__port))

                while not self.found:
                    broadcaster.sendto(f"Who is looking for game on the local network. tell {self.__ip}".encode("utf-8"),
                                   ("255.255.255.255", self.__port))
                    time.sleep(5)
            finally:
                broadcaster.close()

    def receive_data(self) -> None:
        """
        Stops the current work util receives a message from client.
        Args: None
        return: str
        """
        with self.__condition:
            while self.__received_data is None:
                self.__condition.wait()
            received = self.__received_data
            self.__received_data = None
        return received


    def run(self) -> None:
        """
        Runs the Host Server.
        args: None
        returns: None
        """
        self.__set_ip()

        # Starting the Host.
        with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as socket:
            socket.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
            socket.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEPORT, 1)
            socket.bind((self.__ip, self.__port))
            socket.listen(self.__members)

            # Printing Host Server's status(ip address, port).
            print(self)

            t = threading.Thread(target=self.__broadcast_message)
            t.start()

            # Loops till remaining members joins.
            while len(self) < self.__members:
                client_socket, client_address = socket.accept()
                self.__clients[client_socket] = client_address

                # Gives status about number of remaining members to join.
                if not len(self) == self.__members:
                    print(f"Waiting for {self.__members - len(self)} other client to join!")

                # Loops in clients dict to start thread for them.
                if len(self) == self.__members:
                    self.found = True
                    for client,address in self.__clients.items():
                        client_thread = Thread(target=self.__handle_client,
                                               args=(client, address),
                                               name=f"{address[0]}:{address[1]}",
                                               daemon=True)
                        client_thread.start()

    def send_data(self, client_socket: sock, message: str) -> None:
        """
        Sends a message to client.
        Args: socket object, str
        returns None
        """
        client_socket.sendall(message.encode())
        print(f"Message: {message} Sent to {client_socket.getfqdn(client_socket[0])}")

    def close(self):
        """
        Closes all the socket connections for appropriate exit.
        Args: None
        returns: None
        """
        for keys in list(self.__clients):
            keys.close()
