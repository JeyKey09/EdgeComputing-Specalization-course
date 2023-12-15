import cv2
import keras
import socket
import numpy as np
from datetime import datetime
import os


save_path = "models/"
manager_ip = "10.212.25.66"
port = 5050

# The answers to the CIFAR-10 dataset
# Unsure if it should be here or in the server
answers = {0: "airplane",
              1: "automobile",
              2: "bird",
              3: "cat",
              4: "deer",
              5: "dog",
              6: "frog",
              7: "horse",
              8: "ship",
              9: "truck"}

def download_model(ip : str, port : int):
    """Downloads the model if it is not already downloaded

    Args:
        ip (str): ip to the model server
        port (int): port to the model server

    Returns:
        _type_: _description_
    """
    if not os.path.isdir(save_path):
        os.mkdir(save_path)
    sock = socket.create_connection((ip, port))
    sock.sendall("what model".encode())
    filename = sock.recv(4096).strip().decode("utf-8")
    filepath = save_path+filename
    for file in os.listdir(save_path):
        if file == filename:
            sock.close()
            return filepath
        
    sock.sendall("fetch model".encode())
    with open(filepath, "wb") as file:
        file_data = sock.recv(1024).split().decode("utf-8")
        while file_data:
            file.write(file_data)
            file_data = sock.recv(1024).split().decode("utf-8")
            if file_data.endswith("\nModel sent"):
                file.write(file_data[:-10])
                break
    sock.close()
    
    return filepath
    
sock = socket.create_connection((manager_ip, port), timeout=5)

sock.sendall("fetch modelserver".encode())
modelServer = sock.recv(4096).strip().decode("utf-8")

modelServer = modelServer.split("\n")

model = keras.models.load_model(download_model(modelServer[0], int(modelServer[1])))

cameraIP = socket.gethostbyname(socket.gethostname())

cv2.namedWindow("preview")
vc = cv2.VideoCapture(0)

if vc.isOpened(): # try to get the first frame
    rval, frame = vc.read()
else:
    rval = False
    print("Could not open camera") 

while rval:
    cv2.imshow("preview", frame)
    frame = cv2.resize(frame, (32, 32)) / 255
    guess = answers[np.argmax(model.predict(np.array([frame]), verbose=0))]
    
    if guess == "automobile":
        logtime = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
        message = f"log\n {cameraIP} : {logtime} : {guess}"
        if sock.fileno() == -1:
            sock = socket.create_connection((manager_ip, port))
        sock.sendall(message.encode("utf-8"))
        print(sock.recv(4096).strip().decode("utf-8"))
        sock.close
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    
    if key == 27: # exit on ESC
        break
    
cv2.destroyWindow("preview")
vc.release()