import matplotlib.pyplot as plt
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas_datareader as web
from datetime import datetime


if __name__ == "__main__":
    plotly.tools.set_credentials_file(username='tshuang1983', api_key='SLFEuRSvKP6v7sQkB69B')
    df = web.DataReader("aapl", 'morningstar').reset_index()

    trace = go.Candlestick(x=df.Date,
                           open=df.Open,
                           high=df.High,
                           low=df.Low,
                           close=df.Close)
    data = [trace]
    print(data)
    py.plot(data, filename='simple_candlestick')
    # print(plotly.__version__)
    # plt.plot([1, 2, 3, 4])
    # plt.ylabel('some numbers')
    # plt.show()
