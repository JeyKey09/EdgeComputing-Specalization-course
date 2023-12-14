import cv2
import keras
import socket
import numpy as np
from datetime import datetime

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


manager_ip = "127.0.0.1"
port = 5000

sock = socket.create_connection((manager_ip, port), timeout=10)

sock.sendall("fetch model".encode())
model_path : str = sock.recv(4096).strip().decode("utf-8")
sock.close()

model = keras.models.load_model("models/"+model_path)

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
        message = f"log\n {logtime} : {guess}"
        sock = socket.create_connection((ip, port), timeout=10)
        sock.sendall(message.encode("utf-8"))
        print(sock.recv(4096).strip().decode("utf-8"))
        sock.close
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    
    if key == 27: # exit on ESC
        break
    
cv2.destroyWindow("preview")
vc.release()