from socketserver import TCPServer, BaseRequestHandler
from socket import socket
import pickle
import learning
from keras import Sequential

class MyServer(TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.model_path : str =  learning.create_model()
      
class UDPHandler(BaseRequestHandler):
    
    def handle(self):
        data : str = self.request.recv(1024).strip().decode("utf-8")
        response : str = "" 
        match (data.split("\n")[0]):
            case ("fetch model"):
                response = self.server.model_path
            case ("train model"):
                self.server.model_path = learning.create_model()
                response = "Model trained"
            case ("log"):
                print(data.split("\n")[1])
                reponse = "Logged"
            case (_):
                response = "Unknown command"
        self.request.sendall(response.encode())
  
def open_server(port : int):
    """Opens the server

    Args:
        port (int): the port to open the server on
    """
    with MyServer(("localhost", port), UDPHandler) as server :
        server.serve_forever()
        
if __name__ == "__main__":
    open_server(5000)