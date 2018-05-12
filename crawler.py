import requests
from io import StringIO
import pandas as pd
import numpy as np
import csv
import sqlite3

import time
import os, re, time, string, logging, requests, argparse
from datetime import datetime, timedelta

from os import mkdir
from os.path import isdir

import matplotlib.pyplot as plt

'''todo:
modify the record function in crawler to save the data to database
'''

class Crawler():
    def __init__(self, prefix='data'):
        ''' Make directory if not exist when initialize '''
        if not isdir(prefix):
            mkdir(prefix)
        self.prefix = prefix

    def _clean_row(self, row):
        ''' Clean comma and spaces '''
        for index, content in enumerate(row):
            row[index] = re.sub(",", "", content.strip())
        return row

    def _record(self, stock_id, row):
        ''' Save row to csv file '''
        f = open('{}/{}.csv'.format(self.prefix, stock_id), 'a')
        cw = csv.writer(f, lineterminator='\n')
        # key = ['Date', 'Days_Trade', 'Turnover_Value', 'Open', 'Day_High', 'Day_Low', 'Close', 'Price_Dif', 'Num_Deals']
        # cw.writerow(key)
        cw.writerow(row)
        #print(row)
        f.close()

    def _get_tse_data(self, date_tuple):
        date_str = '{0}{1:02d}{2:02d}'.format(date_tuple[0], date_tuple[1], date_tuple[2])
        url = 'http://www.twse.com.tw/exchangeReport/MI_INDEX'

        query_params = {
            'date': date_str,
            'response': 'json',
            'type': 'ALL',
            '_': str(round(time.time() * 1000) - 500)
        }

        # Get json data
        page = requests.get(url, params=query_params)

        if not page.ok:
            logging.error("Can not get TSE data at {}".format(date_str))
            return

        content = page.json()

        # For compatible with original data
        date_str_mingguo = '{0}/{1:02d}/{2:02d}'.format(date_tuple[0] - 1911, date_tuple[1], date_tuple[2])

        for data in content['data5']:
            sign = '-' if data[9].find('green') > 0 else ''
            row = self._clean_row([
                date_str_mingguo,  # 日期
                data[2],  # 成交股數
                data[4],  # 成交金額
                data[5],  # 開盤價
                data[6],  # 最高價
                data[7],  # 最低價
                data[8],  # 收盤價
                sign + data[10],  # 漲跌價差
                data[3],  # 成交筆數
            ])

            self._record(data[0].strip(), row)

    def _get_otc_data(self, date_tuple):
        date_str = '{0}/{1:02d}/{2:02d}'.format(date_tuple[0] - 1911, date_tuple[1], date_tuple[2])
        ttime = str(int(time.time() * 100))
        url = 'http://www.tpex.org.tw/web/stock/aftertrading/daily_close_quotes/stk_quote_result.php?l=zh-tw&d={}&_={}'.format(
            date_str, ttime)
        page = requests.get(url)

        if not page.ok:
            logging.error("Can not get OTC data at {}".format(date_str))
            return

        result = page.json()

        if result['reportDate'] != date_str:
            logging.error("Get error date OTC data at {}".format(date_str))
            return

        for table in [result['mmData'], result['aaData']]:
            for tr in table:
                row = self._clean_row([
                    date_str,
                    tr[8],  # 成交股數
                    tr[9],  # 成交金額
                    tr[4],  # 開盤價
                    tr[5],  # 最高價
                    tr[6],  # 最低價
                    tr[2],  # 收盤價
                    tr[3],  # 漲跌價差
                    tr[10]  # 成交筆數
                ])
                self._record(tr[0], row)


    def get_data(self, date_tuple):
        print('Crawling {}'.format(date_tuple))
        self._get_tse_data(date_tuple)
        self._get_otc_data(date_tuple)

    def string_to_time(self, string):
        year, month, day = string.split('/')
        return datetime(int(year) + 1911, int(month), int(day))

    def is_same(self, row1, row2):
        if not len(row1) == len(row2):
            return False

        for index in range(len(row1)):
            if row1[index] != row2[index]:
                return False
        else:
            return True

    def post_process(self):
        folder = os.path.dirname(os.path.abspath(__file__)) + '//' + self.prefix
        print(folder)
        file_names = os.listdir()
        for file_name in file_names:
            if not file_name.endswith('.csv'):
                continue

            dict_rows = {}

            # Load and remove duplicates (use newer)
            with open('{}/{}'.format(folder, file_name), 'r') as file:
                for line in file.readlines():
                    dict_rows[line.split(',', 1)[0]] = line

            # Sort by date
            rows = [row for date, row in sorted(
                dict_rows.items(), key=lambda x: self.string_to_time(x[0]))]

            with open('{}/{}'.format(folder, file_name), 'w') as file:
                file.writelines(rows)



