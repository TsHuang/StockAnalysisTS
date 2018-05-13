import os, glob
import pandas as pd
import sqlite3
import numpy as np

import matplotlib.pyplot as plt
import plotly
import plotly.plotly as py
import plotly.graph_objs as go

import pandas_datareader as web
from datetime import datetime


if __name__ == "__main__":
    # # read from csv and plot
    # current_path = os.path.dirname(os.path.abspath(__file__)) + '/'
    # data_folder = current_path + "data/"
    # db_folder = current_path + "database/"
    # keys = ['Date', 'Days_Trade', 'Turnover_Value', 'Open', 'Day_High', 'Day_Low', 'Close', 'Price_Dif', 'Num_Deals']
    # idx_col = ['Date']
    #
    # db_file = db_folder + "stockPrice.db"
    # con = sqlite3.connect(db_file)
    # for filename in os.listdir(os.path.join(data_folder)):
    #     if os.path.splitext(filename)[1] != '.csv':
    #         print('csv to sql: ignore file:' + filename)
    #         continue
    #     csv_file = data_folder + filename
    #
    #     df = pd.read_csv(csv_file, names=keys)
    #     df.to_sql(name= filename[:-4], con=con, if_exists='replace')
    #     #print(csv_file)
    #     #print('csv to sql:' + filename[:-4])
    #
    # con.close()


    csv_file = data_folder + '2454.csv'
    csv_file2 = data_folder + '2330.csv'
    db_file = db_folder + "stockPrice.db"
    df = pd.read_csv(csv_file, names=keys)
    df2 = pd.read_csv(csv_file2, names=keys)

    con = sqlite3.connect(db_file)
    df.to_sql(name='2454', con=con, if_exists='replace')
    df2.to_sql(name='2330', con=con, if_exists='replace')
    con.close()

    # Read squlite query results into pandas DataFrame
    con = sqlite3.connect(db_file)
    # dfs1 = pd.read_sql_query("SELECT * from 2454 WHERE Date >='107/5/1'", con)
    # dfs1 = pd.read_sql_query("select * from '2454' ORDER BY 'index' DESC ", con=con)
    # dfs1 = pd.read_sql_query('select * from "2454" where "index" >= "4000" order by "index" ASC', con=con)
    dfs1 = pd.read_sql_query('select * from "2454" order by "index" DESC LIMIT "10"', con=con)

    # for index, row in dfs1.iterrows():
    #     tmp_file = row['Folder Path']
    con.close()
    print(dfs1)
    print('Total items =' + str(len(dfs1)))

    # plt.plot([1, 2, 3, 4])
    # plt.ylabel('some numbers')
    # plt.show()


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
