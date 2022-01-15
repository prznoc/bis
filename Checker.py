import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import GRU
import matplotlib.pyplot as plt
import sys

look_back = 14


class Checker:

    def create_dataset(self, dataset, look_back=1):
        dataX, dataY = [], []
        for i in range(len(dataset) - look_back - 1):
            a = dataset[i:(i + look_back)].values
            dataX.append(a)
            dataY.append(dataset['f'].iloc[i + look_back])
        return np.array(dataX), np.array(dataY)

    def train_model(self, data):
        data['f'] = data['f'].astype('float32')
        train = data[0:look_back * 5].copy()
        trainX, trainY = self.create_dataset(train, look_back)
        trainX = np.reshape(trainX, (trainX.shape[0], look_back, 2))
        model = Sequential()
        model.add(GRU(64, input_shape=(trainX.shape[1], trainX.shape[2]),
                      return_sequences=True))
        model.add(GRU(32))
        model.add(Dense(1))
        model.compile(loss='mean_squared_error', optimizer='sgd')
        model.fit(trainX, trainY, epochs=100, batch_size=16, verbose=0)
        return model


    def predict_flow(self, _model, data):
        ypred = [0] * look_back
        # _max = np.max(data['f'])
        for k in range(len(data) - look_back):
            pattern = data[k:k + look_back].values
            x = np.reshape(pattern, (1, len(pattern), 2))
            ypred.append(_model.predict(x)[0][0])
        # ypred=[v*_max for v in ypred]
        return ypred


    def ApEn(self, U, m, r):
        def _maxdist(x_i, x_j):
            return max([abs(ua - va) for ua, va in zip(x_i, x_j)])

        def _phi(m):
            x = [[U[j] for j in range(i, i + m - 1 + 1)] for i in range(N - m + 1)]
            C = [len([1 for x_j in x if _maxdist(x_i, x_j) <= r]) / (N - m + 1.0) for x_i in x]
            return (N - m + 1.0) ** (-1) * sum(np.log(C))

        N = len(U)

        return abs(_phi(m + 1) - _phi(m))


    def entropy_trend(self, data, d):
        etrend = [self.ApEn(np.multiply(data[n:n + d].values, 1), 2, 3) for n in range(len(data) - d)]
        return etrend


    def check_file(self, filepath):
        try:
            df = pd.read_csv(filepath)

            df['date'] = pd.to_datetime(df['date'])
            df = df.groupby(['date', 'l_ipn'], as_index=False).sum()
            df['yday'] = df['date'].dt.dayofyear
            df['wday'] = df['date'].dt.dayofweek
        except Exception as e:
            return 'File does not comply with required format'

        frames = dict()
        maxes = dict()
        ips = df['l_ipn'].unique()
        for i in ips:
            frames[i] = (df[df['l_ipn'] == i])
            maxes[i] = np.max(frames[i]['f'])

        for i in ips:
            fv = [float(v) / float(maxes[i]) for v in frames[i]['f'].values]
            frames[i].loc[:, 'f'] = np.array(fv).reshape(-1, 1)

        models = dict()
        for i in frames.keys():
            models[i] = self.train_model(frames[i][['f', 'wday']].copy())

        ypred = dict()
        ipf = dict()

        size = len(frames.keys())
        if size < 2:
            f, axarray = plt.subplots(1, 1, figsize=(6, 8))
        else:
            f, axarray = plt.subplots(size // 2, 2, figsize=(size // 2 * 3, size // 2 * 4))
        j = 0
        for i in frames.keys():
            ypred0 = np.multiply(self.predict_flow(models[i], frames[i][['f', 'wday']].copy()), maxes[i])
            ip0f = np.multiply(frames[i]['f'], maxes[i])
            ypred[i] = (ypred0)
            ipf[i] = (ip0f)

            if size < 2:
                axarray.plot(frames[i]['yday'], ip0f)
                axarray.plot(frames[i]['yday'], ypred0, color='r')
                axarray.set_title("Local IP " + str(i) + " Flow and prediction")
            else:
                axarray[j // 2, j % 2].plot(frames[i]['yday'], ip0f)
                axarray[j // 2, j % 2].plot(frames[i]['yday'], ypred0, color='r')
                axarray[j // 2, j % 2].set_title("Local IP " + str(i) + " Flow and prediction")
            j += 1

        f.savefig('output/plot1.png')

        corrs = dict()

        for i in frames.keys():
            corr0 = pd.Series(ipf[i]).corr(pd.Series(ypred[i]))
            corrs[i] = (corr0)

        frames = dict()
        ips = df['l_ipn'].unique()
        for i in ips:
            frames[i] = (df[df['l_ipn'] == i])

        m = 2
        r = 3
        ent = dict()
        for ip in frames.keys():
            ent[ip] = (self.ApEn(np.multiply(frames[ip]['f'].values, 1), m, r))

        size = len(frames.keys())
        if size < 2:
            f, axarray = plt.subplots(1, 1, figsize=(6, 8))
        else:
            f, axarray = plt.subplots(size // 2, 2, figsize=(size // 2 * 3, size // 2 * 4))
        j = 0

        for i in frames.keys():
            days = len(frames[i]['f'])//10 * 10
            et0 = self.entropy_trend(frames[i]['f'], days)
            if size < 2:
                axarray.plot(range(len(et0)), et0)
                axarray.set_title("Local IP " + str(i) + " ApEn Variation")
            else:
                axarray[j // 2, j % 2].plot(range(len(et0)), et0)
                axarray[j // 2, j % 2].set_title("Local IP " + str(ips[i]) + " ApEn Variation")
            j += 1

        f.savefig('output/plot2.png')

        print(ent)
        return ent


if __name__ == '__main__':
    checker = Checker()
    checker.check_file(sys.argv[1])
