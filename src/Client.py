import socket as sock

class Client:
    def __init__(self):
        self.__ip = None
        self.__port = None
        self.server_found = False
        self.__run_listener()

    def __run_listener(self):
        with sock.socket(sock.AF_INET, sock.SOCK_DGRAM) as listener:
            listener.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEADDR, 1)
            listener.setsockopt(sock.SOL_SOCKET, sock.SO_REUSEPORT, 1)
            listener.setsockopt(sock.SOL_SOCKET, sock.SO_BROADCAST, 1)
            listener.bind(("", 12345))

            while not self.server_found:
                message = listener.recv(1024)
                self.__message_parser(message.decode("utf-8"))

    def __message_parser(self, message: str):
        if "Liars-Bar" in message.split("\""):
            ip = message.split(":")[1]
            port = message.split(":")[2]
            print(ip, port)
