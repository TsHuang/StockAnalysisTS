import requests
from io import StringIO
import pandas as pd
import numpy as np
import time
#import matplotlib.pyplot as plt


def daily_report(datestr):
    r = requests.post('http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + datestr + '&type=ALL')
    df = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '})
        for i in r.text.split('\n')
            if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    return df

def monthly_report(year, month):
    # 假如是西元，轉成民國
    if year > 1990:
        year -= 1911

    url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_' + str(year) + '_' + str(month) + '_0.html'
    if year <= 98:
        url = 'http://mops.twse.com.tw/nas/t21/sii/t21sc03_' + str(year) + '_' + str(month) + '.html'

    # 偽瀏覽器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # 下載該年月的網站，並用pandas轉換成 dataframe
    r = requests.get(url, headers)
    r.encoding = 'big5'
    html_df = pd.read_html(StringIO(r.text))

    # 處理一下資料
    if html_df[0].shape[0] > 500:
        df = html_df[0].copy()
    else:
        df = pd.concat([df for df in html_df if df.shape[1] <= 11])
    df = df[list(range(0, 10))]
    column_index = df.index[(df[0] == '公司代號')][0]
    df.columns = df.iloc[column_index]
    df['當月營收'] = pd.to_numeric(df['當月營收'], 'coerce')
    df = df[~df['當月營收'].isnull()]
    df = df[df['公司代號'] != '合計']

    # 偽停頓
    time.sleep(5)
    return df


def financial_statement(year, season, type='綜合損益彙總表'):
    if year >= 1000:
        year -= 1911

    if type == '綜合損益彙總表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb04'
    elif type == '資產負債彙總表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb05'
    elif type == '營益分析彙總表':
        url = 'http://mops.twse.com.tw/mops/web/ajax_t163sb06'
    else:
        print('type does not match')
    r = requests.post(url, {
        'encodeURIComponent': 1,
        'step': 1,
        'firstin': 1,
        'off': 1,
        'TYPEK': 'sii',
        'year': str(year),
        'season': str(season),
    })

    r.encoding = 'utf8'
    dfs = pd.read_html(r.text)

    for i, df in enumerate(dfs):
        df.columns = df.iloc[0]
        dfs[i] = df.iloc[1:]

    df = pd.concat(dfs).applymap(lambda x: x if x != '--' else np.nan)
    df = df[df['公司代號'] != '公司代號']
    df = df[~df['公司代號'].isnull()]
    return df


if __name__ == "__main__":
# select stocks (本益比) Example
    #datestr = '20180131'
    #df = daily_report(datestr)
    #aa = df[pd.to_numeric(df['本益比'], errors='coerce') < 15]
# 任意年月份報表 Example
    #df = monthly_report(2018,2)
    #print(df)
# 季報表 Example
    #df = financial_statement(2017,1,'營益分析彙總表')
    #print(df)
# pick stock Example
    df = financial_statement(2017, 2, '營益分析彙總表')
    #print(df)
    df = df.drop(['合計：共 880 家'], axis=1)  #drop unnecessary column
    df = df.set_index(['公司名稱']) #replace idx with company name
    print (df)
    df = df.astype(float) #set data type to float
    #df = df.drop(['合計：共 880 家'], axis=1).set_index(['公司名稱']).astype(float) #put the above command in one line
    #取得毛利率
    #print(df['毛利率(%)(營業毛利)/(營業收入)'])
    #取得特定公司
    #print(df.loc[['台積電', '聯發科']])
    #每一欄位的數值分析
    #print(df.describe())
    #畫圖
    #％matplotlib inline
    #df['毛利率(%)(營業毛利)/(營業收入)'].astype(float).hist(bins=range(-100,100))
    #plt.plot((df['毛利率(%)(營業毛利)/(營業收入)'].astype(float).hist(bins=range(-100,100))))
    #plt.show()
    cond1 = df['毛利率(%)(營業毛利)/(營業收入)'].astype(float) > 20
    cond2 = df['營業利益率(%)(營業利益)/(營業收入)'].astype(float) > 5
    print(df[cond1 & cond2])






