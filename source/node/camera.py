import cv2
import keras
import socket
import numpy as np
from datetime import datetime
import os
import time


save_path = "models/"
manager_ip = "10.212.25.66"
port = 50500

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
	with socket.create_connection((ip, port), timeout=30) as sock:
		sock.sendall("what model".encode())
		filename = sock.recv(4096).strip().decode("utf-8")
		filepath = save_path+filename
		for file in os.listdir(save_path):
			if file == filename:
				return filepath
		sock.sendall("fetch model".encode())
		with open(filepath, "wb") as file:
			file_data = sock.recv(4096)
			try:
				while file_data:
					file.write(file_data)
					file_data = sock.recv(4096)
			except:
				print("Error happened")
		return filepath
		
	
sock = socket.create_connection((manager_ip, port))

sock.sendall("fetch modelserver".encode())
modelServer = sock.recv(4096).strip().decode("utf-8")
sock.close()

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

counter = (0, "")
while rval:
	cv2.imshow("preview", frame)
	frame = cv2.resize(frame, (32, 32)) / 255
	guess = answers[np.argmax(model.predict(np.array([frame]), verbose=0))]
	
	if guess == "automobile" or guess == "truck":
		if counter[0] == 4 and counter[1] == guess:
			logtime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			message = f"log\n{cameraIP}::{logtime}::{guess}"
			if sock.fileno() == -1:
				sock = socket.create_connection((manager_ip, port))
			sock.sendall(message.encode("utf-8"))
			print(sock.recv(4096).strip().decode("utf-8"))
			sock.close()
			counter = (0, "") 
		elif counter[1] == guess:
			counter = (counter[0] + 1, guess)
		else:
			counter = (1, guess)
	rval, frame = vc.read()
	key = cv2.waitKey(20)
	
	if key == 27: # exit on ESC
		break
cv2.destroyWindow("preview")
vc.release()