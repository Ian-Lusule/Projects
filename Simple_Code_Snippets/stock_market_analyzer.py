import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import talib

class StockAnalyzer:
    def __init__(self, ticker, start_date, end_date):
        self.ticker = ticker
        self.start_date = start_date
        self.end_date = end_date
        self.data = self.fetch_data()

    def fetch_data(self):
        try:
            data = yf.download(self.ticker, start=self.start_date, end=self.end_date)
            return data
        except Exception as e:
            print(f"Error fetching data for {self.ticker}: {e}")
            return None

    def clean_data(self):
        if self.data is not None:
            self.data.dropna(inplace=True)
            self.data.columns = [col.lower() for col in self.data.columns]
            return self.data
        else:
            return None

    def calculate_moving_averages(self, periods=[20, 50, 200]):
        if self.data is not None:
            for period in periods:
                self.data[f'ma_{period}'] = self.data['close'].rolling(window=period).mean()
            return self.data
        else:
            return None

    def calculate_rsi(self, period=14):
        if self.data is not None:
            self.data['rsi'] = talib.RSI(self.data['close'], timeperiod=period)
            return self.data
        else:
            return None

    def calculate_macd(self, fastperiod=12, slowperiod=26, signalperiod=9):
        if self.data is not None:
            macd, macdsignal, macdhist = talib.MACD(self.data['close'], fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
            self.data['macd'] = macd
            self.data['macdsignal'] = macdsignal
            self.data['macdhist'] = macdhist
            return self.data
        else:
            return None

    def calculate_bollinger_bands(self, period=20, num_std=2):
         if self.data is not None:
            self.data['sma'] = self.data['close'].rolling(window=period).mean()
            self.data['std'] = self.data['close'].rolling(window=period).std()
            self.data['upper_band'] = self.data['sma'] + (self.data['std'] * num_std)
            self.data['lower_band'] = self.data['sma'] - (self.data['std'] * num_std)
            return self.data
         else:
            return None


    def perform_correlation_analysis(self):
        if self.data is not None:
            correlation_matrix = self.data.corr()
            return correlation_matrix
        else:
            return None

    def perform_linear_regression(self, x_col='volume', y_col='close'):
        if self.data is not None:
            X = self.data[[x_col]]
            y = self.data[y_col]
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            model = LinearRegression()
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            return model, mse, X_test, y_test, y_pred
        else:
            return None, None, None, None, None

    def plot_candlestick_chart(self):
        if self.data is not None:
            fig = go.Figure(data=[go.Candlestick(x=self.data.index,
                                                 open=self.data['open'],
                                                 high=self.data['high'],
                                                 low=self.data['low'],
                                                 close=self.data['close'])])
            fig.update_layout(title=f'{self.ticker} Candlestick Chart',
                              xaxis_title='Date',
                              yaxis_title='Price')
            fig.show()
        else:
            print("No data to plot.")

    def plot_volume_chart(self):
        if self.data is not None:
            fig = go.Figure(data=[go.Bar(x=self.data.index, y=self.data['volume'])])
            fig.update_layout(title=f'{self.ticker} Volume Chart',
                              xaxis_title='Date',
                              yaxis_title='Volume')
            fig.show()
        else:
            print("No data to plot.")

    def plot_moving_averages(self, periods=[20, 50, 200]):
        if self.data is not None:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data['close'], mode='lines', name='Close Price'))
            for period in periods:
                if f'ma_{period}' in self.data.columns:
                    fig.add_trace(go.Scatter(x=self.data.index, y=self.data[f'ma_{period}'], mode='lines', name=f'MA {period}'))
            fig.update_layout(title=f'{self.ticker} Moving Averages', xaxis_title='Date', yaxis_title='Price')
            fig.show()
        else:
            print("No data to plot.")

    def plot_rsi(self):
        if self.data is not None and 'rsi' in self.data.columns:
             fig = go.Figure(data=[go.Scatter(x=self.data.index, y=self.data['rsi'], mode='lines', name='RSI')])
             fig.update_layout(title=f'{self.ticker} RSI', xaxis_title='Date', yaxis_title='RSI Value', yaxis_range=[0, 100])
             fig.add_hline(y=30, line_dash="dash", annotation_text="Oversold", annotation_position="bottom right")
             fig.add_hline(y=70, line_dash="dash", annotation_text="Overbought", annotation_position="top right")
             fig.show()
        else:
            print("RSI data not available or no data to plot.")

    def plot_macd(self):
        if self.data is not None and 'macd' in self.data.columns and 'macdsignal' in self.data.columns:
            fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.1, subplot_titles=('MACD', 'MACD Histogram'))
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data['macd'], mode='lines', name='MACD'), row=1, col=1)
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data['macdsignal'], mode='lines', name='Signal Line'), row=1, col=1)
            fig.add_trace(go.Bar(x=self.data.index, y=self.data['macdhist'], name='MACD Histogram'), row=2, col=1)
            fig.update_layout(title=f'{self.ticker} MACD', xaxis_title='Date')
            fig.show()
        else:
            print("MACD data not available or no data to plot.")

    def plot_bollinger_bands(self):
        if self.data is not None and 'upper_band' in self.data.columns and 'lower_band' in self.data.columns:
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data['close'], mode='lines', name='Close Price'))
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data['upper_band'], mode='lines', name='Upper Band'))
            fig.add_trace(go.Scatter(x=self.data.index, y=self.data['lower_band'], mode='lines', name='Lower Band'))
            fig.update_layout(title=f'{self.ticker} Bollinger Bands', xaxis_title='Date', yaxis_title='Price')
            fig.show()
        else:
            print("Bollinger Bands data not available or no data to plot.")

    def simple_moving_average_strategy(self, short_window=20, long_window=50):
        if self.data is not None:
            self.data['short_ma'] = self.data['close'].rolling(window=short_window).mean()
            self.data['long_ma'] = self.data['close'].rolling(window=long_window).mean()
            self.data['signal'] = 0.0
            self.data['signal'][short_window:] = np.where(self.data['short_ma'][short_window:] > self.data['long_ma'][short_window:], 1.0, 0.0)
            self.data['positions'] = self.data['signal'].diff()

            initial_capital = 10000
            positions = pd.DataFrame(index=self.data.index).fillna(0.0)
            positions['stock'] = 100*self.data['signal']

            portfolio = positions.multiply(self.data['close'], axis=0)
            pos_diff = positions.diff()

            portfolio['holdings'] = (positions.multiply(self.data['close'], axis=0)).sum(axis=1)
            portfolio['cash'] = initial_capital - (pos_diff.multiply(self.data['close'], axis=0)).sum(axis=1).cumsum()
            portfolio['total'] = portfolio['cash'] + portfolio['holdings']
            portfolio['returns'] = portfolio['total'].pct_change()

            sharpe_ratio = np.sqrt(252) * (portfolio['returns'].mean() / portfolio['returns'].std())
            return portfolio, sharpe_ratio
        else:
            return None, None

    def lstm_prediction(self, look_back=60, test_size=0.2):
        if self.data is not None:
            data = self.data['close'].values.reshape(-1, 1)
            scaler = MinMaxScaler(feature_range=(0, 1))
            data_scaled = scaler.fit_transform(data)

            train_size = int(len(data_scaled) * (1 - test_size))
            test_size = len(data_scaled) - train_size
            train, test = data_scaled[0:train_size,:], data_scaled[train_size:len(data_scaled),:]

            def create_dataset(dataset, look_back=1):
                X, Y = [], []
                for i in range(len(dataset)-look_back-1):
                    a = dataset[i:(i+look_back), 0]
                    X.append(a)
                    Y.append(dataset[i + look_back, 0])
                return np.array(X), np.array(Y)

            X_train, y_train = create_dataset(train, look_back)
            X_test, y_test = create_dataset(test, look_back)

            X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))
            X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

            model = Sequential()
            model.add(LSTM(50, return_sequences=True, input_shape=(look_back, 1)))
            model.add(LSTM(50))
            model.add(Dense(1))
            model.compile(loss='mean_squared_error', optimizer='adam')
            model.fit(X_train, y_train, epochs=2, batch_size=32, verbose=0)

            train_predict = model.predict(X_train)
            test_predict = model.predict(X_test)

            train_predict = scaler.inverse_transform(train_predict)
            y_train = scaler.inverse_transform([y_train])
            test_predict = scaler.inverse_transform(test_predict)
            y_test = scaler.inverse_transform([y_test])

            train_rmse = np.sqrt(mean_squared_error(y_train[0], train_predict[:,0]))
            test_rmse = np.sqrt(mean_squared_error(y_test[0], test_predict[:,0]))

            return model, scaler, X_test, test_predict, test_rmse
        else:
            return None, None, None, None, None

