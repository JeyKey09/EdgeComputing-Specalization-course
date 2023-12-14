from socketserver import TCPServer, BaseRequestHandler
from socket import socket
import learning
from keras import Sequential
import sys

class ManagerServer(TCPServer):
    def __init__(self, server_address, model_server_adresse, RequestHandlerClass,  bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.model_server : str =  model_server_adresse
      
class TCPHandler(BaseRequestHandler):
    def handle(self):
        data : str = self.request.recv(1024).strip().decode("utf-8")
        response : str = "" 
        match (data.split("\n")[0]):
            case ("fetch modelserver"):
                response = self.server.model_path
            case ("log"):
                #Fix to log in database
                print(data.split("\n")[1])
                response = "Logged"
            case (_):
                response = "Unknown command"
        self.request.sendall(response.encode())
  
def open_server(port : int, model_server_adresse : str, model_server_port : int):
    """Opens the server

    Args:
        port (int): the port to open the server on
    """
    with MyServer(("localhost", port), (model_server_adresse, model_server_port), TCPHandler) as server :
        print("Server started")
        server.serve_forever()
        
if __name__ == "__main__":
    arguments = sys.argv
    if len(arguments) == 3:
        open_server(int(arguments[1]), arguments[2], int(arguments[3]))
    else:
        print("Usage: python3 managerserver.py <port> <modelserver ip> <modelserver port>")