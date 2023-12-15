from socketserver import ThreadingMixIn, TCPServer, BaseRequestHandler
import socket
import learning
from keras import Sequential

class ModelServer(ThreadingMixIn, TCPServer):
	def __init__(self, server_address, RequestHandlerClass, bind_and_activate=True):
		super().__init__(server_address, RequestHandlerClass, bind_and_activate)
		self.model_path : str =  learning.fetch_model()
	  
class TCPHandler(BaseRequestHandler):
	def handle(self):
		while self.request.fileno() != -1:
			data : str = self.request.recv(1024).strip().decode("utf-8")
			response : str = "" 
			match (data.split("\n")[0].lower()):
				case ("what model"):
					print("Client asked for model")
					response = self.server.model_path.split("/")[-1]
				case ("fetch model"):
					print("Client asked for model")
					with open(self.server.model_path, "rb") as file:
						file_data = file.read(4096)
						while file_data:
							self.request.sendall(file_data)
							file_data = file.read(4096)
						response = ""
					self.request.close()
				case ("train model"):
					print("Client asked for training new model")
					self.server.model_path = learning.create_model()
					response = "New Model Trained"
				case (""):
					response = ""
				case (_):
					response = "Unknown command"
			if response != "":
				self.request.sendall(response.encode())
  
def open_server(port : int):
	"""Opens the server

	Args:
		port (int): the port to open the server on
	"""
	ip = socket.gethostbyname(socket.gethostname())
	with ModelServer((ip, port), TCPHandler) as server :
		print("Server started")
		server.serve_forever()
		
if __name__ == "__main__":
	open_server(50000)