from socketserver import TCPServer, BaseRequestHandler
import argparse
import psycopg2

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
                response = self.server.model_path[0] + "\n" + self.server.model_path[1]
            case ("log"):
                ip_address, timestamp,log_string = data.split("\n")[1].split(":")
			
                try:
                    conn = psycopg2.connect(
                        dbname = "postgres",
                        user = "userMH",
                        password = "654321",
                        host="localhost",
                        port = "5432"
                    )
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO logs (ip_address,timestamp,log_string) VALUES (%s, %s, %s);", 
                        (ip_address,timestamp,log_string)
                    )
			
                    conn.commit()
                    cursor.close()
                    conn.close()
                    #Fix to log in database
                    print(data.split("\n")[1])
                    response = "Logged"
                except  psycopg2.Error as e:
                    response = f"Error: {e}"
                
            case (_):
                response = "Unknown command"
        self.request.sendall(response.encode())
  
def open_server(port : int, model_server_adresse : str, model_server_port : int):
    """Opens the server

    Args:
        port (int): the port to open the server on
    """
    with ManagerServer(("localhost", port), (model_server_adresse, model_server_port), TCPHandler) as server :
        print("Server started")
        server.serve_forever()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Manager server")
    parser.add_argument("--port", type=int, help="Port to open server on")
    parser.add_argument("--modelIP", type=str, help="Address of the model server")
    parser.add_argument("--modelPort", type=int, help="Port of the model server")
    arguments = parser.parse_args()
    if arguments.port and arguments.modelIP and arguments.modelPort:
        open_server(arguments.port, arguments.modelIP , arguments.modelPort)
    else:
        parser.print_help()
