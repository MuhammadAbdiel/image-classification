# -*- coding: utf-8 -*-
"""Image_Classification.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1XFQPcrtRDqR63ILU-INruk7FMJ7358-S

# **Muhammad Abdiel Firjatullah**

### Image Classification
"""

from google.colab import files

files.upload()

!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d muratkokludataset/rice-image-dataset

zipPath = '../content/rice-image-dataset.zip'
zipFile = zipfile.ZipFile(zipPath, 'r')
zipFile.extractall('../content/RiceDataset/')
zipFile.close()

FILE_PATH = '../content/RiceDataset/Rice_Image_Dataset/'

# Commented out IPython magic to ensure Python compatibility.
import zipfile,os,shutil
import sklearn
from sklearn import datasets
from sklearn.model_selection import train_test_split
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import Callback, EarlyStopping
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Flatten, Dense, Conv2D, MaxPooling2D, Dropout, BatchNormalization
from tensorflow.keras.layers import Dropout
from tensorflow.keras.optimizers import Adam
import numpy as np
from keras.preprocessing import image
import pathlib
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
# %matplotlib inline

arborio_dir = os.path.join(FILE_PATH,'Arborio')
basmati_dir = os.path.join(FILE_PATH, 'Basmati')
ipsala_dir = os.path.join(FILE_PATH, 'Ipsala')
jasmine_dir = os.path.join(FILE_PATH, 'Jasmine')
karacadag_dir = os.path.join(FILE_PATH, 'Karacadag')

total_arborio = len(os.listdir(arborio_dir))
total_basmati = len(os.listdir(basmati_dir))
total_ipsala = len(os.listdir(ipsala_dir))
total_jasmine = len(os.listdir(jasmine_dir))
total_karacadag = len(os.listdir(karacadag_dir))

print("Arborio Image      : ", total_arborio)
print("Basmati Image      : ", total_basmati)
print("Ipsala Image       : ", total_ipsala)
print("Jasmine Image      : ", total_jasmine)
print("Karacadag Image    : ", total_karacadag)

IMG_HEIGHT = 150
IMG_WIDTH = 150
BATCH_SIZE = 64

val_size = 0.2

Train_datagen = ImageDataGenerator(
    rescale = 1.0/255,
    rotation_range = 20,
    horizontal_flip = True,
    shear_range = 0.2,
    fill_mode = 'nearest',
    validation_split = val_size
)

Validation_datagen = ImageDataGenerator(
    rescale = 1./255,
    validation_split = val_size
)

Train_generator = Train_datagen.flow_from_directory(
    FILE_PATH,
    target_size = (IMG_HEIGHT, IMG_WIDTH),
    batch_size = BATCH_SIZE,
    class_mode = 'categorical',
    subset = 'training'
)

Validation_generator = Validation_datagen.flow_from_directory(
    FILE_PATH,
    target_size = (IMG_HEIGHT, IMG_WIDTH),
    batch_size = BATCH_SIZE,
    class_mode = 'categorical',
    subset='validation'
)

target_names = ['Arborio', 'Basmati', 'Ipsala', 'Jasmine', 'Karacadag']

Model = Sequential(
    [
      Conv2D(filters = 16, kernel_size = (5, 5), padding = 'Same', activation = 'relu', input_shape = (IMG_HEIGHT, IMG_WIDTH, 3)),
      MaxPooling2D(pool_size = (2,2)),
      Dropout(0.2),
      BatchNormalization(),

      Conv2D(filters = 32, kernel_size = (3, 3), padding = 'Same', activation = 'relu'),
      MaxPooling2D(pool_size = (2,2), strides = (2, 2)),
      Dropout(0.2),

      Conv2D(filters = 64, kernel_size = (3, 3), padding = 'Same', activation = 'relu'),
      MaxPooling2D(pool_size = (2,2), strides = (2, 2)),
      Dropout(0.2),

      Flatten(),
      Dense(64, activation='relu'),
      Dropout(0.2),
      Dense(5, activation='softmax')
    ]
)

Adam(learning_rate=0.00146, name='Adam')
Model.compile(optimizer = 'Adam', loss = 'categorical_crossentropy', metrics = ['accuracy'])

class EarlyStopByAccuracy(tf.keras.callbacks.Callback):
	def on_epoch_end(self, epoch, logs={}):
		if(logs.get('accuracy') >= 0.95 and logs.get('val_accuracy') >= 0.95):
			print("\nAccuracy and Validation Accuracy has reached 95%!\nStop Train!")
			self.model.stop_training = True

callbacks = EarlyStopByAccuracy()

EarlyStop = EarlyStopping(
    monitor = 'val_loss',
    min_delta = 0.0001,
    patience = 5,
    verbose = 1,
    mode = 'auto'
)

history = Model.fit(
  Train_generator,
  epochs =  100,
  validation_data = Validation_generator,
  verbose = 1,
  callbacks =[callbacks, EarlyStop]
)

print("Loss with Val_Loss Graph")
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'test'], loc = 'upper right')
plt.show()

print("Acc with Val_Acc Graph")
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epoch')
plt.legend(['train', 'test'], loc='lower right')
plt.show()

export_dir = 'saved_model/'
tf.saved_model.save(Model, export_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

tflite_model_file = pathlib.Path('RiceModel.tflite')
tflite_model_file.write_bytes(tflite_model)