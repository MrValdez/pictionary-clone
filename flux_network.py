class Network:
    def update(self):
        packet, data = None, None
        return packet, data

class NetworkServer(Network):
    def __init__(self):
        print("Server ready")

class NetworkClient(Network):
    def __init__(self):
        #self.player_name = input("What is your name? ")
        self.player_name = "Brave sir Robin"

        #server_address = input("Hostname/IP address of server? ")
        server_address = "localhost"
        #server_address = "shuny"