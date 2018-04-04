from crawler import *

def pick_company(df, companys):
    return df.loc[companys]

def pick_stock(df):
    cond1 = df['毛利率(%)(營業毛利)/(營業收入)'].astype(float) > 20
    cond2 = df['營業利益率(%)(營業利益)/(營業收入)'].astype(float) > 5
    return df[cond1 & cond2]


if __name__ == "__main__":
    df = financial_statement(2017, 2, '營益分析彙總表')
    print(pick_stock(df))