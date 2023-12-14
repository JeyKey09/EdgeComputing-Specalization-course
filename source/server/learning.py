import tensorflow as tf
from keras.models import Sequential
from keras.datasets import cifar10
from keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D, InputLayer
from keras.callbacks import EarlyStopping
from datetime import datetime

def create_model() -> str:
       # Load the data
       (x_train, y_train), (x_test, y_test) = cifar10.load_data()

       # Reshape the data
       x_train = x_train.reshape(50000, 32, 32, 3)
       x_test = x_test.reshape(10000, 32, 32, 3)

       # Normalize the data
       x_train = x_train / 255
       x_test = x_test / 255

       # One-hot encode the labels
       y_train = tf.keras.utils.to_categorical(y_train, 10)
       y_test = tf.keras.utils.to_categorical(y_test, 10)

       model : Sequential = Sequential([InputLayer(input_shape=(32, 32, 3)),
              Conv2D(filters=32, kernel_size=3,
                     strides=(2, 2), activation='relu'),
              MaxPooling2D(pool_size=(2, 2)),
              Dropout(0.25),
              Conv2D(filters=64, kernel_size=3,
                     strides=(2, 2), activation='relu'),
              MaxPooling2D(pool_size=(2, 2)),
              Flatten(),
              Dense(100, activation='relu'),
              Dense(10, activation='softmax')])
       callback = EarlyStopping(monitor='loss', patience=3, min_delta=0.01)

       model.compile(loss='categorical_crossentropy',optimizer='adam',metrics=['accuracy'])

       model.fit(x_train, y_train, batch_size=128, epochs=10, verbose=1, validation_split=0.1, callbacks=[callback])
       
       
       date = datetime.now().strftime("%d-%m-%Y_%H-%M")
       filename = f"model-{date}.keras"
       
       model.save("models/"+filename)
       
       return filename