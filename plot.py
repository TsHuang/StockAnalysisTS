import os, glob
import pandas as pd
import sqlite3
import numpy as np

# for candlestick plot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.finance import candlestick_ohlc
import datetime
import DateTime



if __name__ == "__main__":

    keys = ['Date', 'Days_Trade', 'Turnover_Value', 'Open', 'Day_High', 'Day_Low', 'Close', 'Price_Dif', 'Num_Deals']
    current_path = os.path.dirname(os.path.abspath(__file__)) + '/'
    data_folder = current_path + "data/"
    db_folder = current_path + "database/"
    csv_file = data_folder + '2454.csv'
    csv_file2 = data_folder + '2330.csv'
    db_file = db_folder + "stockPrice.db"
    df = pd.read_csv(csv_file, names=keys)
    df2 = pd.read_csv(csv_file2, names=keys)

    #
    con = sqlite3.connect(db_file)
    df.to_sql(name='2454', con=con, if_exists='replace')
    df2.to_sql(name='2330', con=con, if_exists='replace')
    con.close()

    # Read squlite query results into pandas DataFrame
    con = sqlite3.connect(db_file)
    # dfs1 = pd.read_sql_query("SELECT * from 2454 WHERE Date >='107/5/1'", con)
    # dfs1 = pd.read_sql_query("select * from '2454' ORDER BY 'index' DESC ", con=con)
    # dfs1 = pd.read_sql_query('select * from "2454" where "index" >= "4000" order by "index" ASC', con=con)
    dfs1 = pd.read_sql_query('select * from "2454" order by "index" DESC LIMIT "30"', con=con)

    close_values = dfs1.Close.to_string(index=False)
    print(close_values)

    # plt.scatter(dfs1['Date'], dfs1['Close'])
    # plt.show()

    ### candlestick plot
    # data arrangement
    # ohlc = []
    # x = 0
    # y = 10


    # ohlc = [] # should be something like [(1, 2, 3, 4), (1, 2, 3, 4), (1, 2, 3, 4)] where 1 refer to the date
    # a = 1, 2, 3, 4
    # b = 5, 6, 7, 8
    # ohlc.append(a)
    # ohlc.append(b)
    # print(ohlc)

    # print(dfs1.columns[1:]) # get the column names

    # if necessary convert to datetime
    # print(dfs1['Date'].values)
    for idx in range(len(dfs1)):
        ori_date_format = dfs1['Date'].values[idx]
        new_date_format = ori_date_format.replace(ori_date_format[0:3], str(int(ori_date_format[0:3]) + 1911))
        new_date_format = datetime.datetime.strptime(new_date_format, '%Y/%m/%d').strftime('%Y-%m-%d')
        dfs1['Date'].values[idx] = new_date_format

    print(dfs1)

    dfs1.Date = pd.to_datetime(dfs1.Date)
    dfs1.Open = dfs1.Open.astype(float)
    dfs1.Day_High = dfs1.Day_High.astype(float)
    dfs1.Day_Low = dfs1.Day_Low.astype(float)
    dfs1.Close = dfs1.Close.astype(float)
    dfs1.Num_Deals = dfs1.Num_Deals.astype(float)

    df_candleStickPlot = dfs1[['Date', 'Open', 'Day_High', 'Day_Low', 'Close', 'Num_Deals']]
    df_candleStickPlot["Date"] = df_candleStickPlot["Date"].apply(mdates.date2num)

    f1 = plt.subplot2grid((6, 4), (1, 0), rowspan=6, colspan=4, axisbg='#07000d')
    candlestick_ohlc(f1, df_candleStickPlot.values, width=.6, colorup='#ff1717', colordown='#53c156')
    f1.xaxis_date()
    f1.xaxis.set_major_formatter(mdates.DateFormatter('%y-%m-%d %H:%M:%S'))

    plt.xticks(rotation=45)
    plt.ylabel('Stock Price')
    plt.xlabel('Date Hours:Minutes')
    plt.show()

    #candlestick_ohlc(ax1, datas_candleStickPlot)



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
