import os, glob
import pandas as pd
import sqlite3
import numpy as np

# for candlestick plot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
# from matplotlib.finance import candlestick_ohlc #will be deprecated
from mpl_finance import candlestick_ohlc
import datetime
import DateTime


def candleStickPlot(dfs1, MAs):
    df_candleStickPlot = dfs1[['Date', 'Open', 'Day_High', 'Day_Low', 'Close', 'Num_Deals']]
    df_candleStickPlot['Date'] = df_candleStickPlot['Date'].apply(mdates.date2num)

    f1 = plt.subplot2grid((6, 4), (0, 0), rowspan=5, colspan=4, axisbg='#07000d')

    # plot candlestick
    candlestick_ohlc(f1, df_candleStickPlot.values, width=.6, colorup='#ff1717', colordown='#53c156')
    # ohlc = [] # should be something like [(1, 2, 3, 4, 5), (1, 2, 3, 4, 5), (1, 2, 3, 4, 5)] where 1, 2, 3, 4 refer to the date, open, high, low, close, volumn

    # plot MA
    for MA_value in MAs:
        ma_key = 'MA' + str(MA_value)
        f1.plot(dfs1['Date'], dfs1[ma_key])  # plot MA


    # f1.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d %H:%M:%S'))
    # f1.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))
    f1.set_title('2454')
    f1.axes.get_xaxis().set_visible(False)
    f1.set_ylabel('Price')

    # plot volumn
    f2 = plt.subplot2grid((6, 4), (5, 0), rowspan=6, colspan=4, axisbg='#07000d')
    f2.bar(dfs1['Date'], dfs1['Num_Deals'])
    f2.set_ylabel('Volume')
    # f2.xaxis_date()
    # f2.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d'))
    plt.xticks(rotation=45)
    #plt.sca(axes[1, 0])

    plt.show()


def getDataByStockIdx(stockIdx, MAs, days=30):
    keys = ['Date', 'Days_Trade', 'Turnover_Value', 'Open', 'Day_High', 'Day_Low', 'Close', 'Price_Dif', 'Num_Deals']
    current_path = os.path.dirname(os.path.abspath(__file__)) + '/'
    data_folder = current_path + "data/"
    csv_file = data_folder + str(stockIdx) + '.csv'
    df = pd.read_csv(csv_file, names=keys)

    # Read squlite query results into pandas DataFrame
    # con = sqlite3.connect(db_file)
    # dfs1 = pd.read_sql_query('select * from "2454" order by "index" DESC LIMIT "30"', con=con)

    MA_max = max(MAs)

    df = df.tail(int(days) + int(MA_max) - 1)

    # preprocessing
    for idx in range(len(df)):
        ori_date_format = df['Date'].values[idx]
        new_date_format = ori_date_format.replace(ori_date_format[0:3], str(int(ori_date_format[0:3]) + 1911))
        new_date_format = datetime.datetime.strptime(new_date_format, '%Y/%m/%d').strftime('%Y-%m-%d')
        df['Date'].values[idx] = new_date_format

    df.Date = pd.to_datetime(df.Date)
    df.Open = df.Open.astype(float)
    df.Day_High = df.Day_High.astype(float)
    df.Day_Low = df.Day_Low.astype(float)
    df.Close = df.Close.astype(float)
    df.Num_Deals = df.Num_Deals.astype(float)

    # df_candleStickPlot = df_candleStickPlot.iloc[::-1] #revert the data

    # generate MA values
    for MA_value in MAs:
        new_key = 'MA' + str(MA_value)
        df[new_key] = df['Close'].rolling(int(MA_value)).mean()

    return df.tail(days)


if __name__ == "__main__":
    MAs = [5, 10, 20]  # Moving average of 5, 10, 20 days
    dfs1 = getDataByStockIdx(stockIdx=2330, MAs=MAs, days=60)
    candleStickPlot(dfs1=dfs1, MAs=MAs)


    # print(dfs1.columns[1:]) # get the column names

    # print(dfs1['Date'].values)




# #plotly example (related to html, check it later)
# plotly.tools.set_credentials_file(username='tshuang1983', api_key='SLFEuRSvKP6v7sQkB69B')
# df = web.DataReader("aapl", 'morningstar').reset_index()
#
# trace = go.Candlestick(x=df.Date,
#                        open=df.Open,
#                        high=df.High,
#                        low=df.Low,
#                        close=df.Close)
# data = [trace]
# print(data)
# py.plot(data, filename='simple_candlestick')
