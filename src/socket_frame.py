import random
from multiprocessing import Process, Queue, Value, Array, Manager, Pool
import concurrent.futures
import socket
import select



class Frame:
    '''
    implements the game session, manages the deck and keeps track of suits in construction
    '''
    def __init__(self,n):
        self.n = n
        self.serve = True
        self.connecting()
        """
        stored in a shared memory
        """
        with Manager() as manager:
            self.shared_l1 = manager.list()
            self.shared_l2 = manager.list()
            for _ in range(n):
                self.shared_l2(manager.list())#suits_in_construction = [[],[],[],[]] if 4 players
            self.shared_l3 = manager.list()
            self.shared_v1 = Value('i',n)
            self.shared_v2 = Value('i',3)
        self.shared_memory = {"l1":self.shared_l1,
                              "l2":self.shared_l2,
                              "l3":self.shared_l3,
                              "v1":self.shared_v1,
                              "v2":self.shared_v2}
    """
    fuunction of connecting to player process via socket
    """
    def connecting(self):
        HOST = "localhost"
        PORT = 8848
        with concurrent.futures.ProcessPoolExecutor() as executor:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((HOST, PORT))
                server_socket.listen(self.n)
                while self.serve:
                    readable, _, _ = select.select([server_socket], [], [], 1)
                    if server_socket in readable:
                        client_socket, address = server_socket.accept()
                        executor.submit(self.client_handler,client_socket,address)

    def client_handler(self,client_socket,address,shared_memory):
        with client_socket as s:
            print("Connected to client: ", address)
            # data = client_socket.recv(1024)
            (data, ancdata, _, _) = s.recvmsg(256, socket.CMSG_SPACE(256))
            while len(data):
                for cmsg_level, cmsg_type, cmsg_data in ancdata:
                    if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
                        message_type =  cmsg_data.decode()
                        if message_type == "l1":
                            m = "called l1"
                            print("called l1")
                            print("data: ", data.decode())
                            s.sendmsg([m.encode()], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, message_type.encode())])
                        elif message_type == "l2":
                            m = "called l2"
                            print("called l2")
                            print("data: ", data.decode())                            
                            s.sendmsg([m.encode()], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, message_type.encode())])
                        elif message_type == "l3":
                            m = "called l3"
                            print("called l3")
                            print("data: ", data.decode())
                            s.sendmsg([m.encode()], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, message_type.encode())])
                        elif message_type == "v1":
                            print("called v1")
                            print("data: ", data.decode())
                            m = "called v1"
                            s.sendmsg([m.encode()], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, message_type.encode())])
                        elif message_type == "v2":
                            print("called l1")
                            print("data: ", data.decode())
                            m = "called v2"
                            s.sendmsg([m.encode()], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, message_type.encode())])
                        else:
                            client_socket.sendall("error")
                data = client_socket.recv(1024)
            print("Disconnecting from client: ", address)

        
class Player:
    """
    """
    def __init__(self):
        self.connect_to_game()

    def connect_to_game(self): 
        HOST = "localhost"
        PORT = 8848
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((HOST, PORT))
            while True:
                for i in range(5):
                    client_socket.sendmsg([str(i).encode()], [(socket.SOL_SOCKET, socket.SCM_RIGHTS, "l1".encode())])
                    print("sent to l1", str(i))
                    (data, ancdata, _, _) = client_socket.recvmsg(256, socket.CMSG_SPACE(256))
                    for cmsg_level, cmsg_type, cmsg_data in ancdata:
                        if cmsg_level == socket.SOL_SOCKET and cmsg_type == socket.SCM_RIGHTS:
                            print(cmsg_data.decode())
                            print(data.decode())
                break
            client_socket.sendall(b'')