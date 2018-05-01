from crawler import *
import datetime
import time
import matplotlib.pyplot as plt


def pick_company(df, companys):  # need to finish this later
    return df.loc[companys]

def pick_stock(df):
    cond1 = df['毛利率(%)(營業毛利)/(營業收入)'].astype(float) > 20
    cond2 = df['營業利益率(%)(營業利益)/(營業收入)'].astype(float) > 5
    return df[cond1 & cond2]


def nday_price(n_days):
    data = {}
    # n_days = 9
    date = datetime.datetime.now()
    fail_count = 0
    allow_continuous_fail_count = 5
    while len(data) < n_days:
        print('parsing', date)
        # 使用 crawPrice 爬資料
        try:
            # 抓資料
            data[date] = crawl_price(date)
            print('success!')
            fail_count = 0
        except:
            # 假日爬不到
            print('fail! check the date is holiday')
            fail_count += 1
            if fail_count == allow_continuous_fail_count:
                raise
                break

        # 減一天
        date -= datetime.timedelta(days=1)
        time.sleep(10)

    open = pd.DataFrame({k: d['開盤價'] for k, d in data.items()}).transpose()
    open.index = pd.to_datetime(open.index)

    close = pd.DataFrame({k: d['收盤價'] for k, d in data.items()}).transpose()
    close.index = pd.to_datetime(close.index)

    high = pd.DataFrame({k: d['最高價'] for k, d in data.items()}).transpose()
    high.index = pd.to_datetime(high.index)

    low = pd.DataFrame({k: d['最低價'] for k, d in data.items()}).transpose()
    low.index = pd.to_datetime(low.index)

    volume = pd.DataFrame({k: d['成交股數'] for k, d in data.items()}).transpose()
    volume.index = pd.to_datetime(volume.index)

    tsmc = {
        'close': close['2330']['2018'].dropna().astype(float),
        'open': open['2330']['2018'].dropna().astype(float),
        'high': high['2330']['2018'].dropna().astype(float),
        'low': low['2330']['2018'].dropna().astype(float),
        'volume': volume['2330']['2018'].dropna().astype(float),
    }

    return tsmc

if __name__ == "__main__":
    # pick stock example
    # df = financial_statement(2017, 2, '營益分析彙總表')
    # print(pick_stock(df))

    out = nday_price(5)
    out['close'].plot()

