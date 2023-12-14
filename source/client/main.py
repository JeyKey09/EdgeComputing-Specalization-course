import cv2
import pickle
import keras
import socket

ip = "127.0.0.1"
port = 5000

sock = socket.create_connection((ip, port), timeout=10)
sock.sendall("fetch model".encode())

model_path : str = sock.recv(1024).strip().decode("utf-8")

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
    rval, frame = vc.read()
    key = cv2.waitKey(20)
    
    if key == 27: # exit on ESC
        break
    elif key == 32: # spacebar to take a picture
        cv2.imwrite("test.png", frame)
        break
    
cv2.destroyWindow("preview")
vc.release()