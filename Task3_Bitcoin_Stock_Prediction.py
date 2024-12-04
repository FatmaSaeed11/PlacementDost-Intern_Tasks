# -*- coding: utf-8 -*-
"""PlacementDost_Task3_last .ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1JNeCRQ4fpbGVd5JEnQ_UUVEaw-MBTc0V

Bitcoin price prediction

import important libraries
"""

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import tensorflow as tf
import plotly.express as px


from itertools import cycle
from tensorflow import keras
from keras.utils import normalize,to_categorical
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.models import Model
from keras.layers import Flatten, GlobalMaxPooling1D, Embedding, Conv1D, LSTM,Activation, Dropout, Dense,Bidirectional, Input

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score,classification_report

"""load dataset"""

dataset=pd.read_csv('/content/BTC-USD.csv')

dataset.info()

dataset.shape

dataset.head()

dataset.describe()

"""check null values"""

print('Null:',dataset.isnull().values.sum())

"""check starting and ending date"""

sd=dataset.iloc[0][0]
ed=dataset.iloc[-1][0]


print('Starting Date',sd)
print('Ending Date',ed)

"""overall analysis"""

dataset['Date'] = pd.to_datetime(dataset['Date'], format='%Y-%m-%d')

y_overall = dataset.loc[(dataset['Date'] >= '2023-05-15')
                     & (dataset['Date'] <= '2024-05-15')]

y_overall.drop(y_overall[['Adj Close','Volume']],axis=1)

"""order data by months"""

monthvise= y_overall.groupby(y_overall['Date'].dt.strftime('%B'))[['Open','Close']].mean()
new_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
             'September', 'October', 'November', 'December']
monthvise = monthvise.reindex(new_order, axis=0)
monthvise

"""plot stock analysis"""

names = cycle(['Stock Open Price','Stock Close Price','Stock High Price','Stock Low Price'])

fig = px.line(y_overall, x=y_overall.Date, y=[y_overall['Open'], y_overall['Close'],
                                          y_overall['High'], y_overall['Low']],
             labels={'Date': 'Date','value':'Stock value'})
fig.update_layout(title_text='Stock analysis chart', font_size=15, font_color='black',legend_title_text='Stock Parameters')
fig.for_each_trace(lambda t:  t.update(name = next(names)))
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)

fig.show()

"""Build model

dataframe for date and close
"""

closedf = dataset[['Date','Close']]
print("Shape of close dataframe:", closedf.shape)

"""plot all period of timeframe"""

fig = px.line(closedf, x=closedf.Date, y=closedf.Close,labels={'date':'Date','close':'Close Stock'})
fig.update_traces(marker_line_width=2, opacity=0.8, marker_line_color='orange')
fig.update_layout(title_text='Whole period of timeframe of Bitcoin close price 2023-2024', plot_bgcolor='white',
                  font_size=15, font_color='black')
fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)
fig.show()

"""preprocessing"""

del closedf['Date']
scaler=MinMaxScaler(feature_range=(0,1))
closedf=scaler.fit_transform(np.array(closedf).reshape(-1,1))
print(closedf.shape)

training_size=int(len(closedf)*0.60)
test_size=len(closedf)-training_size
train_data,test_data=closedf[0:training_size,:],closedf[training_size:len(closedf),:1]
print("train_data: ", train_data.shape)
print("test_data: ", test_data.shape)

def create_dataset(dataset, time_step=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-time_step-1):
        a = dataset[i:(i+time_step), 0]
        dataX.append(a)
        dataY.append(dataset[i + time_step, 0])
    return np.array(dataX), np.array(dataY)

time_step = 15
X_train, y_train = create_dataset(train_data, time_step)
X_test, y_test = create_dataset(test_data, time_step)

print(X_train.shape)
print(X_test.shape)
print(y_train.shape)
print(y_test.shape)

X_train =X_train.reshape(X_train.shape[0],X_train.shape[1] , 1)
X_test = X_test.reshape(X_test.shape[0],X_test.shape[1] , 1)

print( X_train.shape)
print( X_test.shape)

"""build LSTM model"""

model=Sequential()

model.add(LSTM(10,input_shape=(None,1),activation="relu"))

model.add(Dense(1))

"""print  model summary"""

model.summary()

"""compile the model"""

model.compile(loss="mean_squared_error",optimizer="adam")

"""fit the model"""

history=model.fit(X_train, y_train, validation_data=(X_test, y_test),epochs=250, batch_size=128)

"""plot loss of training and validation"""

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs = range(len(loss))

plt.plot(epochs, loss, 'r', label='Training loss')
plt.plot(epochs, val_loss, 'b', label='Validation loss')
plt.title('Training and validation loss')
plt.legend(loc=0)
plt.figure()


plt.show()

"""prediction"""

train_predict=model.predict(X_train)
test_predict=model.predict(X_test)
print(train_predict.shape)
print(test_predict.shape)

"""prediction for next 60 days"""

x_input=test_data[len(test_data)-time_step:].reshape(1,-1)
temp_input=list(x_input)
temp_input=temp_input[0].tolist()

from numpy import array

lst_output=[]
n_steps=time_step
i=0
pred_days = 60
while(i<pred_days):

    if(len(temp_input)>time_step):

        x_input=np.array(temp_input[1:])

        x_input = x_input.reshape(1,-1)
        x_input = x_input.reshape((1, n_steps, 1))

        yhat = model.predict(x_input, verbose=0)

        temp_input.extend(yhat[0].tolist())
        temp_input=temp_input[1:]


        lst_output.extend(yhat.tolist())
        i=i+1

    else:

        x_input = x_input.reshape((1, n_steps,1))
        yhat = model.predict(x_input, verbose=0)
        temp_input.extend(yhat[0].tolist())

        lst_output.extend(yhat.tolist())
        i=i+1

print("Output of predicted next days: ", len(lst_output))

"""plot predictio of 60 days"""

lstmdf=closedf.tolist()
lstmdf.extend((np.array(lst_output).reshape(-1,1)).tolist())
lstmdf=scaler.inverse_transform(lstmdf).reshape(1,-1).tolist()[0]

names = cycle(['Close price'])

fig = px.line(lstmdf,labels={'value': 'Stock price','index': 'Timestamp'})
fig.update_layout(title_text='Plotting whole closing stock price with prediction',
                  plot_bgcolor='white', font_size=15, font_color='black',legend_title_text='Stock')

fig.for_each_trace(lambda t:  t.update(name = next(names)))

fig.update_xaxes(showgrid=False)
fig.update_yaxes(showgrid=False)
fig.show()