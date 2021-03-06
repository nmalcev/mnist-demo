# coding: utf-8
# The objective of this script is to learn Keras early stopping feature
import numpy

from config import CNN_config
from model import create_MNIST_CNN, createModel1, createModel2, createModel3
from utils.dataset import load_dataset, getDataGen, repack_dataset
from utils.hardware import configureHardware
from utils.timer import Timer
from utils.training_plot import TrainingPlot
from utils.training_log import TrainingLog

from keras.callbacks import EarlyStopping, ModelCheckpoint
import keras.optimizers as KO


# Set the seed value for repeatability
numpy.random.seed(42)

configureHardware(num_GPU=1)

model = create_MNIST_CNN()
# ~ model = createModel1()
# ~ model.compile(loss='categorical_crossentropy', optimizer='SGD', metrics=['accuracy'])
model.compile(loss='categorical_crossentropy', optimizer=KO.Adam(lr=0.0001, epsilon=1e-8), metrics=['accuracy'])

# print(model.summary())

validation_split = 0.1

# Train the network
if CNN_config.use_fit_generator:
    X_train, X_test, Y_train, Y_test, validation_data = repack_dataset(validation_split, *load_dataset())
    # This will do preprocessing and realtime data augmentation:
    datagen = getDataGen()
    datagen.fit(X_train)
    # ~ plot_losses = TrainingPlot()
    training_log = TrainingLog()
    timer = Timer().start()
    earlyStopping = EarlyStopping(monitor='val_loss', mode='min', verbose=1)
    modelCheckpoint = ModelCheckpoint('best_model.h5', monitor='val_acc', mode='max', verbose=1, save_best_only=True)

    model.fit_generator(
        datagen.flow(X_train, Y_train, batch_size=CNN_config.batch_size),
        len(X_train),
        CNN_config.epochs,
        validation_data=validation_data,
        callbacks=[
            training_log, 
            earlyStopping, 
            modelCheckpoint
        ]
    )
    timer.stop().note('Prediction time')
    timer.summary()
	
else:
    X_train, X_test, Y_train, Y_test = load_dataset()

    model.fit(
        X_train, 
        Y_train, 
        batch_size=CNN_config.batch_size, 
        nb_epoch=CNN_config.epochs, 
        validation_split=validation_split, 
        # verbose=2 # this will hide the progress
    )

# We evaluate the quality of network training on test data
scores = model.evaluate(X_test, Y_test, verbose=0)
print("The accuracy on test dataset: %.2f%%" % (scores[1]*100))

# Get json description of model
model_json = model.to_json()

# Save model description in file
json_file = open(CNN_config.model_json_path, 'w')
json_file.write(model_json)
json_file.close()

# Save model weights in file
model.save_weights(CNN_config.model_weight_path, overwrite=True)
