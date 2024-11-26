import socket as sock
from threading import Thread, Lock, Condition

class Server:
    def __init__(self, members, ip=None, port=9353):
        self.ip = ip                            # Host's ip address: Local(Private) ip that host machine is currently running on.
        self.port = port                        # Host's port: Integer value that need to be more than 1023 and less than 65535.
        self.members = members                  # Number of participants of the game.
        self.clients = {}                       # A dict to store connected clients.
        self.lock = Lock()
        self.condition = Condition(self.lock)
        self.data = None

    def __len__(self):
        return len(self.clients)

    def __repr__(self):
        return f"Host Server Running At {self.ip}:{self.port}"

    def ip_check(self) -> None:
        """
        Checks if passed ip address is valid or not.
        args: None
        returns: None
        """
        if self.ip is None:
            try:
                # Try a simple ping connection to 1.1.1.1 to get the private ip address
                with sock.socket(sock.AF_INET, sock.SOCK_DGRAM) as connection:
                    connection.settimeout(2)
                    connection.connect(("1.1.1.1", 80))
                    ip = connection.getsockname()
                    if ip[0].startswith("127"):
                        raise OSError
                    # Assigning new valid ip address
                    self.ip = ip[0]
                    return

            except OSError as e:
                print(f"Function \"ip_check\" throws an Exception:\t{e}")
            except Exception as e:
                print(f"Crashed due unhandled Exception:\t{e}")

        try:
            with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as socket:
                socket.bind((self.ip, self.port))
        except OSError:
            self.ip = None
            self.ip_check()

    def start_server(self):
        """
        Starts the server at given ip address and port.
        args: None
        returns: None
        """

        self.ip_check()

        with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as socket:
            socket.bind((self.ip, self.port))
            socket.listen(self.members)
            print(self)

            while len(self.clients) < self.members:
                client_socket, client_address = socket.accept()
                self.clients[client_socket] = client_address

                if not len(self.clients) == self.members:
                    print(f"Waiting for {self.members - len(self.clients)} other client to join!")

                # TODO: NEED TO CHECK IF CLIENT IS STILL ALIVE
                if len(self.clients) == self.members:
                    for client,address in self.clients.items():
                        client_thread = Thread(target=self.handle_client, args=(client, address))
                        client_thread.start()

    def handle_client(self, client_socket: sock.socket, client_address):
        with client_socket:
            print(f"Connection established with {sock.getfqdn(client_address[0])} from {client_address[0]}")
            while True:
                data = client_socket.recv(1024).decode(encoding="utf-8")
                if not self.data:
                    print(f"Connection Closed by client{client_address}")
                    break
                with self.lock:
                    self.data = data
                    self.condition.notify_all()
    # TODO:NOT FINISHED YET
    def get_command(self):
        with self.condition:
            while self.condition is None:
                self.condition.wait()
            data = self.data
            self.data = None
        return data