def main():
    # Set logging
    if not os.path.isdir('log'):
        os.makedirs('log')
    logging.basicConfig(filename='log/crawl-error.log',
        level=logging.ERROR,
        format='%(asctime)s\t[%(levelname)s]\t%(message)s',
        datefmt='%Y/%m/%d %H:%M:%S')

    # Get arguments
    parser = argparse.ArgumentParser(description='Crawl data at assigned day')
    parser.add_argument('day', type=int, nargs='*',
        help='assigned day (format: YYYY MM DD), default is today')
    parser.add_argument('-b', '--back', action='store_true',
        help='crawl back from assigned day until 2004/2/11')
    parser.add_argument('-c', '--check', action='store_true',
        help='crawl back 10 days for check data')

    args = parser.parse_args()

    # Day only accept 0 or 3 arguments
    if len(args.day) == 0:
        first_day = datetime.today()
    elif len(args.day) == 3:
        first_day = datetime(args.day[0], args.day[1], args.day[2])
    else:
        parser.error('Date should be assigned with (YYYY MM DD) or none')
        return

    crawler = Crawler()

    # If back flag is on, crawl till 2004/2/11, else crawl one day
    if args.back or args.check:
        # otc first day is 2007/04/20
        # tse first day is 2004/02/11

        last_day = datetime(2004, 2, 11) if args.back else first_day - timedelta(10)
        max_error = 5
        error_times = 0

        while error_times < max_error and first_day >= last_day:
            try:
                crawler.get_data((first_day.year, first_day.month, first_day.day))
                error_times = 0
            except:
                date_str = first_day.strftime('%Y/%m/%d')
                logging.error('Crawl raise error {}'.format(date_str))
                error_times += 1
                continue
            finally:
                first_day -= timedelta(1)
    else:
        crawler.get_data((first_day.year, first_day.month, first_day.day))

    crawler.post_process()

def crawl_price(date):
    r = requests.post(
        'http://www.twse.com.tw/exchangeReport/MI_INDEX?response=csv&date=' + str(date).split(' ')[0].replace('-',
                                                                                                              '') + '&type=ALL')
    ret = pd.read_csv(StringIO("\n".join([i.translate({ord(c): None for c in ' '})
                                          for i in r.text.split('\n')
                                          if len(i.split('",')) == 17 and i[0] != '='])), header=0)
    ret = ret.set_index('證券代號')
    ret['成交金額'] = ret['成交金額'].str.replace(',', '')
    ret['成交股數'] = ret['成交股數'].str.replace(',', '')
    return ret

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
    main()
    # crawler = Crawler()
    # first_day = datetime(2018, 5, 11)
    # crawler.get_data((first_day.year, first_day.month, first_day.day))
    # current_path = os.path.dirname(os.path.abspath(__file__))
    #print(current_path)

# databas Example
# current_path = os.path.dirname(os.path.abspath(__file__))
# db_name = current_path + 'StockDatabase.pb'
# xlsx_name = current_path + 'test.xlsx'
#
# #convert from Excel to sqlite
# xlsx_file = pd.ExcelFile(xlsx_name)
# dfs = pd.read_excel(xlsx_file, sheet_name = '0204', header=0, index_col=0)
#
# #xlsx_file to SQLite
# con = sqlite3.connect(db_name)
# dfs.to_sql(name = "Database", con=con, if_exists='replace')
# con.close()
#
# #Read squlite query results into pandas DataFrame
# con = sqlite3.connect(db_name)
# dfs1 = pd.read_sql_query("SELECT * from Database WHERE Zoom='4x' AND lux='100lux", con)
# print('Total items =' + str(len(dfs1)))
# for index, row in dfs1.iterrows():
#     tmp_file = row['Folder Path']
# con.close()

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
#df = financial_statement(2017, 2, '營益分析彙總表')
    #print(df)
# df = df.drop(['合計：共 880 家'], axis=1)  #drop unnecessary column
# df = df.set_index(['公司名稱']) #replace idx with company name
# print (df)
#df = df.astype(float) #set data type to float
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
# cond1 = df['毛利率(%)(營業毛利)/(營業收入)'].astype(float) > 20
# cond2 = df['營業利益率(%)(營業利益)/(營業收入)'].astype(float) > 5
# print(df[cond1 & cond2])

#main()
