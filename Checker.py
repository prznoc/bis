import numpy as np
import pandas as pd
import math
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.layers import GRU
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error
import matplotlib.pyplot as plt

look_back = 14

def create_dataset(dataset, look_back=1):
    dataX, dataY = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back)].values
        dataX.append(a)
        dataY.append(dataset['f'].iloc[i + look_back])
    return np.array(dataX), np.array(dataY)

def trainModel(data):
    data['f'] = data['f'].astype('float32')
    train = data[0:look_back*5].copy()
    trainX, trainY = create_dataset(train, look_back)
    trainX = np.reshape(trainX, (trainX.shape[0], look_back, 2))
    model = Sequential()
    model.add(GRU(64,input_shape=(trainX.shape[1], trainX.shape[2]),
               return_sequences=True))
    model.add(GRU(32))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='sgd')
    model.fit(trainX, trainY, epochs=100, batch_size=16, verbose=0)
    return model

def predictFlow(_model,data):
    ypred=[0]*look_back
    #_max = np.max(data['f'])
    for k in range(len(data)-look_back):
        pattern = data[k:k+look_back].values
        x = np.reshape(pattern, (1, len(pattern), 2))
        ypred.append(_model.predict(x)[0][0])
    #ypred=[v*_max for v in ypred]
    return ypred

def ApEn(U, m, r):

    def _maxdist(x_i, x_j):
        return max([abs(ua - va) for ua, va in zip(x_i, x_j)])

    def _phi(m):
        x = [[U[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
        C = [len([1 for x_j in x if _maxdist(x_i, x_j) <= r]) / (N - m + 1.0) for x_i in x]
        return (N - m + 1.0)**(-1) * sum(np.log(C))

    N = len(U)

    return abs(_phi(m + 1) - _phi(m))

def entropyTrend(data,d):
    etrend = [ApEn(np.multiply(data[n:n+d].values,1),2,3) for n in range(len(data)-d)]
    return etrend

def checkFile(filepath):
    df = pd.read_csv(filepath)

    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby(['date', 'l_ipn'], as_index=False).sum()
    df['yday'] = df['date'].dt.dayofyear
    df['wday'] = df['date'].dt.dayofweek

    df.head(2)

    frames = []
    maxes = []
    ips = df['l_ipn'].unique()
    print(ips)
    for i in ips:
        frames.append(df[df['l_ipn'] == i])
        maxes.append(np.max(frames[i]['f']))

    for i in range(len(ips)):
        fv = [float(v) / float(maxes[i]) for v in frames[i]['f'].values]
        frames[i].loc[:, 'f'] = np.array(fv).reshape(-1, 1)

    models = []
    for i in frames:
        models.append(trainModel(i[['f', 'wday']].copy()))

    ypred = []
    ipf = []

    f, axarray = plt.subplots(5, 2, figsize=(15, 20))
    for i in range(len(models)):
        ypred0 = np.multiply(predictFlow(models[i], frames[i][['f', 'wday']].copy()), maxes[i])
        ip0f = np.multiply(frames[i]['f'], maxes[i])
        ypred.append(ypred0)
        ipf.append(ip0f)

        axarray[i // 2, i % 2].plot(frames[i]['yday'], ip0f)
        axarray[i // 2, i % 2].plot(frames[i]['yday'], ypred0, color='r')
        axarray[i // 2, i % 2].set_title("Local IP " + str(i) + " Flow and prediction")

    corrs = []
    for i in range(len(ipf)):
        corr0 = pd.Series(ipf[i]).corr(pd.Series(ypred[i]))
        corrs.append(corr0)

    frames = []
    ips = df['l_ipn'].unique()
    for i in ips:
        frames.append(df[df['l_ipn'] == i])

    m = 2
    r = 3
    ent = []
    for ip in frames:
        ent.append(ApEn(np.multiply(ip['f'].values, 1), m, r))

    columns = []
    for i in range(len(corrs)):
        columns.append('e' + str(i))
    rows = ['0']
    entropy = pd.DataFrame(data=[ent], index=rows, columns=columns)

    f, axarray = plt.subplots(5, 2, figsize=(15, 20))
    days = 60

    for i in range(len(frames)):
        et0 = entropyTrend(frames[i]['f'], days)
        axarray[i // 2, i % 2].plot(range(len(et0)), et0)
        axarray[i // 2, i % 2].set_title("Local IP " + str(ips[i]) + " ApEn Variation")
    print(entropy)


checkFile("archive/cs448b_ipasn.csv")
