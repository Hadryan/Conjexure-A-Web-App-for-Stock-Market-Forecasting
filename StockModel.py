import numpy as np
import pandas as pd
import tensorflow as tf

import matplotlib.pyplot as plt

from tensorflow.keras import layers
from sklearn.preprocessing import MinMaxScaler

tf.random.set_seed(7)
np.random.seed(7)

class Model_related_things():
    def __init__(self,Outputdays = 7, inputdays = 30):

        self.Outputdays = Outputdays
        self.inputdays = inputdays

        tf.keras.backend.clear_session()
        self.model = tf.keras.Sequential()

        self.model.add(layers.Conv1D(128,5,1,padding = "causal",activation = "relu",input_shape=[None, 1]))
        for j in [128,128]:
            self.model.add(layers.LSTM(j, return_sequences=True))
        self.model.add(layers.LSTM(128))
        for i in [64,64,Outputdays]:
            self.model.add(layers.Dense(i, activation="selu"))

    def plsgivedataset(self, series):
        window_size = self.inputdays
        predday = self.Outputdays
        shuffle_buffer = 1000

        batch_size = 4

        ds = tf.data.Dataset.from_tensor_slices(series)
        ds = ds.window(window_size + predday, shift=1, drop_remainder=True)
        ds = ds.flat_map(lambda w: w.batch(window_size + predday))
        ds = ds.shuffle(shuffle_buffer)
        ds = ds.map(lambda w: (w[:predday], tf.squeeze(w[-predday:])))
        ds = ds.batch(batch_size).prefetch(3)

        return ds
    
    def trainModel(self, traindata):

        scaler = MinMaxScaler(feature_range=(0,0.75))

        ser = traindata.reshape(-1,1)
        series = scaler.fit_transform(ser)
        
        ds = self.plsgivedataset(series)

        optimizer = tf.keras.optimizers.Adam(lr=1e-1)
        l = tf.keras.losses.LogCosh()
        self.model.compile(optimizer = "SGD", loss = "mse" , metrics=[l])
        
        h = self.model.fit(ds,epochs=20,verbose=1)
        hist = h.history

        return hist


Apple_data = pd.read_csv("data_googl.csv")

window = 30
predday = 7

print(len(Apple_data))

newmodel = Model_related_things(predday,window)
plt.plot(newmodel.trainModel(Apple_data.Close.values)["loss"])
plt.show()

