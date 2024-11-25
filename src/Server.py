import socket as sock

class Server:
    def __init__(self, members, ip=None, port=9353):
        self.ip = ip           # Host's ip address: Local(Private) ip that host machine is currently running on.
        self.port = port       # Host's port: Integer value that need to be more than 1023 and less than 65535.
        self.members = members # Number of participants of the game.
        self.clients = []      # A list to store connected clients.

    def __enter__(self):
        self.ip_check()
        self.start_server()

    def __exit__(self):
        for client in self.clients:
            client.close()

    def __len__(self):
        return len(self.clients)

    def __repr__(self):
        return f"Host Server Running At {self.ip}:{self.port}"

    # TODO: START_SERVER FUNCTION HATE TO USE THIS FUNCTION IN FUTURE.
    def ip_check(self) -> None:
        """
        Checks if passed ip address is valid or not.
        args:None
        returns: None
        """
        if self.ip is None:
            try:
                # Try a simple ping connection to 1.1.1.1 to get the private ip address
                with sock.socket(sock.AF_INET, sock.SOCK_DGRAM) as connection:
                    connection.settimeout(0)
                    connection.connect(("1.1.1.1", 80))
                    ip = connection.getsockname()
                    if ip[0].startswith("127"):
                        raise OSError
                    # Assigning new valid ip address
                    self.ip = ip[0]

            except OSError as e:
                print(f"Function \"ip_check\" throw an Exception:\t{e}")
            except Exception as e:
                print(f"Crashed due unhandled Exception:\t{e}")

    # TODO: NOT FINISHED YET
    def start_server(self):
        """
        Starts the server at given ip address and port.
        args: None
        returns: None
        """
        with sock.socket(sock.AF_INET, sock.SOCK_STREAM) as socket:
            socket.bind((self.ip, self.port))
            socket.listen(self.members)
            print(self)

            while True:
                client_socket, client_address = socket.accept()

                if len(self.clients) >= self.members:
                    continue

                self.clients.append(client_socket)

