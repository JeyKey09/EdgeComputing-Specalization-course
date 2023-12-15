from socketserver import TCPServer, BaseRequestHandler
from socket import socket
import learning
from keras import Sequential

class ModelServer(TCPServer):
    def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.model_path : str =  learning.fetch_model()
      
class TCPHandler(BaseRequestHandler):
    def handle(self):
        data : str = self.request.recv(1024).strip().decode("utf-8")
        response : str = "" 
        match (data.split("\n")[0]):
            case ("what model"):
                response = self.server.model_path.split("/")[-1]
            case ("fetch model"):
                with open(self.server.model_path, "rb") as file:
                    file_data = file.read(1024)
                    while data:
                        self.request.sendall(file_data)
                        file_data = file.read(1024)
                    response = "\n Model sent"
            case ("train model"):
                self.server.model_path = learning.create_model()
                response = "New Model Trained"
            case (_):
                response = "Unknown command"
        self.request.sendall(response.encode())
  
def open_server(port : int):
    """Opens the server

    Args:
        port (int): the port to open the server on
    """
    with ModelServer(("localhost", port), TCPHandler) as server :
        print("Server started")
        server.serve_forever()
        
if __name__ == "__main__":
    open_server(5000)