if __name__ == '__main__':
    ticker = 'AAPL'
    start_date = '2020-01-01'
    end_date = '2024-01-01'

    analyzer = StockAnalyzer(ticker, start_date, end_date)

    if analyzer.data is not None:
        cleaned_data = analyzer.clean_data()
        if cleaned_data is not None:
            analyzer.calculate_moving_averages()
            analyzer.calculate_rsi()
            analyzer.calculate_macd()
            analyzer.calculate_bollinger_bands()

            # Visualizations
            analyzer.plot_candlestick_chart()
            analyzer.plot_volume_chart()
            analyzer.plot_moving_averages()
            analyzer.plot_rsi()
            analyzer.plot_macd()
            analyzer.plot_bollinger_bands()

            # Correlation Analysis
            correlation_matrix = analyzer.perform_correlation_analysis()
            if correlation_matrix is not None:
                print("Correlation Matrix:")
                print(correlation_matrix)

            # Linear Regression
            model, mse, X_test, y_test, y_pred = analyzer.perform_linear_regression()
            if model is not None:
                print(f"Linear Regression MSE: {mse}")
                # Plotting Linear Regression
                plt.figure(figsize=(10, 6))
                plt.scatter(X_test, y_test, color='blue', label='Actual')
                plt.plot(X_test, y_pred, color='red', label='Predicted')
                plt.xlabel('Volume')
                plt.ylabel('Close Price')
                plt.title('Linear Regression: Volume vs. Close Price')
                plt.legend()
                plt.show()

            # Backtesting SMA Strategy
            portfolio, sharpe_ratio = analyzer.simple_moving_average_strategy()
            if portfolio is not None:
                print(f"Sharpe Ratio: {sharpe_ratio}")
                plt.figure(figsize=(12, 6))
                plt.plot(portfolio['total'], label='Portfolio Value')
                plt.xlabel('Date')
                plt.ylabel('Value')
                plt.title('SMA Backtesting - Portfolio Value')
                plt.legend()
                plt.show()

            # LSTM Prediction
            lstm_model, scaler, X_test_lstm, test_predict, test_rmse = analyzer.lstm_prediction()
            if lstm_model is not None:
                print(f"LSTM Test RMSE: {test_rmse}")

                # Plotting LSTM predictions
                # Shift train predictions for plotting
                trainPredictPlot = np.empty_like(analyzer.data['close'].values.reshape(-1,1))
                trainPredictPlot[:, :] = np.nan
                trainPredictPlot[60:len(lstm_model.predict(np.reshape(analyzer.data['close'].values[0:int(len(analyzer.data)*0.8)],(int(len(analyzer.data)*0.8),1,1))))+60, :] = lstm_model.predict(np.reshape(analyzer.data['close'].values[0:int(len(analyzer.data)*0.8)],(int(len(analyzer.data)*0.8),1,1)))

                # Shift test predictions for plotting
                testPredictPlot = np.empty_like(analyzer.data['close'].values.reshape(-1,1))
                testPredictPlot[:, :] = np.nan
                testPredictPlot[len(analyzer.data['close'].values[0:int(len(analyzer.data)*0.8)])+61:len(analyzer.data)-1, :] = test_predict

                # Plot baseline and predictions
                plt.figure(figsize=(12,6))
                plt.plot(scaler.inverse_transform(analyzer.data['close'].values.reshape(-1,1)), label='Original Data')
                plt.plot(trainPredictPlot, label='Train Predictions')
                plt.plot(testPredictPlot, label='Test Predictions')
                plt.xlabel('Time')
                plt.ylabel('Stock Price')
                plt.title('LSTM Stock Price Prediction')
                plt.legend()
                plt.show()
        else:
            print("Data cleaning failed.")
    else:
        print("Failed to fetch data.")