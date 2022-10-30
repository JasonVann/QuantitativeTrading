import numpy as np
import pandas as pd
from jqdata import finance


def get_data(code=None, is_mutual_fund=False, to_save=False):
    import pandas as pd

    if code is None:
        code = '510300.XSHG'

    if is_mutual_fund:
        from jqdata import finance
        q = query(finance.FUND_NET_VALUE).filter(finance.FUND_NET_VALUE.code == code)
        df = finance.run_query(q)
        price_column_name = 'net_value'

        df['dt'] = pd.to_datetime(df['day'])
        df['day_of_week'] = df.dt.dt.dayofweek + 1
        df['day_of_month'] = df.dt.dt.day
        df['week_of_year'] = df.dt.dt.weekofyear
        df['day_of_year'] = df.dt.dt.dayofyear
        df['month'] = df.dt.dt.month
    else:
        # 获取股票510300.XSHG2015年1月的日级交易数据
        df = get_price(code, start_date='2010-01-01', end_date='2021-10-21', frequency='daily')
        # df = get_price(code, start_date='2021-09-01', end_date='2021-10-20', frequency='daily')
        price_column_name = 'close'

        df['dt'] = df.index
        df['day_of_week'] = df.index.dayofweek + 1
        df['day_of_month'] = df.index.day
        df['week_of_year'] = df.index.weekofyear
        df['day_of_year'] = df.index.dayofyear
        df['month'] = df.index.month

    df_end_of_year = annual_return(df, is_mutual_fund)
    plot_df(df_end_of_year, is_mutual_fund)
    return df, df_end_of_year


def annual_return(df, is_mutual_fund=False):
    df_end_of_year = df.loc[df['week_of_year'] == 52][df['day_of_week'] == 5]

    if is_mutual_fund:
        df_end_of_year['YoY'] = df_end_of_year['refactor_net_value'].pct_change()
    else:
        df_end_of_year['YoY'] = df_end_of_year['close'].pct_change()
    return df_end_of_year


def plot_df(df, is_mutal_fund=False):
    plt.figure(figsize=[18, 5])
    # df_end_of_year['net_value'].plot(label='net_value')

    if is_mutal_fund:
        df.plot(x='dt', y='refactor_net_value')
    else:
        df.plot(x='dt', y='close')

    df.plot(x='dt', y='YoY')
    plt.show()


def test_wine():
    df, df_end_of_year = get_data(code='161725', is_mutual_fund=True)
    print('Next is moutai')
    df, df_end_of_year = get_data(code='600519.XSHG', is_mutual_fund=False)


test_wine()

