import tensorflow as tf
from keras.models import Sequential
from keras.datasets import cifar10
from keras.layers import Dense, Dropout, Flatten
from keras.applications import MobileNetV2  # Import InceptionResNetV2
from keras.callbacks import EarlyStopping
from datetime import datetime
import os

save_path = "models/"

def fetch_model() -> str:
       """Fetches the latest model from the server
       
       Returns:
              str: The name of the model
       """
       if not os.path.isdir(save_path):
              os.mkdir(save_path)
       files = os.listdir(save_path)
       files.sort()
       for file in files:
              if file.endswith(".keras"):
                     return save_path+file
       return create_model()
       
def create_model() -> str:
       """Creates a new model and saves it to the models folder

       Returns:
       str: The filename of the model
       """
       # Load the data
       (x_train, y_train), (_, _) = cifar10.load_data()

       # Reshape and normalize the data
       x_train = x_train.astype('float32') / 255.0

       # One-hot encode the labels
       y_train = tf.keras.utils.to_categorical(y_train, 10)

       # Create the InceptionResNetV2 base model (pre-trained on ImageNet)
       base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(32, 32, 3))

       # Create a sequential model
       model = Sequential()

       # Add the InceptionResNetV2 base model as the initial layer
       model.add(base_model)
       base_model.trainable=False
       # Flatten the output of the base model
       model.add(Flatten())

       # Add a dense layer with 64 nodes and ReLU activation
       model.add(Dense(64, activation='relu'))

       # Add dropout layer
       model.add(Dropout(0.25))

       # Add another dense layer with 64 nodes and ReLU activation
       model.add(Dense(64, activation='relu'))

       # Add dropout layer
       model.add(Dropout(0.25))

       # Add the output layer with 10 nodes for classification
       model.add(Dense(10, activation='softmax'))

       # Compile the model
       model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

       # Print a summary of the model architecture
       model.summary()

       # Fit the model
       callback = EarlyStopping(monitor='loss', patience=3, min_delta=0.01)

       model.fit(x_train, y_train, batch_size=128, epochs=10, verbose=1, validation_split=0.1, callbacks=[callback])

       # Save the model
       date = datetime.now().strftime("%d-%m-%Y_%H-%M")
       filename = f"{save_path}model-{date}.keras"
       model.save(filename)

       return filename

# Call the function to create and train the model